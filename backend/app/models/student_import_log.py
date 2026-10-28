from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class StudentImportLog(Base, TimestampMixin):
    """Audit history record for student bulk imports from Excel."""
    __tablename__ = "student_import_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    admin_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    file_name = Column(String(255), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="SET NULL"), nullable=True, index=True)
    academic_year = Column(String(50), nullable=False, index=True)
    total_rows = Column(Integer, default=0, nullable=False)
    imported_count = Column(Integer, default=0, nullable=False)
    already_enrolled_count = Column(Integer, default=0, nullable=False)
    skipped_count = Column(Integer, default=0, nullable=False)
    failed_count = Column(Integer, default=0, nullable=False)
    details = Column(Text, nullable=True)

    # Relationships
    admin_user = relationship("User", foreign_keys=[admin_user_id])
    school_class = relationship("SchoolClass", foreign_keys=[class_id])

    def __repr__(self) -> str:
        return f"<StudentImportLog(id={self.id}, file='{self.file_name}', imported={self.imported_count}, class_id={self.class_id})>"
