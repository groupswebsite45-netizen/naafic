from datetime import date, datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, field_validator


class TeacherRosterAttendanceItem(BaseModel):
    teacher_id: int
    teacher_number: str
    teacher_name: str
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    qualification: Optional[str] = None
    employment_status: Optional[str] = None
    status: str = "PRESENT"  # "PRESENT", "ABSENT", "LATE", "ON_LEAVE"
    reason: Optional[str] = None
    attendance_id: Optional[int] = None
    is_saved: bool = False

    model_config = ConfigDict(from_attributes=True)


class TeacherDailyRosterResponse(BaseModel):
    date: date
    academic_year: str
    is_recorded: bool
    total_teachers: int
    present_count: int
    absent_count: int
    late_count: int
    on_leave_count: int
    teachers: List[TeacherRosterAttendanceItem]


class TeacherSaveEntry(BaseModel):
    teacher_id: int
    status: str = "PRESENT"  # "PRESENT", "ABSENT", "LATE", "ON_LEAVE"
    reason: Optional[str] = None


class TeacherBulkSavePayload(BaseModel):
    date: date
    academic_year: str
    entries: List[TeacherSaveEntry]

    @field_validator("date")
    @classmethod
    def validate_date_not_future(cls, v: date) -> date:
        if v > date.today():
            raise ValueError(f"Teacher attendance cannot be recorded for future dates (Today is {date.today().isoformat()}).")
        return v


class TeacherAttendanceKPIs(BaseModel):
    total_teachers: int
    today_present: int
    today_absent: int
    today_late: int
    today_on_leave: int
    today_attendance_percentage: float
    overall_attendance_percentage: float


class TeacherAttendanceDailySummaryItem(BaseModel):
    date: date
    day_name: str
    present_count: int
    absent_count: int
    late_count: int
    on_leave_count: int
    attendance_percentage: float


class TeacherAttendanceMonthlySummaryItem(BaseModel):
    month_name: str
    month: int
    year: int
    present_count: int
    absent_count: int
    late_count: int
    on_leave_count: int
    attendance_percentage: float


class TeacherAttendanceDashboardResponse(BaseModel):
    kpis: TeacherAttendanceKPIs
    daily_summary: List[TeacherAttendanceDailySummaryItem]
    monthly_summary: List[TeacherAttendanceMonthlySummaryItem]


class TeacherAttendanceRecordItem(BaseModel):
    id: int
    teacher_id: int
    teacher_name: str
    teacher_number: str
    phone: Optional[str] = None
    email: Optional[str] = None
    date: date
    academic_year: str
    status: str
    reason: Optional[str] = None
    recorded_by_name: Optional[str] = None
    recorded_at: Optional[datetime] = None


class TeacherAttendanceRecordsResponse(BaseModel):
    items: List[TeacherAttendanceRecordItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class TeacherStaffAttendanceSummaryItem(BaseModel):
    teacher_id: int
    teacher_name: str
    teacher_number: str
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    total_days: int
    days_present: int
    days_absent: int
    days_late: int
    days_on_leave: int
    attendance_percentage: float
    last_attendance_date: Optional[date] = None
    last_status: Optional[str] = None


class StaffAttendanceSummaryResponse(BaseModel):
    academic_year: str
    period_label: str
    total_teachers: int
    overall_percentage: float
    total_present_days: int
    total_absent_days: int
    total_late_days: int
    total_leave_days: int
    teachers: List[TeacherStaffAttendanceSummaryItem]

