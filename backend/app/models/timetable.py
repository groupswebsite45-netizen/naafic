from sqlalchemy import Column, Integer, String, Time, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class Timetable(Base, TimestampMixin):
    """Timetable schedule slot entity."""
    __tablename__ = "timetables"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="SET NULL"), nullable=True, index=True)
    academic_year = Column(String(50), nullable=False, default="2026/2027", index=True)  # e.g., "2026/2027"
    day_of_week = Column(String(20), nullable=False, index=True)  # "Monday", "Tuesday", etc.
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    room = Column(String(50), nullable=True)  # e.g., "Room 101", "Lab A"
    period_number = Column(Integer, nullable=True, index=True)
    is_break = Column(Boolean, default=False, nullable=False)
    status = Column(String(20), default="ACTIVE", nullable=False)  # "DRAFT", "GENERATED", "PUBLISHED", "ACTIVE", "ARCHIVED"
    published_at = Column(DateTime(timezone=True), nullable=True)
    published_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    school_class = relationship("SchoolClass", back_populates="timetables", lazy="joined")
    subject = relationship("Subject", back_populates="timetables", lazy="joined")
    teacher = relationship("Teacher", back_populates="timetables", lazy="joined")
    published_by = relationship("User", foreign_keys=[published_by_id], lazy="joined")

    def __repr__(self) -> str:
        return f"<Timetable(id={self.id}, day='{self.day_of_week}', time='{self.start_time}-{self.end_time}', class_id={self.class_id})>"
