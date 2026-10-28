from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class ResultReleaseBatch(Base, TimestampMixin):
    """
    Result Release Batch model for class-based result publication tracking.
    When Admin releases results for a class, a batch is generated to group and audit the release.
    """
    __tablename__ = "result_release_batches"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    batch_code = Column(String(50), unique=True, nullable=False, index=True)  # e.g., "RB-2026-0001"
    exam_name = Column(String(100), nullable=False, index=True)
    academic_year = Column(String(50), nullable=False, index=True)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False, index=True)
    release_type = Column(String(20), default="FULL", nullable=False)  # "FULL", "PARTIAL"
    status = Column(String(20), default="RELEASED", nullable=False)  # "RELEASED", "REVOKED"

    released_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    released_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )
    results_count = Column(Integer, default=0, nullable=False)
    notes = Column(Text, nullable=True)

    # Relationships
    school_class = relationship("SchoolClass", foreign_keys=[class_id], lazy="joined")
    released_by = relationship("User", foreign_keys=[released_by_id])
    results = relationship("ExamResult", back_populates="release_batch")
    views = relationship("StudentResultView", back_populates="release_batch")

    def __repr__(self) -> str:
        return f"<ResultReleaseBatch(batch_code='{self.batch_code}', class_id={self.class_id}, results={self.results_count})>"
