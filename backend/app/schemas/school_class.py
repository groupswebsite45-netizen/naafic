from datetime import date, datetime, time
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class SchoolClassBase(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    division: str = Field(default="PRIMARY", description="PRIMARY or SECONDARY")
    level: Optional[str] = Field(default="Grade 7", description="Grade 1..Grade 8 or Form 1..Form 4")
    section: Optional[str] = Field(default="A", description="A, B, C, D, E...")
    academic_year: str = Field(..., min_length=4, max_length=50)
    capacity: int = Field(default=40, ge=1, le=200)
    description: Optional[str] = None
    status: str = Field(default="ACTIVE")


class SchoolClassCreate(SchoolClassBase):
    pass


class SchoolClassUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    division: Optional[str] = None
    level: Optional[str] = None
    section: Optional[str] = None
    academic_year: Optional[str] = None
    capacity: Optional[int] = Field(None, ge=1, le=200)
    description: Optional[str] = None
    status: Optional[str] = None


class ClassStatusUpdate(BaseModel):
    status: str
    reason: Optional[str] = None


class ClassCapacityMetrics(BaseModel):
    enrolled: int
    capacity: int
    available_seats: int
    utilization_rate: float
    capacity_status: str  # "NORMAL", "NEAR_CAPACITY", "FULL", "OVER_CAPACITY"


class SchoolClassResponse(SchoolClassBase):
    id: int
    created_at: datetime
    updated_at: datetime
    students_count: int = 0
    teachers_count: int = 0
    subjects_count: int = 0
    available_seats: int = 0
    utilization_rate: float = 0.0
    capacity_status: str = "NORMAL"

    model_config = ConfigDict(from_attributes=True)


class ClassSummary(BaseModel):
    total_classes: int
    active_classes: int
    total_students_enrolled: int
    available_seats: int
    near_capacity_classes: int


class ClassEnrollmentStudent(BaseModel):
    id: int
    student_id: int
    admission_number: str
    full_name: str
    gender: str
    status: str
    has_portal_access: bool
    enrollment_date: date
    academic_year: str

    model_config = ConfigDict(from_attributes=True)


class ClassEnrollmentCreate(BaseModel):
    student_id: int
    academic_year: str
    enrollment_date: Optional[date] = None


class ClassTeacherAssignmentItem(BaseModel):
    id: int
    teacher_id: int
    teacher_number: str
    full_name: str
    subject_id: int
    subject_name: str
    subject_code: str
    academic_year: str
    status: str

    model_config = ConfigDict(from_attributes=True)


class ClassTeacherAssignPayload(BaseModel):
    teacher_id: int
    subject_id: int
    academic_year: str


class ClassSubjectItem(BaseModel):
    id: int
    code: str
    name: str
    department: Optional[str] = None
    teacher_id: Optional[int] = None
    teacher_name: Optional[str] = None
    status: str = "ACTIVE"


class ClassTimetableItem(BaseModel):
    id: int
    day_of_week: str
    start_time: time
    end_time: time
    subject_name: str
    subject_code: str
    teacher_name: Optional[str] = None
    room: Optional[str] = None
    status: str = "ACTIVE"

    model_config = ConfigDict(from_attributes=True)


class ClassExamItem(BaseModel):
    id: int
    name: str
    exam_type: str
    academic_year: str
    term: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: str = "SCHEDULED"

    model_config = ConfigDict(from_attributes=True)


class ClassFullProfileResponse(SchoolClassResponse):
    capacity_metrics: ClassCapacityMetrics
    students: List[ClassEnrollmentStudent] = []
    teachers: List[ClassTeacherAssignmentItem] = []
    subjects: List[ClassSubjectItem] = []
    timetables: List[ClassTimetableItem] = []
    exams: List[ClassExamItem] = []

    model_config = ConfigDict(from_attributes=True)
