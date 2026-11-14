from datetime import date, datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from app.schemas.attendance import StudentSubjectAttendanceBreakdown, StudentAttendanceHistoryDetailResponse


class AdminTeacherOption(BaseModel):
    id: int
    name: str
    employee_number: Optional[str] = None
    class_id: Optional[int] = None
    subject_id: Optional[int] = None
    academic_year: Optional[str] = None


class AdminClassOption(BaseModel):
    id: int
    name: str
    code: str
    academic_year: str
    grade_level: Optional[str] = None
    section: Optional[str] = None


class AdminSubjectOption(BaseModel):
    id: int
    name: str
    code: str
    class_id: Optional[int] = None
    academic_year: Optional[str] = None


class AdminMonthOption(BaseModel):
    value: int
    name: str


class AdminAttendanceFilterOptionsResponse(BaseModel):
    academic_years: List[str]
    classes: List[AdminClassOption]
    subjects: List[AdminSubjectOption]
    teachers: List[AdminTeacherOption] = []
    months: List[AdminMonthOption]


class AdminAttendanceKPIs(BaseModel):
    total_students: int
    today_present: int
    today_absent: int
    today_late: int
    today_attendance_percentage: float
    overall_attendance_percentage: float
    frequent_absentees_count: int


class AdminAttendanceDailySummaryItem(BaseModel):
    date: date
    day_name: str
    present_count: int
    absent_count: int
    late_count: int
    attendance_percentage: float


class AdminAttendanceWeeklySummaryItem(BaseModel):
    week_label: str
    start_date: date
    end_date: date
    present_count: int
    absent_count: int
    attendance_percentage: float


class AdminAttendanceMonthlySummaryItem(BaseModel):
    month_name: str
    month: int
    year: int
    present_count: int
    absent_count: int
    attendance_percentage: float


class AdminAttendanceRecentSessionItem(BaseModel):
    date: date
    period: Optional[str] = None
    class_id: int
    class_name: str
    subject_id: int
    subject_name: str
    teacher_name: Optional[str] = None
    total_students: int
    present_count: int
    absent_count: int
    late_count: int = 0
    attendance_percentage: float
    recorded_at: Optional[datetime] = None


class AbsenceDateDetail(BaseModel):
    date: date
    period: Optional[str] = None
    subject_name: Optional[str] = None
    status: str
    remarks: Optional[str] = None


class AdminAttendanceFrequentAbsenteeItem(BaseModel):
    student_id: int
    student_name: str
    admission_number: str
    class_id: int
    class_name: str
    gender: Optional[str] = None
    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None
    total_sessions: int
    present_count: int
    absent_count: int
    late_count: int
    attendance_percentage: float
    last_absent_date: Optional[date] = None
    absence_dates: List[AbsenceDateDetail] = []


class AdminAttendanceDashboardResponse(BaseModel):
    kpis: AdminAttendanceKPIs
    daily_summary: List[AdminAttendanceDailySummaryItem]
    weekly_summary: List[AdminAttendanceWeeklySummaryItem]
    monthly_summary: List[AdminAttendanceMonthlySummaryItem]
    frequent_absentees: List[AdminAttendanceFrequentAbsenteeItem]
    recent_sessions: List[AdminAttendanceRecentSessionItem]


class AdminAttendanceRecordItem(BaseModel):
    id: int
    date: date
    period: Optional[str] = None
    student_id: int
    student_name: str
    admission_number: str
    class_id: int
    class_name: str
    subject_id: int
    subject_name: str
    teacher_name: Optional[str] = None
    status: str
    remarks: Optional[str] = None
    recorded_at: Optional[datetime] = None


class AdminAttendanceRecordsListResponse(BaseModel):
    items: List[AdminAttendanceRecordItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class AdminClassInfo(BaseModel):
    id: int
    name: str
    code: str
    academic_year: str
    total_enrolled: int


class AdminClassAttendanceSummaryStats(BaseModel):
    total_sessions: int
    total_records: int
    present_count: int
    absent_count: int
    late_count: int
    attendance_percentage: float


class AdminClassStudentAttendanceItem(BaseModel):
    student_id: int
    student_name: str
    admission_number: str
    gender: Optional[str] = None
    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None
    total_sessions: int
    days_present: int
    days_absent: int
    days_late: int
    attendance_percentage: float
    absence_dates: List[AbsenceDateDetail] = []
    daily_status: Dict[str, str] = {}  # "YYYY-MM-DD" -> "PRESENT"|"ABSENT"|"LATE"
    subject_breakdown: List[StudentSubjectAttendanceBreakdown] = []


class AdminClassAttendanceReportResponse(BaseModel):
    class_info: AdminClassInfo
    summary: AdminClassAttendanceSummaryStats
    students: List[AdminClassStudentAttendanceItem]
    dates_header: List[date]
    academic_year: str
    period_label: str

