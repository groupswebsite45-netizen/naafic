from datetime import time, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class TimetableSettingBase(BaseModel):
    academic_year: str = Field(..., min_length=4, max_length=50)
    division: str = Field(default="ALL", description="PRIMARY, SECONDARY, ALL")
    school_days: str = Field(
        default="Saturday,Sunday,Monday,Tuesday,Wednesday,Thursday",
        description="Comma-separated school days"
    )
    start_time: time = Field(default=time(7, 30))
    end_time: time = Field(default=time(13, 30))
    period_duration_minutes: int = Field(default=45, ge=20, le=120)
    break_duration_minutes: int = Field(default=20, ge=0, le=60)
    break_after_period: int = Field(default=3, ge=1, le=10)
    lunch_duration_minutes: int = Field(default=30, ge=0, le=90)
    lunch_after_period: int = Field(default=5, ge=0, le=12)
    periods_per_day: int = Field(default=6, ge=1, le=12)
    is_active: bool = Field(default=True)


class TimetableSettingCreate(TimetableSettingBase):
    pass


class TimetableSettingUpdate(BaseModel):
    academic_year: Optional[str] = None
    division: Optional[str] = None
    school_days: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    period_duration_minutes: Optional[int] = None
    break_duration_minutes: Optional[int] = None
    break_after_period: Optional[int] = None
    lunch_duration_minutes: Optional[int] = None
    lunch_after_period: Optional[int] = None
    periods_per_day: Optional[int] = None
    is_active: Optional[bool] = None


class TimetableSettingResponse(TimetableSettingBase):
    id: int
    created_at: datetime
    updated_at: datetime
    days_list: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
