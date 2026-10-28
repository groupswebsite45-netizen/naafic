from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey, UniqueConstraint, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class ResultSubmission(Base, TimestampMixin):
    """
    Result Submission entity representing teacher's submission of marks 
    for a specific exam, class, and subject.
    
    Workflow stages:
    DRAFT -> SUBMITTED -> UNDER_REVIEW -> APPROVED -> RELEASED
                         ↳ RETURNED (Teacher edits & resubmits)
    """
    __tablename__ = "result_submissions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    exam_id = Column(Integer, ForeignKey("exams.id", ondelete="CASCADE"), nullable=False, index=True)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False, index=True)
    academic_year = Column(String(50), nullable=False, index=True)
    exam_name = Column(String(100), nullable=False, index=True)
    exam_type = Column(String(50), nullable=True, index=True)

    status = Column(String(30), default="DRAFT", nullable=False, index=True)
    # Allowed: "DRAFT", "PARTIAL", "SUBMITTED", "UNDER_REVIEW", "APPROVED", "RETURNED", "RELEASED"

    expected_students = Column(Integer, default=0, nullable=False)
    completed_students = Column(Integer, default=0, nullable=False)
    pending_students = Column(Integer, default=0, nullable=False)

    submitted_at = Column(DateTime(timezone=True), nullable=True)
    submitted_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    reviewed_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    approved_at = Column(DateTime(timezone=True), nullable=True)
    approved_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    returned_at = Column(DateTime(timezone=True), nullable=True)
    return_reason = Column(Text, nullable=True)

    submission_deadline = Column(Date, nullable=True)
    revisions = Column(JSON, default=list, nullable=True)  # Audit trail of submissions and return-for-correction events

    # Relationships
    exam = relationship("Exam", foreign_keys=[exam_id], lazy="joined")
    school_class = relationship("SchoolClass", foreign_keys=[class_id], lazy="joined")
    subject = relationship("Subject", foreign_keys=[subject_id], lazy="joined")
    teacher = relationship("Teacher", foreign_keys=[teacher_id], lazy="joined")
    submitted_by = relationship("User", foreign_keys=[submitted_by_id])
    reviewed_by = relationship("User", foreign_keys=[reviewed_by_id])
    approved_by = relationship("User", foreign_keys=[approved_by_id])
    results = relationship("ExamResult", back_populates="submission", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("exam_id", "class_id", "subject_id", "teacher_id", name="uq_result_sub_exam_class_subj_tch"),
    )

    def __repr__(self) -> str:
        return f"<ResultSubmission(id={self.id}, exam='{self.exam_name}', class_id={self.class_id}, subject_id={self.subject_id}, status='{self.status}')>"
