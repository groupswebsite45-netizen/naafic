from sqlalchemy import Column, Integer, String, Time, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class TeacherAvailability(Base, TimestampMixin):
    """Teacher schedule availability, unavailable periods, and workload constraints."""
    __tablename__ = "teacher_availabilities"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False, index=True)
    academic_year = Column(String(50), nullable=False, index=True)  # e.g., "2026/2027"
    day_of_week = Column(String(20), nullable=False, index=True)  # "Monday", "Tuesday", etc.
    start_time = Column(Time, nullable=True)  # unavailable window start or available window start
    end_time = Column(Time, nullable=True)  # unavailable window end or available window end
    is_available = Column(Boolean, default=True, nullable=False)
    max_periods_per_day = Column(Integer, default=5, nullable=True)
    max_periods_per_week = Column(Integer, default=25, nullable=True)
    notes = Column(String(255), nullable=True)

    # Relationships
    teacher = relationship("Teacher", backref="availabilities", lazy="joined")

    __table_args__ = (
        UniqueConstraint("teacher_id", "academic_year", "day_of_week", name="uq_teacher_year_day_availability"),
    )

    def __repr__(self) -> str:
        return f"<TeacherAvailability(teacher_id={self.teacher_id}, day='{self.day_of_week}', available={self.is_available})>"
