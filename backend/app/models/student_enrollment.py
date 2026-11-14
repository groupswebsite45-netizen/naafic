from sqlalchemy import Column, Integer, String, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class StudentEnrollment(Base, TimestampMixin):
    """Student class enrollment with historical record preservation."""
    __tablename__ = "student_enrollments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="RESTRICT"), nullable=False, index=True)
    academic_year = Column(String(50), nullable=False, default="2026/2027", index=True)  # e.g., "2026/2027"
    roll_number = Column(String(50), nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    status = Column(String(20), default="ACTIVE", nullable=False)  # "ACTIVE", "COMPLETED", "TRANSFERRED", "PROMOTED"

    # Relationships
    student = relationship("Student", back_populates="enrollments", lazy="joined")
    school_class = relationship("SchoolClass", back_populates="enrollments", lazy="joined")

    __table_args__ = (
        UniqueConstraint("student_id", "academic_year", name="uq_student_academic_year"),
    )

    def __repr__(self) -> str:
        return f"<StudentEnrollment(student_id={self.student_id}, class_id={self.class_id}, year='{self.academic_year}')>"
