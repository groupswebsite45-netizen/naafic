import enum
from datetime import datetime, date, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    Boolean,
    Text,
    ForeignKey,
    Index,
    CheckConstraint,
    func,
)
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class AcademicYearStatus(str, enum.Enum):
    UPCOMING = "Upcoming"
    ACTIVE = "Active"
    COMPLETED = "Completed"
    ARCHIVED = "Archived"


class AcademicYear(Base, TimestampMixin):
    """
    Central authoritative Academic Year model for Somroyal Educational Management System.
    Governs operational scope, scheduling, promotions, and historical archiving across all modules.
    """
    __tablename__ = "academic_years"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    institution_id = Column(Integer, ForeignKey("institutions.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # Standard format: e.g. "2026/2027"
    name = Column(String(50), nullable=False, index=True)
    code = Column(String(50), nullable=True, index=True)
    
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    status = Column(String(20), nullable=False, default=AcademicYearStatus.UPCOMING.value, index=True)
    is_current = Column(Boolean, default=False, nullable=False, index=True)
    
    activation_date = Column(DateTime(timezone=True), nullable=True)
    completion_date = Column(DateTime(timezone=True), nullable=True)
    
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    created_by = relationship("User", foreign_keys=[created_by_id])
    institution = relationship("Institution", foreign_keys=[institution_id])

    __table_args__ = (
        CheckConstraint("end_date > start_date", name="chk_academic_year_dates"),
        Index("ix_academic_years_inst_status", "institution_id", "status"),
        Index("ix_academic_years_inst_name", "institution_id", "name", unique=True),
    )

    @property
    def is_active(self) -> bool:
        return self.status == AcademicYearStatus.ACTIVE.value

    @property
    def is_completed(self) -> bool:
        return self.status == AcademicYearStatus.COMPLETED.value

    @property
    def is_upcoming(self) -> bool:
        return self.status == AcademicYearStatus.UPCOMING.value

    @property
    def is_archived(self) -> bool:
        return self.status == AcademicYearStatus.ARCHIVED.value

    def __repr__(self) -> str:
        return f"<AcademicYear(id={self.id}, name='{self.name}', status='{self.status}', inst={self.institution_id})>"

