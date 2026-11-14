from datetime import date, datetime, time
from typing import List, Optional
from pydantic import BaseModel, EmailStr, ConfigDict, Field
from app.schemas.school_class import SchoolClassResponse
from app.schemas.subject import SubjectResponse


class TeacherAssignmentBase(BaseModel):
    teacher_id: int
    class_id: int
    subject_id: int
    academic_year: str = "2026/2027"
    status: str = "ACTIVE"


class TeacherAssignmentCreate(BaseModel):
    class_id: int
    subject_id: int
    academic_year: str = "2026/2027"


class TeacherAssignmentUpdate(BaseModel):
    teacher_id: Optional[int] = None
    class_id: Optional[int] = None
    subject_id: Optional[int] = None
    academic_year: Optional[str] = None
    status: Optional[str] = None


class TeacherBulkAssignmentItem(BaseModel):
    teacher_id: Optional[int] = None
    class_id: int
    subject_id: int
    academic_year: str = "2026/2027"
    status: str = "ACTIVE"


class TeacherBulkAssignmentCreate(BaseModel):
    teacher_id: Optional[int] = None
    assignments: List[TeacherBulkAssignmentItem]


class TeacherAssignmentCheckResponse(BaseModel):
    is_assigned: bool
    is_same_teacher: bool
    available: bool
    message: str
    assignment_id: Optional[int] = None
    teacher_id: Optional[int] = None
    teacher_name: Optional[str] = None


class TeacherAssignmentResponse(BaseModel):
    id: int
    teacher_id: int
    class_id: int
    subject_id: int
    academic_year: str
    status: str
    teacher_name: Optional[str] = None
    teacher_number: Optional[str] = None
    class_name: Optional[str] = None
    class_code: Optional[str] = None
    section: Optional[str] = None
    subject_name: Optional[str] = None
    subject_code: Optional[str] = None
    department: Optional[str] = None
    student_count: int = 0
    is_current_academic_year: bool = True
    display_status: str = "ACTIVE"
    school_class: Optional[SchoolClassResponse] = None
    subject: Optional[SubjectResponse] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class TeacherBase(BaseModel):
    teacher_number: str = Field(..., min_length=3, max_length=50)
    first_name: str = Field(..., min_length=2, max_length=100)
    middle_name: Optional[str] = None
    last_name: str = Field(..., min_length=2, max_length=100)
    gender: str = Field(..., description="Male or Female")
    date_of_birth: Optional[date] = None
    phone: Optional[str] = None
    email: EmailStr
    address: Optional[str] = None
    qualification: Optional[str] = None
    hire_date: Optional[date] = None
    status: str = Field(default="ACTIVE")


class TeacherCreate(TeacherBase):
    create_portal_account: bool = False
    portal_username: Optional[str] = None
    portal_password: Optional[str] = None


class TeacherUpdate(BaseModel):
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    qualification: Optional[str] = None
    hire_date: Optional[date] = None
    status: Optional[str] = None


class TeacherStatusUpdate(BaseModel):
    status: str
    reason: Optional[str] = None


class TeacherResponse(TeacherBase):
    id: int
    user_id: Optional[int] = None
    email: str
    full_name: str
    has_portal_access: bool = False
    created_at: datetime
    updated_at: datetime
    assignments: List[TeacherAssignmentResponse] = []

    model_config = ConfigDict(from_attributes=True)


class TeacherSummary(BaseModel):
    total_teachers: int
    active_teachers: int
    inactive_teachers: int
    unassigned_teachers: int


class TeacherListResponse(BaseModel):
    items: List[TeacherResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class TeacherTimetableSlot(BaseModel):
    id: int
    class_id: int
    subject_id: int
    teacher_id: Optional[int] = None
    academic_year: str
    day_of_week: str
    start_time: time
    end_time: time
    room: Optional[str] = None
    status: str
    school_class: Optional[SchoolClassResponse] = None
    subject: Optional[SubjectResponse] = None

    model_config = ConfigDict(from_attributes=True)


class TeacherFullProfile(TeacherResponse):
    portal_username: Optional[str] = None
    portal_email: Optional[str] = None
    timetables: List[TeacherTimetableSlot] = []
    assigned_classes_count: int = 0
    teaching_subjects_count: int = 0
    teaching_assignments_count: int = 0

    model_config = ConfigDict(from_attributes=True)
