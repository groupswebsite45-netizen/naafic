from sqlalchemy import Column, Integer, String, Time, Boolean
from app.core.database import Base
from app.models.base import TimestampMixin


class TimetableSetting(Base, TimestampMixin):
    """Timetable configuration entity defining school hours, periods, and breaks."""
    __tablename__ = "timetable_settings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    academic_year = Column(String(50), nullable=False, index=True)  # e.g., "2026/2027"
    division = Column(String(20), default="ALL", nullable=False)  # "PRIMARY", "SECONDARY", "ALL"
    school_days = Column(
        String(255),
        default="Saturday,Sunday,Monday,Tuesday,Wednesday,Thursday",
        nullable=False
    )
    start_time = Column(Time, nullable=False)  # e.g. 07:30
    end_time = Column(Time, nullable=False)  # e.g. 13:30
    period_duration_minutes = Column(Integer, default=45, nullable=False)
    break_duration_minutes = Column(Integer, default=20, nullable=False)
    break_after_period = Column(Integer, default=3, nullable=False)  # break occurs after period N
    lunch_duration_minutes = Column(Integer, default=30, nullable=False)  # 0 if no separate lunch
    lunch_after_period = Column(Integer, default=5, nullable=False)  # lunch occurs after period N
    periods_per_day = Column(Integer, default=6, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    @property
    def days_list(self):
        """Return list of active school days."""
        return [d.strip() for d in self.school_days.split(",") if d.strip()]

    def __repr__(self) -> str:
        return f"<TimetableSetting(id={self.id}, year='{self.academic_year}', periods={self.periods_per_day})>"
