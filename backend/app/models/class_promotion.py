from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class ClassPromotionBatch(Base):
    """
    Tracks a bulk or class-level promotion batch operation.
    Enables tracking of batch transactions, audit logs, and safe rollbacks.
    """
    __tablename__ = "class_promotion_batches"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    batch_code = Column(String(50), unique=True, nullable=False, index=True)  # e.g., "PROM-2027-0001"
    source_academic_year = Column(String(50), nullable=False, index=True)      # e.g., "2026/2027" or "2025-2026"
    target_academic_year = Column(String(50), nullable=False, index=True)      # e.g., "2027/2028" or "2026-2027"
    promotion_type = Column(String(30), default="BULK_PROMOTION", nullable=False)  # BULK_PROMOTION, CLASS_LEVEL, INDIVIDUAL_CHANGE
    status = Column(String(30), default="COMPLETED", nullable=False, index=True)  # COMPLETED, ROLLED_BACK, FAILED
    total_promoted = Column(Integer, default=0, nullable=False)
    total_graduated = Column(Integer, default=0, nullable=False)
    total_skipped = Column(Integer, default=0, nullable=False)
    reason = Column(Text, nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )

    # Relationships
    created_by = relationship("User", foreign_keys=[created_by_id])
    records = relationship("ClassPromotionRecord", back_populates="batch", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<ClassPromotionBatch(id={self.id}, code='{self.batch_code}', type='{self.promotion_type}', status='{self.status}')>"


class ClassPromotionRecord(Base):
    """
    Granular audit log of each individual student's class change / promotion within a batch.
    Preserves exact linkage of source and target enrollments.
    """
    __tablename__ = "class_promotion_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    batch_id = Column(Integer, ForeignKey("class_promotion_batches.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    from_class_id = Column(Integer, ForeignKey("classes.id", ondelete="SET NULL"), nullable=True, index=True)
    to_class_id = Column(Integer, ForeignKey("classes.id", ondelete="SET NULL"), nullable=True, index=True)
    from_enrollment_id = Column(Integer, ForeignKey("student_enrollments.id", ondelete="SET NULL"), nullable=True)
    to_enrollment_id = Column(Integer, ForeignKey("student_enrollments.id", ondelete="SET NULL"), nullable=True)
    source_academic_year = Column(String(50), nullable=False)
    target_academic_year = Column(String(50), nullable=False)
    action = Column(String(30), default="PROMOTED", nullable=False)  # PROMOTED, GRADUATED, CLASS_CHANGED, SKIPPED
    status = Column(String(30), default="COMPLETED", nullable=False)  # COMPLETED, ROLLED_BACK
    reason = Column(String(255), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    batch = relationship("ClassPromotionBatch", back_populates="records")
    student = relationship("Student", foreign_keys=[student_id], lazy="joined")
    from_class = relationship("SchoolClass", foreign_keys=[from_class_id], lazy="joined")
    to_class = relationship("SchoolClass", foreign_keys=[to_class_id], lazy="joined")
    from_enrollment = relationship("StudentEnrollment", foreign_keys=[from_enrollment_id])
    to_enrollment = relationship("StudentEnrollment", foreign_keys=[to_enrollment_id])

    def __repr__(self) -> str:
        return f"<ClassPromotionRecord(id={self.id}, student_id={self.student_id}, action='{self.action}')>"
