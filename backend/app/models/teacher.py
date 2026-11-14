from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class Teacher(Base, TimestampMixin):
    """Teacher profile entity linked to system user."""
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), unique=True, nullable=True, index=True)
    teacher_number = Column(String(50), unique=True, nullable=False, index=True)  # e.g., "TCH-2026-001"
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=False)
    gender = Column(String(20), nullable=False)  # "Male", "Female"
    date_of_birth = Column(Date, nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    address = Column(Text, nullable=True)
    qualification = Column(String(200), nullable=True)
    hire_date = Column(Date, nullable=True)
    status = Column(String(20), default="ACTIVE", nullable=False)  # "ACTIVE", "INACTIVE", "ON_LEAVE"

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    assignments = relationship("TeacherAssignment", back_populates="teacher", cascade="all, delete-orphan")
    timetables = relationship("Timetable", back_populates="teacher")
    form_master_assignments = relationship("FormMasterAssignment", back_populates="teacher", cascade="all, delete-orphan")

    @property
    def full_name(self) -> str:
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:
        return f"<Teacher(id={self.id}, teacher_number='{self.teacher_number}', name='{self.full_name}')>"
