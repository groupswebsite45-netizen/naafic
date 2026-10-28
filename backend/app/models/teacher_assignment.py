from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class TeacherAssignment(Base, TimestampMixin):
    """Associative model mapping Teacher to Class and Subject."""
    __tablename__ = "teacher_assignments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False, index=True)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    academic_year = Column(String(50), nullable=False, index=True)  # e.g., "2025-2026"
    status = Column(String(20), default="ACTIVE", nullable=False)

    # Relationships
    teacher = relationship("Teacher", back_populates="assignments", lazy="joined")
    school_class = relationship("SchoolClass", back_populates="teacher_assignments", lazy="joined")
    subject = relationship("Subject", back_populates="teacher_assignments", lazy="joined")

    @property
    def teacher_name(self) -> str:
        return self.teacher.full_name if self.teacher else ""

    @property
    def teacher_number(self) -> str:
        return self.teacher.teacher_number if self.teacher else ""

    @property
    def class_name(self) -> str:
        return self.school_class.name if self.school_class else ""

    @property
    def class_code(self) -> str:
        return self.school_class.code if self.school_class else ""

    @property
    def section(self) -> str:
        return self.school_class.section if (self.school_class and self.school_class.section) else ""

    @property
    def subject_name(self) -> str:
        return self.subject.name if self.subject else ""

    @property
    def subject_code(self) -> str:
        return self.subject.code if (self.subject and self.subject.code) else ""

    @property
    def department(self) -> str:
        return self.subject.department if (self.subject and self.subject.department) else ""

    __table_args__ = (
        UniqueConstraint("teacher_id", "class_id", "subject_id", "academic_year", name="uq_teacher_class_subject_year"),
    )

    def __repr__(self) -> str:
        return f"<TeacherAssignment(teacher_id={self.teacher_id}, class_id={self.class_id}, subject_id={self.subject_id})>"
