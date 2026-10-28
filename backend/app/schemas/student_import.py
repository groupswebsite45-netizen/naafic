from typing import Optional, List, Any
from datetime import datetime, date
from pydantic import BaseModel, Field


class StudentImportRowPreview(BaseModel):
    row_number: int
    admission_number: Optional[str] = None
    student_name: Optional[str] = None
    full_name: Optional[str] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[str] = None
    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None
    guardian_email: Optional[str] = None
    guardian_relationship: Optional[str] = "Parent"
    phone: Optional[str] = None
    address: Optional[str] = None
    status: str = "VALID"  # VALID, ERROR, WARNING, ALREADY_EXISTS
    error_reason: Optional[str] = None
    is_existing_student: bool = False
    is_already_enrolled: bool = False
    existing_student_id: Optional[int] = None
    existing_class_name: Optional[str] = None


class StudentImportDestination(BaseModel):
    class_id: int
    class_name: str
    academic_year_id: Optional[str] = None
    academic_year: str


class StudentImportSummaryStats(BaseModel):
    total_rows: int
    valid_rows: int
    invalid_rows: int
    existing_rows: int


class StudentImportPreviewResponse(BaseModel):
    success: bool = True
    total_rows: int
    valid_rows: int
    warning_rows: int
    error_rows: int
    already_exists_rows: int
    class_id: int
    class_name: str
    academic_year: str
    destination: Optional[StudentImportDestination] = None
    summary: Optional[StudentImportSummaryStats] = None
    rows: List[StudentImportRowPreview]


class StudentImportExecuteRequest(BaseModel):
    class_id: int
    academic_year: str
    file_name: Optional[str] = "students.xlsx"
    rows: List[StudentImportRowPreview]
    enroll_existing_students: bool = False


class StudentImportSummaryResponse(BaseModel):
    success: bool
    total_rows: int
    imported_count: int
    already_enrolled_count: int
    skipped_count: int
    failed_count: int
    class_id: int
    class_name: str
    academic_year: str
    message: str
    errors: List[str] = []


class StudentImportLogResponse(BaseModel):
    id: int
    file_name: str
    class_id: Optional[int] = None
    class_name: Optional[str] = None
    academic_year: str
    total_rows: int
    imported_count: int
    already_enrolled_count: int
    skipped_count: int
    failed_count: int
    admin_name: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
