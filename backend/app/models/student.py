from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class Student(Base, TimestampMixin):
    """Student profile entity linked to system user."""
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), unique=True, nullable=True, index=True)
    admission_number = Column(String(50), unique=True, nullable=False, index=True)  # e.g., "ADM-2026-001"
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=False)
    gender = Column(String(20), nullable=False)  # "Male", "Female"
    date_of_birth = Column(Date, nullable=True)
    phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    guardian_name = Column(String(200), nullable=True)
    guardian_phone = Column(String(50), nullable=True)
    guardian_email = Column(String(255), nullable=True)
    guardian_relationship = Column(String(50), nullable=True)  # "Father", "Mother", "Guardian"
    admission_date = Column(Date, nullable=True)
    status = Column(String(20), default="ACTIVE", nullable=False)  # "ACTIVE", "GRADUATED", "TRANSFERRED", "SUSPENDED", "INACTIVE"

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    enrollments = relationship("StudentEnrollment", back_populates="student", cascade="all, delete-orphan", lazy="joined")
    student_fees = relationship("StudentFee", back_populates="student", cascade="all, delete-orphan")
    fee_payments = relationship("FeePayment", back_populates="student", cascade="all, delete-orphan")
    exam_results = relationship("ExamResult", back_populates="student", cascade="all, delete-orphan")

    @property
    def full_name(self) -> str:
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"

    @property
    def current_enrollment(self):
        """Get the latest active enrollment if any, otherwise latest enrollment."""
        if not self.enrollments:
            return None
        sorted_enrollments = sorted(
            self.enrollments,
            key=lambda e: (str(e.academic_year or ''), e.id or 0),
            reverse=True
        )
        active = [e for e in sorted_enrollments if e.status == "ACTIVE"]
        return active[0] if active else sorted_enrollments[0]

    @property
    def current_class(self):
        """Get currently enrolled SchoolClass."""
        ce = self.current_enrollment
        return ce.school_class if ce else None

    @property
    def has_portal_access(self) -> bool:
        if hasattr(self, '_has_portal_access'):
            return self._has_portal_access
        return bool(self.user_id and self.user and self.user.is_active)

    @has_portal_access.setter
    def has_portal_access(self, val: bool):
        self._has_portal_access = val

    @property
    def portal_is_active(self) -> bool:
        if hasattr(self, '_portal_is_active'):
            return self._portal_is_active
        return bool(self.user and self.user.is_active) if self.user_id else False

    @portal_is_active.setter
    def portal_is_active(self, val: bool):
        self._portal_is_active = val

    @property
    def portal_username(self):
        if hasattr(self, '_portal_username'):
            return self._portal_username
        return self.user.username if self.user else None

    @portal_username.setter
    def portal_username(self, val):
        self._portal_username = val

    def __repr__(self) -> str:
        return f"<Student(id={self.id}, admission_number='{self.admission_number}', name='{self.full_name}')>"
