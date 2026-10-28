from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class AttendanceRecordResponse(BaseModel):
    id: int
    date: date
    subject_id: int
    subject_name: str
    subject_code: Optional[str] = None
    period: Optional[str] = None
    status: str  # "PRESENT", "ABSENT", "EXCUSED", "LATE"
    teacher_name: Optional[str] = None
    remarks: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class SubjectAttendanceSummary(BaseModel):
    subject_id: int
    subject_name: str
    subject_code: Optional[str] = None
    total_classes: int
    present_count: int
    absent_count: int
    excused_count: int
    attendance_percentage: float


class AttendanceOverallSummary(BaseModel):
    total_classes: int
    present_count: int
    absent_count: int
    excused_count: int
    attendance_percentage: float


class StudentAttendancePortalResponse(BaseModel):
    academic_year: str
    summary: AttendanceOverallSummary
    by_subject: List[SubjectAttendanceSummary]
    history: List[AttendanceRecordResponse]


# =============================================================================
# TEACHER ATTENDANCE MODULE SCHEMAS
# =============================================================================

class TeacherAttendanceClassOption(BaseModel):
    id: int
    name: str
    code: str
    academic_year: str


class TeacherAttendanceSubjectOption(BaseModel):
    id: int
    name: str
    code: str
    class_id: int


class TeacherAttendanceOptionsResponse(BaseModel):
    academic_years: List[str]
    classes: List[TeacherAttendanceClassOption]
    subjects: List[TeacherAttendanceSubjectOption]


class StudentAttendanceRosterItem(BaseModel):
    student_id: int
    student_name: str
    admission_number: str
    gender: Optional[str] = None
    attendance_id: Optional[int] = None
    status: str = "PRESENT"  # "PRESENT", "ABSENT", "EXCUSED", "LATE"
    remarks: Optional[str] = None


class TeacherAttendanceRosterResponse(BaseModel):
    class_id: int
    class_name: str
    subject_id: int
    subject_name: str
    academic_year: str
    date: date
    period: Optional[str] = None
    is_recorded: bool = False
    total_students: int = 0
    present_count: int = 0
    absent_count: int = 0
    students: List[StudentAttendanceRosterItem] = []


class StudentAttendanceEntry(BaseModel):
    student_id: int
    status: str = "PRESENT"  # "PRESENT", "ABSENT", "EXCUSED", "LATE"
    remarks: Optional[str] = None


class TeacherSaveAttendancePayload(BaseModel):
    class_id: int
    subject_id: int
    academic_year: str
    date: date
    period: Optional[str] = None
    entries: List[StudentAttendanceEntry]


class TeacherAttendanceSessionItem(BaseModel):
    session_key: str
    date: date
    period: Optional[str] = None
    class_id: int
    class_name: str
    subject_id: int
    subject_name: str
    academic_year: str
    total_students: int
    present_count: int
    absent_count: int
    attendance_percentage: float
    recorded_at: Optional[datetime] = None


class AbsentRecordDetail(BaseModel):
    date: date
    period: Optional[str] = None
    subject_name: Optional[str] = None
    status: str
    remarks: Optional[str] = None


class TeacherStudentAttendanceSummaryItem(BaseModel):
    student_id: int
    student_name: str
    admission_number: str
    class_id: int
    class_name: str
    total_sessions: int
    present_count: int
    absent_count: int
    excused_count: int
    attendance_percentage: float
    absent_history: List[AbsentRecordDetail] = []


class TeacherAttendanceSummaryResponse(BaseModel):
    class_id: int
    class_name: str
    subject_id: Optional[int] = None
    subject_name: Optional[str] = None
    total_sessions: int
    students: List[TeacherStudentAttendanceSummaryItem]

