from sqlalchemy import Column, Integer, String, Text, Numeric, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class FeeStructure(Base, TimestampMixin):
    """Institutional fee item definition (e.g. Tuition, Exam, Transport)."""
    __tablename__ = "fee_structures"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)  # e.g., "Monthly Tuition Fee"
    academic_year = Column(String(50), nullable=False, index=True)  # e.g., "2026/2027"
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="SET NULL"), nullable=True, index=True)  # Null applies to all
    amount = Column(Numeric(10, 2), nullable=False)
    frequency = Column(String(50), default="Term", nullable=False)  # "Monthly", "Term", "Semester", "Annual", "One-Time"
    due_date = Column(Date, nullable=False)
    description = Column(Text, nullable=True)
    education_level = Column(String(20), nullable=True, index=True)  # "PRIMARY", "SECONDARY", or Null (School-wide)
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    status = Column(String(20), default="ACTIVE", nullable=False)  # "ACTIVE", "INACTIVE", "ARCHIVED"

    # Relationships
    school_class = relationship("SchoolClass", back_populates="fee_structures", lazy="selectin")
    created_by = relationship("User", foreign_keys=[created_by_id], lazy="selectin")
    student_fees = relationship("StudentFee", back_populates="fee_structure")

    def __repr__(self) -> str:
        return f"<FeeStructure(id={self.id}, name='{self.name}', amount={self.amount}, freq='{self.frequency}')>"


class StudentFee(Base, TimestampMixin):
    """Individual student fee invoice with unique serial number and live balance tracking."""
    __tablename__ = "student_fees"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)  # e.g., "INV-2026-000001"
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="SET NULL"), nullable=True, index=True)
    fee_structure_id = Column(Integer, ForeignKey("fee_structures.id", ondelete="SET NULL"), nullable=True, index=True)
    academic_year = Column(String(50), nullable=False, index=True)
    fee_type = Column(String(100), nullable=True)
    amount_due = Column(Numeric(10, 2), nullable=False)
    discount_amount = Column(Numeric(10, 2), default=0.00, nullable=False)
    due_date = Column(Date, nullable=False)
    status = Column(String(20), default="PENDING", nullable=False)  # "PENDING" / "UNPAID", "PARTIALLY_PAID", "PAID", "OVERDUE", "CANCELLED"

    # Relationships
    student = relationship("Student", back_populates="student_fees", lazy="selectin")
    school_class = relationship("SchoolClass", foreign_keys=[class_id], lazy="selectin")
    fee_structure = relationship("FeeStructure", back_populates="student_fees", lazy="selectin")
    payments = relationship("FeePayment", back_populates="student_fee", cascade="all, delete-orphan", lazy="selectin")

    __table_args__ = (
        UniqueConstraint("student_id", "fee_structure_id", name="uq_student_fee_structure"),
    )

    @property
    def net_amount(self) -> float:
        return float(self.amount_due) - float(self.discount_amount)

    @property
    def total_amount(self) -> float:
        return self.net_amount

    @property
    def total_paid(self) -> float:
        # Sum only verified payments
        return sum(float(p.amount_paid) for p in self.payments if getattr(p, "status", "VERIFIED") == "VERIFIED")

    @property
    def paid_amount(self) -> float:
        return self.total_paid

    @property
    def balance_remaining(self) -> float:
        return max(0.0, self.net_amount - self.total_paid)

    @property
    def balance(self) -> float:
        return self.balance_remaining

    @property
    def student_name(self) -> str:
        return self.student.full_name if self.student else ""

    @property
    def student_admission_number(self) -> str:
        return self.student.admission_number if self.student else ""

    @property
    def class_name(self) -> str:
        # Authoritative student current class takes priority
        if self.student and self.student.current_class:
            return self.student.current_class.name
        if self.school_class:
            return self.school_class.name
        return ""

    def __repr__(self) -> str:
        return f"<StudentFee(invoice='{self.invoice_number}', student_id={self.student_id}, due={self.amount_due}, balance={self.balance_remaining})>"


class FeePayment(Base, TimestampMixin):
    """Payment transaction receipt."""
    __tablename__ = "fee_payments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_fee_id = Column(Integer, ForeignKey("student_fees.id", ondelete="RESTRICT"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    receipt_number = Column(String(50), unique=True, nullable=False, index=True)  # e.g., "RCT-2026-000001"
    amount_paid = Column(Numeric(10, 2), nullable=False)
    payment_date = Column(Date, nullable=False)
    payment_method = Column(String(50), nullable=False)  # "CASH", "EVC_PLUS", "EDAHAB", "ZAAD", "SAHAL", "BANK_TRANSFER", "CHEQUE", "OTHER"
    reference_number = Column(String(100), nullable=True)  # Transaction ID / Gateway code
    recorded_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    notes = Column(Text, nullable=True)
    status = Column(String(20), default="VERIFIED", nullable=False)  # "VERIFIED", "PENDING", "FAILED", "CANCELLED"

    # Relationships
    student_fee = relationship("StudentFee", back_populates="payments")
    student = relationship("Student", back_populates="fee_payments", lazy="selectin")
    recorded_by = relationship("User", foreign_keys=[recorded_by_id], lazy="selectin")

    @property
    def student_name(self) -> str:
        return self.student.full_name if self.student else ""

    @property
    def student_admission_number(self) -> str:
        return self.student.admission_number if self.student else ""

    @property
    def invoice_number(self) -> str:
        return self.student_fee.invoice_number if self.student_fee else ""

    @property
    def recorded_by_name(self) -> str:
        return self.recorded_by.full_name if self.recorded_by else "System Administrator"

    def __repr__(self) -> str:
        return f"<FeePayment(receipt='{self.receipt_number}', amount={self.amount_paid}, method='{self.payment_method}')>"
