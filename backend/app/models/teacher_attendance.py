from sqlalchemy import Column, Integer, String, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class TeacherAttendance(Base, TimestampMixin):
    """Daily staff attendance record for registered teachers."""
    __tablename__ = "teacher_attendances"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    academic_year = Column(String(50), nullable=False, index=True)
    status = Column(String(20), default="PRESENT", nullable=False, index=True)  # "PRESENT", "ABSENT", "LATE", "ON_LEAVE"
    reason = Column(String(255), nullable=True)  # Absence, lateness, or leave reason
    recorded_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    teacher = relationship("Teacher", foreign_keys=[teacher_id], lazy="joined")
    recorded_by = relationship("User", foreign_keys=[recorded_by_id], lazy="joined")

    __table_args__ = (
        UniqueConstraint("teacher_id", "date", name="uq_teacher_date_attendance"),
    )

    def __repr__(self) -> str:
        return f"<TeacherAttendance(teacher_id={self.teacher_id}, date={self.date}, status='{self.status}')>"

