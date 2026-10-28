from datetime import time, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class TeacherAvailabilityBase(BaseModel):
    teacher_id: int
    academic_year: str = Field(..., min_length=4, max_length=50)
    day_of_week: str = Field(..., description="Saturday, Sunday, Monday, Tuesday, Wednesday, Thursday, Friday")
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_available: bool = Field(default=True)
    max_periods_per_day: Optional[int] = Field(default=5, ge=1, le=12)
    max_periods_per_week: Optional[int] = Field(default=25, ge=1, le=60)
    notes: Optional[str] = None


class TeacherAvailabilityBatchItem(BaseModel):
    day_of_week: str
    is_available: bool = True
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    max_periods_per_day: Optional[int] = Field(default=5, ge=1, le=12)
    max_periods_per_week: Optional[int] = Field(default=25, ge=1, le=60)
    notes: Optional[str] = None


class TeacherAvailabilityCreate(BaseModel):
    teacher_id: int
    academic_year: str = Field(..., min_length=4, max_length=50)
    day_of_week: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_available: Optional[bool] = True
    max_periods_per_day: Optional[int] = Field(default=5, ge=1, le=12)
    max_periods_per_week: Optional[int] = Field(default=25, ge=1, le=60)
    notes: Optional[str] = None
    availabilities: Optional[List[TeacherAvailabilityBatchItem]] = None


class TeacherAvailabilityUpdate(BaseModel):
    is_available: Optional[bool] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    max_periods_per_day: Optional[int] = None
    max_periods_per_week: Optional[int] = None
    notes: Optional[str] = None


class TeacherAvailabilityResponse(TeacherAvailabilityBase):
    id: int
    teacher_name: Optional[str] = None
    teacher_number: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TeacherAvailabilityMatrixItem(BaseModel):
    teacher_id: int
    teacher_name: str
    teacher_number: Optional[str] = None
    total_assigned_weekly_periods: int = 0
    max_periods_per_week: int = 25
    daily_availability: dict = Field(default_factory=dict)  # { "Saturday": { is_available: true, ... } }
