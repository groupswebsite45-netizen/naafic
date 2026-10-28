from datetime import date, datetime
from typing import List, Optional, Dict, Any
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.school_class import SchoolClassResponse
from app.schemas.subject import SubjectResponse


from pydantic import BaseModel, ConfigDict, Field, field_validator

ALLOWED_EXAM_TYPES = {"MID_TERM", "FINAL", "MONTHLY", "QUIZ"}
EXAM_TYPE_NORMALIZATION = {
    "MID_TERM": "MID_TERM",
    "MID-TERM": "MID_TERM",
    "MIDTERM": "MID_TERM",
    "FINAL": "FINAL",
    "FINALS": "FINAL",
    "MONTHLY": "MONTHLY",
    "MONTHLY TEST": "MONTHLY",
    "QUIZ": "QUIZ",
}


class ExamBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    exam_type: str = Field(..., description="MID_TERM, FINAL, MONTHLY, QUIZ")
    academic_year: str = Field(..., min_length=4, max_length=50)
    class_id: int
    subject_id: int
    start_date: date
    end_date: Optional[date] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    result_submission_deadline: Optional[datetime] = None
    teacher_id: Optional[int] = None
    instructions: Optional[str] = None
    max_marks: Decimal = Field(default=Decimal("100.00"), gt=0)
    pass_marks: Decimal = Field(default=Decimal("50.00"), ge=0)
    status: str = Field(default="SCHEDULED")  # "DRAFT", "SCHEDULED", "OPEN_FOR_RESULTS", "ONGOING", "COMPLETED", "CLOSED", "PUBLISHED", "CANCELLED"

    @field_validator("exam_type")
    @classmethod
    def validate_exam_type(cls, v: str) -> str:
        if not v:
            raise ValueError("Exam type is required.")
        norm = v.upper().strip()
        canonical = EXAM_TYPE_NORMALIZATION.get(norm)
        if not canonical or canonical not in ALLOWED_EXAM_TYPES:
            raise ValueError(f"Invalid exam type '{v}'. Allowed exam types are strictly: Mid-Term (MID_TERM), Final (FINAL), Monthly (MONTHLY), Quiz (QUIZ).")
        return canonical


class ExamCreate(ExamBase):
    pass


class ExamBatchCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    exam_type: str = Field(..., description="MID_TERM, FINAL, MONTHLY, QUIZ")
    academic_year: str = Field(..., min_length=4, max_length=50)
    class_ids: List[int] = Field(..., min_length=1)
    subject_ids: List[int] = Field(..., min_length=1)
    start_date: date
    end_date: Optional[date] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    result_submission_deadline: Optional[datetime] = None
    instructions: Optional[str] = None
    max_marks: Decimal = Field(default=Decimal("100.00"), gt=0)
    pass_marks: Decimal = Field(default=Decimal("50.00"), ge=0)
    status: str = Field(default="SCHEDULED")

    @field_validator("exam_type")
    @classmethod
    def validate_exam_type(cls, v: str) -> str:
        if not v:
            raise ValueError("Exam type is required.")
        norm = v.upper().strip()
        canonical = EXAM_TYPE_NORMALIZATION.get(norm)
        if not canonical or canonical not in ALLOWED_EXAM_TYPES:
            raise ValueError(f"Invalid exam type '{v}'. Allowed exam types are strictly: Mid-Term (MID_TERM), Final (FINAL), Monthly (MONTHLY), Quiz (QUIZ).")
        return canonical


class ExamUpdate(BaseModel):
    name: Optional[str] = None
    exam_type: Optional[str] = None
    academic_year: Optional[str] = None
    class_id: Optional[int] = None
    subject_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    result_submission_deadline: Optional[datetime] = None
    instructions: Optional[str] = None
    max_marks: Optional[Decimal] = None
    pass_marks: Optional[Decimal] = None
    status: Optional[str] = None


class ExamDeadlineExtensionResponse(BaseModel):
    id: int
    exam_id: int
    previous_deadline: Optional[datetime] = None
    new_deadline: datetime
    reason: Optional[str] = None
    extended_by_id: Optional[int] = None
    extended_by_name: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DeadlineExtendRequest(BaseModel):
    new_deadline: datetime
    reason: Optional[str] = None


class ExamReopenRequest(BaseModel):
    new_deadline: Optional[datetime] = None
    reason: Optional[str] = None


class ExamStatusUpdateRequest(BaseModel):
    status: str


