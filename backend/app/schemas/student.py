from datetime import date, datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, EmailStr, ConfigDict, Field
from app.schemas.school_class import SchoolClassResponse


class StudentEnrollmentResponse(BaseModel):
    id: int
    student_id: int
    class_id: int
    academic_year: str
    roll_number: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: str
    school_class: Optional[SchoolClassResponse] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StudentEnrollmentCreate(BaseModel):
    class_id: int
    academic_year: str = "2026/2027"
    roll_number: Optional[str] = None
    start_date: Optional[date] = None


class StudentBase(BaseModel):
    admission_number: str = Field(..., min_length=1, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=100)
    middle_name: Optional[str] = None
    last_name: str = Field(..., min_length=1, max_length=100)
    gender: str = Field(..., description="Male or Female")
    date_of_birth: Optional[date] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None
    guardian_email: Optional[EmailStr] = None
    guardian_relationship: Optional[str] = None
    admission_date: Optional[date] = None
    status: str = Field(default="ACTIVE")


class StudentCreate(StudentBase):
    initial_class_id: Optional[int] = None
    academic_year: Optional[str] = "2026/2027"
    create_portal_account: bool = False
    portal_username: Optional[str] = None
    portal_password: Optional[str] = None


class StudentUpdate(BaseModel):
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None
    guardian_email: Optional[EmailStr] = None
    guardian_relationship: Optional[str] = None
    admission_date: Optional[date] = None
    status: Optional[str] = None


class StudentStatusUpdate(BaseModel):
    status: str = Field(..., description="ACTIVE, INACTIVE, SUSPENDED, GRADUATED, TRANSFERRED")
    reason: Optional[str] = None


class StudentSummaryMetrics(BaseModel):
    total_students: int
    active_students: int
    inactive_students: int
    unassigned_students: int


class StudentResponse(StudentBase):
    id: int
    user_id: Optional[int] = None
    full_name: str
    has_portal_access: bool = False
    portal_username: Optional[str] = None
    portal_is_active: Optional[bool] = None
    photo_path: Optional[str] = None
    photo_url: Optional[str] = None
    photo_filename: Optional[str] = None
    photo_mime_type: Optional[str] = None
    photo_size: Optional[int] = None
    photo_uploaded_at: Optional[datetime] = None
    photo_updated_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    current_class: Optional[SchoolClassResponse] = None
    enrollments: List[StudentEnrollmentResponse] = []

    model_config = ConfigDict(from_attributes=True)


class StudentFeeItem(BaseModel):
    id: int
    fee_name: str
    academic_year: str
    total_amount: float
    paid_amount: float
    balance: float
    status: str
    due_date: Optional[date] = None
    created_at: datetime


class StudentExamItem(BaseModel):
    id: int
    exam_name: str
    exam_type: str
    subject_name: str
    academic_year: str
    marks_obtained: float
    total_marks: float
    grade: Optional[str] = None
    remarks: Optional[str] = None
    exam_date: Optional[date] = None


class StudentFullProfileResponse(StudentResponse):
    financial_summary: Dict[str, Any] = {
        "total_billed": 0.0,
        "total_paid": 0.0,
        "outstanding_balance": 0.0,
    }
    fees: List[StudentFeeItem] = []
    exam_results: List[StudentExamItem] = []


class CreateStudentPortalAccountPayload(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Unique alphanumeric username (min 3 chars)")
    password: str = Field(..., min_length=6, description="Initial temporary password (min 6 chars)")


class ResetStudentPortalPasswordPayload(BaseModel):
    password: str = Field(..., min_length=6, description="New password (min 6 chars)")


class UpdateStudentPortalStatusPayload(BaseModel):
    is_active: bool = Field(..., description="Enable (True) or Disable (False) student portal login")


class UpdateStudentPortalUsernamePayload(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="New portal username (min 3 chars)")


class BatchEnablePortalsPayload(BaseModel):
    academic_year: Optional[str] = None
    class_id: Optional[int] = None
    student_ids: Optional[List[int]] = None
    default_password: Optional[str] = "Student@123"


class BatchStudentPortalItem(BaseModel):
    student_id: int
    student_name: str
    admission_number: str
    username: str
    status: str  # "CREATED", "ACTIVATED", "ALREADY_ACTIVE"


class BatchEnablePortalsResponse(BaseModel):
    success: bool = True
    message: str
    total_processed: int
    enabled_count: int
    already_active_count: int
    default_password: str
    students: List[BatchStudentPortalItem] = []


class ToggleStudentPortalPayload(BaseModel):
    is_active: Optional[bool] = None
    default_password: Optional[str] = "Student@123"


class StudentPortalLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    student_id: int
    student_name: str
    username: str
    portal_url: str = "/student/exams"

