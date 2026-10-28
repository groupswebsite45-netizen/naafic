from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class StudentResultView(Base, TimestampMixin):
    """
    Student Result View record to verify whether students have viewed their released results.
    Distinguishes 'Released' from 'Viewed'.
    """
    __tablename__ = "student_result_views"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    exam_name = Column(String(100), nullable=False, index=True)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False, index=True)
    academic_year = Column(String(50), nullable=False, index=True)
    release_batch_id = Column(Integer, ForeignKey("result_release_batches.id", ondelete="SET NULL"), nullable=True, index=True)

    first_viewed_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    last_viewed_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    view_count = Column(Integer, default=1, nullable=False)

    # Relationships
    student = relationship("Student", foreign_keys=[student_id], lazy="joined")
    school_class = relationship("SchoolClass", foreign_keys=[class_id], lazy="joined")
    release_batch = relationship("ResultReleaseBatch", back_populates="views")

    __table_args__ = (
        UniqueConstraint("student_id", "exam_name", "class_id", "academic_year", name="uq_student_exam_class_year_view"),
    )

    def __repr__(self) -> str:
        return f"<StudentResultView(student_id={self.student_id}, exam='{self.exam_name}', views={self.view_count})>"
