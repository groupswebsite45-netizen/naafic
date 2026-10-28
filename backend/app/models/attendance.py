from sqlalchemy import Column, Integer, String, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class Attendance(Base, TimestampMixin):
    """Student attendance record per subject lecture / period."""
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="SET NULL"), nullable=True, index=True)
    academic_year = Column(String(50), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    period = Column(String(50), nullable=True)  # e.g., "08:00 - 09:00"
    status = Column(String(20), default="PRESENT", nullable=False, index=True)  # "PRESENT", "ABSENT", "EXCUSED", "LATE"
    remarks = Column(String(255), nullable=True)
    recorded_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    student = relationship("Student", foreign_keys=[student_id], lazy="joined")
    school_class = relationship("SchoolClass", foreign_keys=[class_id], lazy="joined")
    subject = relationship("Subject", foreign_keys=[subject_id], lazy="joined")
    teacher = relationship("Teacher", foreign_keys=[teacher_id], lazy="joined")
    recorded_by = relationship("User", foreign_keys=[recorded_by_id])

    __table_args__ = (
        UniqueConstraint("student_id", "date", "subject_id", "period", name="uq_student_date_subject_period"),
    )

    def __repr__(self) -> str:
        return f"<Attendance(student_id={self.student_id}, subject_id={self.subject_id}, date={self.date}, status='{self.status}')>"
