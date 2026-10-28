from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel
from app.schemas.teacher import TeacherResponse, TeacherAssignmentResponse
from app.schemas.timetable import TimetableResponse
from app.schemas.exam import ExamResponse
from app.schemas.student import StudentResponse


class TeacherTodayAttendanceItem(BaseModel):
    class_id: int
    class_name: str
    subject_id: int
    subject_name: str
    period: Optional[str] = None
    is_recorded: bool
    total_students: int
    present_count: int
    absent_count: int


class TeacherPendingSubmissionWidget(BaseModel):
    exam_id: int
    exam_name: str
    class_id: int
    class_name: str
    subject_id: int
    subject_name: str
    academic_year: str
    status: str
    total_students: int
    completed_students: int
    pending_students: int


class TeacherDashboardResponse(BaseModel):
    teacher: TeacherResponse
    total_classes: int
    total_subjects: int
    total_students: int
    today_classes_count: int
    pending_results_count: int = 0
    today_attendance_summary: List[TeacherTodayAttendanceItem] = []
    pending_submissions: List[TeacherPendingSubmissionWidget] = []
    assigned_classes: List[TeacherAssignmentResponse]
    upcoming_timetables: List[TimetableResponse]
    active_exams: List[ExamResponse]


class TeacherClassStudentsResponse(BaseModel):
    class_id: int
    class_name: str
    class_code: str
    academic_year: str
    students: List[StudentResponse]


class TeacherClassDetailSubject(BaseModel):
    id: int
    name: str
    code: str


class TeacherClassDetailResponse(BaseModel):
    class_id: int
    name: str
    code: str
    section: Optional[str] = None
    academic_year: str
    capacity: int
    enrolled_students_count: int
    my_subjects: List[TeacherClassDetailSubject]
    students: List[StudentResponse]
    timetables: List[TimetableResponse]
    exams: List[ExamResponse]
    attendance_rate: float


class TeacherExamItemResponse(BaseModel):
    id: int
    name: str
    exam_type: str
    academic_year: str
    class_id: int
    class_name: str
    class_code: Optional[str] = None
    subject_id: int
    subject_name: str
    subject_code: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    result_submission_deadline: Optional[datetime] = None
    deadline_status: Optional[str] = None
    is_overdue: Optional[bool] = False
    remaining_time_human: Optional[str] = None
    max_marks: float = 100.0
    pass_marks: float = 50.0
    instructions: Optional[str] = None
    status: str
    submission_id: Optional[int] = None
    submission_status: str  # "DRAFT", "RESULTS_IN_PROGRESS", "SUBMITTED", "UNDER_REVIEW", "RELEASED", "RETURNED_FOR_CORRECTION"
    expected_students: int
    completed_students: int
    pending_students: int
    return_reason: Optional[str] = None
    is_locked: bool = False
    submitted_at: Optional[str] = None


class TeacherRosterStudentItem(BaseModel):
    student_id: int
    admission_number: str
    student_name: str
    gender: Optional[str] = None
    attendance_status: str = "PRESENT"  # PRESENT, ABSENT, EXCUSED
    marks_obtained: Optional[float] = None
    grade: Optional[str] = None
    remarks: Optional[str] = None
    paper_file_path: Optional[str] = None
    paper_original_name: Optional[str] = None
    paper_mime_type: Optional[str] = None
    paper_uploaded_at: Optional[str] = None


class TeacherExamRosterResponse(BaseModel):
    exam_id: int
    exam_name: str
    exam_type: str
    academic_year: str
    class_id: int
    class_name: str
    subject_id: int
    subject_name: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    result_submission_deadline: Optional[datetime] = None
    deadline_status: Optional[str] = None
    is_overdue: Optional[bool] = False
    remaining_time_human: Optional[str] = None
    instructions: Optional[str] = None
    max_marks: float
    pass_marks: float
    submission_id: Optional[int] = None
    submission_status: str
    is_locked: bool
    return_reason: Optional[str] = None
    students: List[TeacherRosterStudentItem]


class TeacherIdentityResponse(BaseModel):
    user_id: int
    teacher_id: int
    teacher_number: str
    name: str
    email: str
    role: str = "TEACHER"
    status: str = "ACTIVE"


class TeacherPortalProfileResponse(BaseModel):
    id: int
    teacher_number: str
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    gender: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    qualification: Optional[str] = None
    hire_date: Optional[date] = None
    status: str
    full_name: str
    user_id: Optional[int] = None
    assignments: List[TeacherAssignmentResponse] = []