class ExamConflictCheckRequest(BaseModel):
    class_id: int
    start_date: date
    end_date: Optional[date] = None
    exclude_exam_id: Optional[int] = None


class ExamConflictItem(BaseModel):
    conflict_type: str
    exam_id: int
    exam_name: str
    subject_name: str
    start_date: str
    end_date: str
    message: str


class ExamConflictCheckResponse(BaseModel):
    has_conflict: bool
    conflicts_count: int
    conflicts: List[ExamConflictItem]


class ExamResultEntry(BaseModel):
    student_id: int
    marks_obtained: Decimal = Field(..., ge=0)
    grade: Optional[str] = None
    remarks: Optional[str] = None


class BulkExamResultsCreate(BaseModel):
    exam_id: int
    subject_id: Optional[int] = None
    results: List[ExamResultEntry]


class ExamResultResponse(BaseModel):
    id: int
    exam_id: int
    class_id: Optional[int] = None
    student_id: int
    subject_id: int
    marks_obtained: Optional[Decimal] = None
    grade: Optional[str] = None
    remarks: Optional[str] = None
    status: str = "RELEASED"
    attendance_status: str = "PRESENT"
    exam_name: Optional[str] = None
    academic_year: Optional[str] = None
    subject_name: Optional[str] = None
    subject_code: Optional[str] = None
    total_marks: Optional[float] = 100.0
    percentage: Optional[float] = None
    recorded_by_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    student_name: Optional[str] = None
    student_admission_number: Optional[str] = None
    roll_number: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ExamResponse(ExamBase):
    id: int
    school_class: Optional[SchoolClassResponse] = None
    subject: Optional[SubjectResponse] = None
    results_count: Optional[int] = 0
    enrolled_students_count: Optional[int] = 0
    completion_percentage: Optional[float] = 0.0
    created_by_id: Optional[int] = None
    reopened_at: Optional[datetime] = None
    reopened_by_id: Optional[int] = None
    reopen_reason: Optional[str] = None
    is_overdue: Optional[bool] = False
    deadline_status: Optional[str] = None  # ON_TRACK, APPROACHING, OVERDUE, CLOSED, EXTENDED
    deadline_extensions: Optional[List[ExamDeadlineExtensionResponse]] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedExamResponse(BaseModel):
    items: List[ExamResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ExamSummary(BaseModel):
    total_exams: int
    upcoming_exams: int
    ongoing_exams: int
    completed_exams: int
    published_results: int
    total_students_assessed: int


class ExamFilterOptions(BaseModel):
    academic_years: List[str]
    exam_types: List[str]
    statuses: List[str]
    classes: List[dict]
    subjects: List[dict]


class ExamStudentSheetItem(BaseModel):
    student_id: int
    admission_number: str
    student_name: str
    roll_number: Optional[str] = None
    gender: Optional[str] = None
    result_id: Optional[int] = None
    marks_obtained: Optional[Decimal] = None
    grade: Optional[str] = None
    remarks: Optional[str] = None
    is_saved: bool = False
    updated_at: Optional[datetime] = None


class ExamDetailResponse(BaseModel):
    exam: ExamResponse
    enrolled_count: int
    results_count: int
    completion_percentage: float
    average_score: Optional[float] = None
    highest_score: Optional[float] = None
    lowest_score: Optional[float] = None
    pass_count: int = 0
    fail_count: int = 0
    pass_rate: float = 0.0
    student_sheet: List[ExamStudentSheetItem]


class PublishResultsPayload(BaseModel):
    publish: bool = True


class ReportCardSubject(BaseModel):
    subject_id: int
    subject_name: str
    subject_code: str
    marks_obtained: float
    max_marks: float
    pass_marks: float
    grade: str
    percentage: float
    remarks: str
    is_passed: bool


class ReportCardStudent(BaseModel):
    id: int
    admission_number: str
    full_name: str
    gender: Optional[str] = None
    roll_number: Optional[str] = None
    class_name: str
    class_section: Optional[str] = None


class ReportCardSummary(BaseModel):
    total_subjects: int
    total_marks_obtained: float
    total_possible_marks: float
    overall_percentage: float
    overall_grade: str
    overall_remark: str
    publication_status: str


class ReportCardResponse(BaseModel):
    school_name: str
    school_motto: str
    academic_year: str
    exam_name: str
    exam_type: str
    student: ReportCardStudent
    subjects: List[ReportCardSubject]
    summary: ReportCardSummary
