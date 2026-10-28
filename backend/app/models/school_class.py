from sqlalchemy import Column, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class SchoolClass(Base, TimestampMixin):
    """School Class / Grade / Section model with structured division and level hierarchy."""
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)  # e.g., "Grade 7 - A", "Form 1 - B"
    code = Column(String(50), unique=True, nullable=False, index=True)  # e.g., "G7-A-2026", "F1-B-2026"
    division = Column(String(20), default="PRIMARY", nullable=False, index=True)  # "PRIMARY", "SECONDARY"
    level = Column(String(50), nullable=False, index=True)  # "Grade 1".."Grade 8", "Form 1".."Form 4"
    section = Column(String(50), nullable=True, index=True)  # "A", "B", "C", "D", "E"...
    academic_year = Column(String(50), nullable=False, index=True)  # e.g., "2026-2027"
    capacity = Column(Integer, default=40, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="ACTIVE", nullable=False)  # "ACTIVE", "INACTIVE", "ARCHIVED"

    # Relationships
    enrollments = relationship("StudentEnrollment", back_populates="school_class", cascade="all, delete-orphan")
    teacher_assignments = relationship("TeacherAssignment", back_populates="school_class", cascade="all, delete-orphan")
    timetables = relationship("Timetable", back_populates="school_class", cascade="all, delete-orphan")
    fee_structures = relationship("FeeStructure", back_populates="school_class")
    exams = relationship("Exam", back_populates="school_class", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("academic_year", "division", "level", "section", name="uq_class_academic_year_div_level_sec"),
    )

    def __repr__(self) -> str:
        return f"<SchoolClass(id={self.id}, code='{self.code}', name='{self.name}', div='{self.division}', level='{self.level}', sec='{self.section}')>"

