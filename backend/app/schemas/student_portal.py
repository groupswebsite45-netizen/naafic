from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.school_class import SchoolClassResponse
from app.schemas.timetable import TimetableResponse
from app.schemas.fee import StudentFeeResponse
from app.schemas.exam import ExamResultResponse
from app.schemas.attendance import AttendanceOverallSummary


class StudentProfileResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    admission_number: str
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    full_name: str
    gender: str
    date_of_birth: Optional[date] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None
    guardian_email: Optional[str] = None
    guardian_relationship: Optional[str] = None
    admission_date: Optional[date] = None
    status: str
    current_class_name: Optional[str] = None
    current_class_code: Optional[str] = None
    academic_year: Optional[str] = None
    portal_account_status: str = "Active"
    photo_url: Optional[str] = None
    photo_path: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class StudentSubjectDetail(BaseModel):
    id: int
    name: str
    code: str
    department: Optional[str] = None
    teacher_name: Optional[str] = None
    status: str = "ACTIVE"

    model_config = ConfigDict(from_attributes=True)


class EnrollmentHistoryItem(BaseModel):
    academic_year: str
    class_name: str
    class_code: str
    section: Optional[str] = None
    status: str
    roll_number: Optional[str] = None


class StudentClassDetailsResponse(BaseModel):
    school_class: Optional[SchoolClassResponse] = None
    academic_year: Optional[str] = None
    section: Optional[str] = None
    class_teacher_name: Optional[str] = None
    capacity: int = 40
    classmates_count: int = 0
    subjects: List[StudentSubjectDetail] = []
    enrollment_history: List[EnrollmentHistoryItem] = []


class LatestExamResultSummary(BaseModel):
    exam_name: str
    academic_year: str
    subject_name: str
    marks_obtained: Optional[float] = None
    total_marks: float = 100.0
    percentage: Optional[float] = None
    grade: Optional[str] = None
    released_at: Optional[datetime] = None


class StudentFeeSummary(BaseModel):
    total_billed: float
    total_paid: float
    total_outstanding: float
    is_cleared: bool


class StudentFeesPortalResponse(BaseModel):
    summary: StudentFeeSummary
    fees: List[StudentFeeResponse]


class StudentDashboardResponse(BaseModel):
    student: StudentProfileResponse
    current_class: Optional[SchoolClassResponse] = None
    academic_year: Optional[str] = None
    enrolled_subjects_count: int
    attendance_summary: Optional[AttendanceOverallSummary] = None
    total_fees_due: float
    total_fees_paid: float
    outstanding_balance: float
    latest_exam_result: Optional[LatestExamResultSummary] = None
    next_class_period: Optional[TimetableResponse] = None
    today_schedule: List[TimetableResponse] = []
    recent_exam_results: List[ExamResultResponse] = []


class StudentPublishedExamItem(BaseModel):
    id: int
    name: str
    exam_type: str
    academic_year: str
    class_id: int
    class_name: Optional[str] = None
    class_code: Optional[str] = None
    section: Optional[str] = None
    subject_id: int
    subject_name: Optional[str] = None
    subject_code: Optional[str] = None
    teacher_name: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    instructions: Optional[str] = None
    max_marks: float = 100.0
    pass_marks: float = 50.0
    status: str = "PUBLISHED"
    published_at: Optional[datetime] = None
    result_submission_deadline: Optional[datetime] = None
    # Results publication isolation (marks remain None unless officially RELEASED)
    has_released_result: bool = False
    marks_obtained: Optional[float] = None
    grade: Optional[str] = None
    remarks: Optional[str] = None
    attendance_status: Optional[str] = None
    percentage: Optional[float] = None
    total_marks: float = 100.0

    model_config = ConfigDict(from_attributes=True)

