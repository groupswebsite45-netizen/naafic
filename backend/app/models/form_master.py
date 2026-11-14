from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func, Index
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class FormMasterAssignment(Base, TimestampMixin):
    """
    Form Master Assignment entity.
    Maps a Teacher to one or two School Classes as their supervisory Form Master.
    Admin-appointed only. Provides cross-subject read-only supervision for academic,
    attendance, and fee progress.
    """
    __tablename__ = "form_master_assignments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False, index=True)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False, index=True)
    academic_year = Column(String(50), nullable=False, default="2026/2027", index=True)  # e.g., "2026/2027"
    status = Column(String(20), default="ACTIVE", nullable=False, index=True)  # "ACTIVE", "REVOKED", "INACTIVE"
    notes = Column(Text, nullable=True)

    appointed_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    appointed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    revoked_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    teacher = relationship("Teacher", back_populates="form_master_assignments", foreign_keys=[teacher_id], lazy="joined")
    school_class = relationship("SchoolClass", back_populates="form_master_assignments", foreign_keys=[class_id], lazy="joined")
    appointed_by = relationship("User", foreign_keys=[appointed_by_id], lazy="joined")
    revoked_by = relationship("User", foreign_keys=[revoked_by_id], lazy="joined")

    __table_args__ = (
        Index("ix_form_master_class_year_status", "class_id", "academic_year", "status"),
        Index("ix_form_master_teacher_year_status", "teacher_id", "academic_year", "status"),
    )

    @property
    def teacher_name(self) -> str:
        return self.teacher.full_name if self.teacher else ""

    @property
    def teacher_number(self) -> str:
        return self.teacher.teacher_number if self.teacher else ""

    @property
    def teacher_email(self) -> str:
        return self.teacher.email if self.teacher else ""

    @property
    def teacher_phone(self) -> str:
        return self.teacher.phone if (self.teacher and self.teacher.phone) else ""

    @property
    def class_name(self) -> str:
        return self.school_class.name if self.school_class else ""

    @property
    def class_code(self) -> str:
        return self.school_class.code if self.school_class else ""

    @property
    def division(self) -> str:
        return self.school_class.division if self.school_class else ""

    @property
    def level(self) -> str:
        return self.school_class.level if self.school_class else ""

    @property
    def section(self) -> str:
        return self.school_class.section if (self.school_class and self.school_class.section) else ""

    @property
    def appointed_by_name(self) -> str:
        if self.appointed_by:
            return self.appointed_by.full_name or self.appointed_by.username
        return ""

    @property
    def revoked_by_name(self) -> str:
        if self.revoked_by:
            return self.revoked_by.full_name or self.revoked_by.username
        return ""

    def __repr__(self) -> str:
        return f"<FormMasterAssignment(id={self.id}, teacher_id={self.teacher_id}, class_id={self.class_id}, year='{self.academic_year}', status='{self.status}')>"
