from typing import List, Optional, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field


# =============================================================================
# ADMIN APPOINTMENT & MANAGEMENT SCHEMAS
# =============================================================================

class FormMasterAppointPayload(BaseModel):
    teacher_id: int = Field(..., description="Teacher ID to appoint as Form Master")
    class_ids: List[int] = Field(..., min_length=1, max_length=2, description="List of 1 or 2 class IDs to assign")
    academic_year: str = Field(default="2026/2027", description="Academic year for the appointment, e.g. 2026/2027")
    notes: Optional[str] = Field(None, description="Optional notes or administrative remarks")


class FormMasterReplacePayload(BaseModel):
    new_teacher_id: int = Field(..., description="New Teacher ID to replace the existing Form Master")
    notes: Optional[str] = Field(None, description="Optional notes for replacement")


class FormMasterRevokePayload(BaseModel):
    notes: Optional[str] = Field(None, description="Optional revocation justification notes")


class FormMasterAssignmentResponse(BaseModel):
    id: int
    teacher_id: int
    teacher_name: str
    teacher_number: str
    teacher_email: Optional[str] = None
    teacher_phone: Optional[str] = None
    class_id: int
    class_name: str
    class_code: str
    division: Optional[str] = None
    level: Optional[str] = None
    section: Optional[str] = None
    academic_year: str
    status: str
    notes: Optional[str] = None
    appointed_by_name: Optional[str] = None
    appointed_at: datetime
    revoked_by_name: Optional[str] = None
    revoked_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ClassFormMasterItem(BaseModel):
    class_id: int
    class_name: str
    class_code: str
    division: str
    level: str
    section: Optional[str] = None
    academic_year: str
    capacity: int
    student_count: int
    assignment_id: Optional[int] = None
    form_master_id: Optional[int] = None
    form_master_name: Optional[str] = None
    form_master_number: Optional[str] = None
    form_master_email: Optional[str] = None
    form_master_phone: Optional[str] = None
    status: str  # "ASSIGNED", "UNASSIGNED"
    appointed_at: Optional[datetime] = None
    notes: Optional[str] = None


class AvailableTeacherItem(BaseModel):
    teacher_id: int
    teacher_number: str
    full_name: str
    email: str
    phone: Optional[str] = None
    gender: Optional[str] = None
    active_form_classes_count: int
    can_assign: bool
    assigned_classes: List[str] = []


class FormMasterAdminOverview(BaseModel):
    total_classes: int
    assigned_classes_count: int
    unassigned_classes_count: int
    total_form_masters: int
    academic_year: str


# =============================================================================
# FORM MASTER PORTAL SCHEMAS
# =============================================================================

class FormMasterClassSummary(BaseModel):
    id: int
    name: str
    code: str
    division: str
    level: str
    section: Optional[str] = None
    academic_year: str
    capacity: int
    student_count: int
    assignment_id: int
    appointed_at: datetime


class FormMasterStudentItem(BaseModel):
    student_id: int
    admission_number: str
    first_name: str
    last_name: str
    full_name: str
    gender: str
    phone: Optional[str] = None
    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None
    guardian_email: Optional[str] = None
    guardian_relationship: Optional[str] = None
    enrollment_status: str
    # Academic Summary
    total_exams_taken: int = 0
    average_marks: Optional[float] = None
    failing_subjects_count: int = 0
    has_poor_academic_performance: bool = False
    # Attendance Summary
    total_attendance_records: int = 0
    present_count: int = 0
    absent_count: int = 0
    late_count: int = 0
    attendance_rate: float = 100.0
    has_frequent_absences: bool = False
    # Fee Summary
    fee_total_invoiced: float = 0.0
    fee_total_paid: float = 0.0
    fee_balance: float = 0.0
    fee_status: str = "NO_FEES"  # "PAID", "PARTIALLY_PAID", "UNPAID", "OVERDUE", "NO_FEES"
    has_overdue_fees: bool = False


class FormMasterDashboardData(BaseModel):
    assigned_classes: List[FormMasterClassSummary]
    selected_class: FormMasterClassSummary
    total_students: int
    attendance_rate: float
    students_with_poor_performance_count: int
    students_with_frequent_absences_count: int
    students_with_outstanding_fees_count: int
    total_outstanding_fees: float
    poor_performance_students: List[Dict[str, Any]]
    frequent_absences_students: List[Dict[str, Any]]
    outstanding_fees_students: List[Dict[str, Any]]
    recent_activity: List[Dict[str, Any]]
    alerts: List[Dict[str, Any]]


class FormMasterResultsData(BaseModel):
    class_id: int
    class_name: str
    class_code: str
    academic_year: str
    available_exam_types: List[str]
    available_exams: List[Dict[str, Any]]
    subjects: List[Dict[str, Any]]
    students: List[Dict[str, Any]]
    class_average: float
    total_students: int
    pass_rate: float
    poor_performers_count: int
    top_performers_count: int


class FormMasterAttendanceData(BaseModel):
    class_id: int
    class_name: str
    class_code: str
    academic_year: str
    overall_stats: Dict[str, Any]
    students: List[Dict[str, Any]]
    recent_records: List[Dict[str, Any]]
    monthly_trend: List[Dict[str, Any]]


class FormMasterFeesData(BaseModel):
    class_id: int
    class_name: str
    class_code: str
    academic_year: str
    summary: Dict[str, Any]
    students: List[Dict[str, Any]]
