from sqlalchemy import Column, Integer, String, Text, Numeric, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class Exam(Base, TimestampMixin):
    """Examination schedule & metadata model."""
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)  # e.g., "Mid-Term Examination 2026"
    exam_type = Column(String(50), nullable=False)  # "Mid-Term", "Final", "Monthly Test", "Quiz"
    academic_year = Column(String(50), nullable=False, index=True)  # e.g., "2025-2026"
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="SET NULL"), nullable=True, index=True)
    start_time = Column(String(20), nullable=True)  # e.g., "08:30"
    end_time = Column(String(20), nullable=True)  # e.g., "11:30"
    result_submission_deadline = Column(DateTime(timezone=True), nullable=True, index=True)
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reopened_at = Column(DateTime(timezone=True), nullable=True)
    reopened_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reopen_reason = Column(Text, nullable=True)
    instructions = Column(Text, nullable=True)
    max_marks = Column(Numeric(5, 2), default=100.00, nullable=False)
    pass_marks = Column(Numeric(5, 2), default=50.00, nullable=False)
    status = Column(String(30), default="SCHEDULED", nullable=False, index=True)  # "DRAFT", "SCHEDULED", "OPEN_FOR_RESULTS", "CLOSED", "PUBLISHED", "CANCELLED"

    # Relationships
    school_class = relationship("SchoolClass", back_populates="exams", lazy="joined")
    subject = relationship("Subject", back_populates="exams", lazy="joined")
    teacher = relationship("Teacher", foreign_keys=[teacher_id], lazy="joined")
    created_by = relationship("User", foreign_keys=[created_by_id])
    reopened_by = relationship("User", foreign_keys=[reopened_by_id])
    results = relationship("ExamResult", back_populates="exam", cascade="all, delete-orphan")
    deadline_extensions = relationship("ExamDeadlineExtension", back_populates="exam", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("academic_year", "class_id", "subject_id", "exam_type", name="uq_exam_academic_year_class_subj_type"),
    )

    @property
    def total_marks(self) -> float:
        return float(self.max_marks) if self.max_marks is not None else 100.0

    @property
    def exam_date(self):
        return self.start_date

    def __repr__(self) -> str:
        return f"<Exam(id={self.id}, name='{self.name}', class_id={self.class_id}, subject_id={self.subject_id}, teacher_id={self.teacher_id}, status='{self.status}')>"


class ExamDeadlineExtension(Base, TimestampMixin):
    """Audit record for exam result submission deadline extensions."""
    __tablename__ = "exam_deadline_extensions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    exam_id = Column(Integer, ForeignKey("exams.id", ondelete="CASCADE"), nullable=False, index=True)
    previous_deadline = Column(DateTime(timezone=True), nullable=True)
    new_deadline = Column(DateTime(timezone=True), nullable=False)
    reason = Column(Text, nullable=False)
    extended_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    exam = relationship("Exam", back_populates="deadline_extensions")
    extended_by = relationship("User", foreign_keys=[extended_by_id], lazy="joined")

    def __repr__(self) -> str:
        return f"<ExamDeadlineExtension(exam_id={self.exam_id}, new_deadline='{self.new_deadline}')>"


class ExamResult(Base, TimestampMixin):
    """Student examination score record."""
    __tablename__ = "exam_results"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    exam_id = Column(Integer, ForeignKey("exams.id", ondelete="CASCADE"), nullable=False, index=True)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"), nullable=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    submission_id = Column(Integer, ForeignKey("result_submissions.id", ondelete="SET NULL"), nullable=True, index=True)
    release_batch_id = Column(Integer, ForeignKey("result_release_batches.id", ondelete="SET NULL"), nullable=True, index=True)

    attendance_status = Column(String(20), default="PRESENT", nullable=False)  # "PRESENT", "ABSENT", "EXCUSED"
    absence_reason = Column(Text, nullable=True)  # Specific reason when student is ABSENT or EXCUSED
    complaint = Column(Text, nullable=True)  # Student or exam-related complaint/grievance
    marks_obtained = Column(Numeric(5, 2), nullable=True)  # Nullable when student is ABSENT or EXCUSED
    grade = Column(String(20), nullable=True)  # "A+", "A", "B", "C", "D", "F", "ABSENT"
    remarks = Column(String(255), nullable=True)
    status = Column(String(20), default="DRAFT", nullable=False, index=True)  # "DRAFT", "SUBMITTED", "APPROVED", "RELEASED"
    recorded_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Exam paper / evidence document upload metadata
    paper_file_path = Column(String(500), nullable=True)
    paper_original_name = Column(String(255), nullable=True)
    paper_mime_type = Column(String(100), nullable=True)
    paper_file_size = Column(Integer, nullable=True)
    paper_uploaded_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    exam = relationship("Exam", back_populates="results", lazy="joined")
    school_class = relationship("SchoolClass", foreign_keys=[class_id], lazy="joined")
    student = relationship("Student", back_populates="exam_results", lazy="joined")
    subject = relationship("Subject", back_populates="exam_results", lazy="joined")
    submission = relationship("ResultSubmission", back_populates="results")
    release_batch = relationship("ResultReleaseBatch", back_populates="results")

    @property
    def exam_name(self) -> str:
        return self.exam.name if self.exam else ""

    @property
    def academic_year(self) -> str:
        return self.exam.academic_year if self.exam else ""

    @property
    def subject_name(self) -> str:
        return self.subject.name if self.subject else ""

    @property
    def subject_code(self) -> str:
        return self.subject.code if self.subject else ""

    @property
    def total_marks(self) -> float:
        return float(self.exam.max_marks) if self.exam and self.exam.max_marks else 100.0

    @property
    def percentage(self) -> Optional[float]:
        if self.marks_obtained is not None and self.total_marks > 0:
            return round(float(self.marks_obtained) / float(self.total_marks) * 100, 1)
        return None

    @property
    def student_name(self) -> str:
        return self.student.full_name if self.student else ""

    @property
    def student_admission_number(self) -> str:
        return self.student.admission_number if self.student else ""

    __table_args__ = (
        UniqueConstraint("exam_id", "student_id", "subject_id", name="uq_exam_student_subject"),
    )

    def __repr__(self) -> str:
        return f"<ExamResult(exam_id={self.exam_id}, student_id={self.student_id}, attendance={self.attendance_status}, marks={self.marks_obtained}, status={self.status})>"

