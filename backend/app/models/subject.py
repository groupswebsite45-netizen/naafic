from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class Subject(Base, TimestampMixin):
    """Academic Subject model with division and level curriculum isolation."""
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)  # e.g., "Mathematics", "Islamic Studies", "Physics"
    code = Column(String(50), unique=True, nullable=False, index=True)  # e.g., "MATH-101", "PHY-201"
    division = Column(String(20), default="ALL", nullable=False, index=True)  # "PRIMARY", "SECONDARY", "ALL"
    applicable_levels = Column(String(255), nullable=True)  # comma-separated list of applicable levels
    department = Column(String(100), nullable=True)  # e.g., "Sciences", "Languages", "Social Studies"
    description = Column(Text, nullable=True)
    status = Column(String(20), default="ACTIVE", nullable=False)  # "ACTIVE", "INACTIVE"

    # Relationships
    teacher_assignments = relationship("TeacherAssignment", back_populates="subject", cascade="all, delete-orphan")
    timetables = relationship("Timetable", back_populates="subject", cascade="all, delete-orphan")
    exams = relationship("Exam", back_populates="subject", cascade="all, delete-orphan")
    exam_results = relationship("ExamResult", back_populates="subject", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Subject(id={self.id}, code='{self.code}', name='{self.name}', div='{self.division}')>"

