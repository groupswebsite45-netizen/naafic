from datetime import datetime, date
from typing import List, Optional
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class ResultOverviewStats(BaseModel):
    """Aggregate statistics for Admin Exam Results dashboard."""
    academic_year: str
    exam_name: str
    classes_count: int
    submissions_completed: int
    submissions_total: int
    pending_count: int
    approved_count: int
    released_count: int


class ClassResultSummaryItem(BaseModel):
    """Result completion summary for a single class."""
    class_id: int
    class_name: str
    class_code: str
    academic_year: str
    students_count: int
    subjects_count: int
    complete_subjects_count: int = 0
    pending_subjects_count: int = 0
    released_subjects_count: int = 0
    submitted_subjects_count: int = 0
    progress_percent: int = 0
    expected_results: int
    submitted_results: int
    pending_results: int
    approved_results: int
    released_results: int
    viewed_results: int
    status: str  # "COMPLETE", "PARTIAL", "PENDING", "REVIEW", "APPROVED", "RELEASED"


class ClassSubjectMatrixItem(BaseModel):
    """Detailed result status for a class subject."""
    subject_id: int
    subject_name: str
    subject_code: str
    teacher_id: Optional[int] = None
    teacher_name: Optional[str] = None
    teacher_email: Optional[str] = None
    exam_id: Optional[int] = None
    submission_id: Optional[int] = None
    status: str  # "NOT_STARTED", "DRAFT", "PARTIAL", "SUBMITTED", "RETURNED", "COMPLETE", "APPROVED", "RELEASED"
    release_status: str = "NOT RELEASED"  # "RELEASED", "NOT RELEASED"
    is_complete: bool = False
    expected_students: int = 0
    attended_students: int = 0
    marks_entered: int = 0
    marks_submitted: int = 0
    marks_approved: int = 0
    marks_released: int = 0
    pending_students: int = 0
    absent_students: int = 0
    submitted_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    return_reason: Optional[str] = None


class StudentSubjectScoreItem(BaseModel):
    """Subject score for a student in class matrix."""
    subject_id: int
    subject_name: str
    subject_code: str
    attendance_status: str = "PRESENT"
    marks_obtained: Optional[Decimal] = None
    max_marks: Decimal = Decimal("100.00")
    pass_marks: Decimal = Decimal("50.00")
    grade: Optional[str] = None
    remarks: Optional[str] = None
    status: str = "DRAFT"  # "DRAFT", "SUBMITTED", "APPROVED", "RELEASED"


class ClassStudentMatrixRow(BaseModel):
    """Row in class student matrix with all subject scores."""
    student_id: int
    admission_number: str
    student_name: str
    roll_number: Optional[str] = None
    gender: Optional[str] = None
    scores: dict = {}  # { str(subject_id): StudentSubjectScoreItem }
    total_marks: Optional[Decimal] = None
    average_marks: Optional[Decimal] = None
    passed_all: bool = True


class ClassResultDashboardResponse(BaseModel):
    """Comprehensive Class Result Dashboard response."""
    class_id: int
    class_name: str
    academic_year: str
    exam_name: str
    students_count: int
    subjects_count: int
    complete_subjects_count: int = 0
    pending_subjects_count: int = 0
    released_subjects_count: int = 0
    not_released_subjects_count: int = 0
    expected_results: int
    submitted_results: int
    pending_results: int
    approved_results: int
    released_results: int
    viewed_results: int
    status: str
    subjects_matrix: List[ClassSubjectMatrixItem]
    student_matrix: List[ClassStudentMatrixRow] = []
    can_release_full: bool
    can_release_partial: bool
    release_batch_code: Optional[str] = None
    released_at: Optional[datetime] = None


class TeacherSubmissionItem(BaseModel):
    """Submission item for Admin Teacher Submissions Monitoring."""
    id: int
    teacher_id: Optional[int] = None
    teacher_name: str = "Unassigned"
    teacher_number: Optional[str] = None
    subject_id: int
    subject_name: str
    subject_code: Optional[str] = None
    class_id: int
    class_name: str
    class_section: Optional[str] = None
    exam_id: int
    exam_name: str
    exam_type: Optional[str] = None
    exam_status: Optional[str] = None
    academic_year: str
    expected_students: int
    completed_students: int
    pending_students: int
    absent_students: int = 0
    present_students: int = 0
    complaints_count: int = 0
    status: str  # "DRAFT", "PARTIAL", "SUBMITTED", "APPROVED", "RETURNED", "RELEASED"
    submitted_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    returned_at: Optional[datetime] = None
    return_reason: Optional[str] = None
    submission_deadline: Optional[datetime] = None
    is_overdue: bool = False
    deadline_status: str = "ON_TRACK"  # "ON_TRACK", "APPROACHING", "OVERDUE", "CLOSED", "EXTENDED"
    completion_percentage: float = 0.0
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    instructions: Optional[str] = None
    revisions: Optional[List[dict]] = None


class TeacherAccountabilitySummary(BaseModel):
    """Summary of teacher result responsibilities."""
    teacher_id: int
    teacher_name: str
    teacher_number: Optional[str] = None
    total_assigned: int
    submitted: int
    partial: int
    pending: int
    approved: int
    returned: int
    released: int


class StudentMarkItem(BaseModel):
    """Individual student mark, grade, and attendance entry."""
    student_id: int
    admission_number: str
    student_name: str
    roll_number: Optional[str] = None
    gender: Optional[str] = None
    attendance_status: str = "PRESENT"  # "PRESENT", "ABSENT", "EXCUSED"
    absence_reason: Optional[str] = None
    complaint: Optional[str] = None
    marks_obtained: Optional[Decimal] = None
    max_marks: Decimal = Decimal("100.00")
    pass_marks: Decimal = Decimal("50.00")
    grade: Optional[str] = None
    remarks: Optional[str] = None
    status: str = "DRAFT"  # "DRAFT", "SUBMITTED", "APPROVED", "RELEASED"
    paper_file_path: Optional[str] = None
    paper_original_name: Optional[str] = None


class SubmissionReviewDetail(BaseModel):
    """Detail view for Admin reviewing a teacher's submission."""
    id: int
    exam_id: int
    exam_name: str
    exam_type: Optional[str] = None
    academic_year: str
    class_id: int
    class_name: str
    class_section: Optional[str] = None
    subject_id: int
    subject_name: str
    teacher_id: int
    teacher_name: str
    status: str
    expected_students: int
    completed_students: int
    pending_students: int
    absent_students: int = 0
    present_students: int = 0
    sat_exam_students: int = 0
    missing_marks_students: int = 0
    recorded_absence_reasons_count: int = 0
    complaints_count: int = 0
    pass_marks: Decimal = Decimal("50.00")
    max_marks: Decimal = Decimal("100.00")
    is_complete: bool = False
    submitted_at: Optional[datetime] = None
    returned_at: Optional[datetime] = None
    return_reason: Optional[str] = None
    revisions: Optional[List[dict]] = None
    students: List[StudentMarkItem]


class ReleaseSubmissionPayload(BaseModel):
    """Admin submission release payload."""
    notes: Optional[str] = None


class StudentMarkEntryInput(BaseModel):
    """Input entry when teacher saves draft or submits."""
    student_id: int
    attendance_status: str = Field(default="PRESENT", pattern="^(PRESENT|ABSENT|EXCUSED)$")
    marks_obtained: Optional[Decimal] = Field(default=None, ge=0)
    absence_reason: Optional[str] = None
    complaint: Optional[str] = None
    remarks: Optional[str] = None


class TeacherSaveDraftPayload(BaseModel):
    """Teacher draft save payload."""
    exam_id: int
    class_id: int
    subject_id: int
    marks: List[StudentMarkEntryInput]


class TeacherSubmitPayload(BaseModel):
    """Teacher formal submit payload to Admin."""
    exam_id: int
    class_id: int
    subject_id: int
    marks: List[StudentMarkEntryInput]
    notes: Optional[str] = None


class ReturnSubmissionPayload(BaseModel):
    """Admin returning submission for correction."""
    reason: str = Field(..., min_length=3, description="Detailed explanation of what needs review/correction.")


class ApproveSubmissionPayload(BaseModel):
    """Admin approval payload."""
    notes: Optional[str] = None


class ReleaseClassResultsPayload(BaseModel):
    """Admin class result publication payload."""
    academic_year: str
    exam_name: str
    class_id: Optional[int] = None
    release_type: str = Field(default="FULL", pattern="^(FULL|PARTIAL)$")
    notes: Optional[str] = None


class StudentReceiptStatusItem(BaseModel):
    """Receipt and visibility status for a single student."""
    student_id: int
    admission_number: str
    student_name: str
    class_name: str
    status: str  # "NOT_RELEASED", "RELEASED", "VIEWED"
    release_batch_code: Optional[str] = None
    released_at: Optional[datetime] = None
    first_viewed_at: Optional[datetime] = None
    last_viewed_at: Optional[datetime] = None
    view_count: int = 0


class ClassReceiptSummary(BaseModel):
    """Receipt summary for a class release."""
    class_id: int
    class_name: str
    exam_name: str
    academic_year: str
    total_students: int
    released_students: int
    viewed_students: int
    not_viewed_students: int
    receipts: List[StudentReceiptStatusItem]


class TeacherExamAssignmentItem(BaseModel):
    """An assigned exam stream for a teacher."""
    exam_id: int
    exam_name: str
    exam_type: str
    academic_year: str
    class_id: int
    class_name: str
    class_code: str
    class_section: Optional[str] = None
    subject_id: int
    subject_name: str
    subject_code: str
    start_date: Optional[date] = None
    result_submission_deadline: Optional[datetime] = None
    is_overdue: bool = False
    deadline_status: str = "ON_TRACK"
    remaining_time_human: Optional[str] = None
    max_marks: Decimal
    pass_marks: Decimal
    submission_id: Optional[int] = None
    status: str  # "NOT_STARTED", "DRAFT", "PARTIAL", "READY_TO_SUBMIT", "SUBMITTED", "RETURNED", "APPROVED", "RELEASED"
    expected_students: int
    completed_students: int
    pending_students: int
    absent_students: int = 0
    complaints_count: int = 0
    submitted_at: Optional[datetime] = None
    returned_at: Optional[datetime] = None
    return_reason: Optional[str] = None
    revisions: Optional[List[dict]] = None


class RecordStudentViewPayload(BaseModel):
    """Payload to record student view event."""
    exam_name: str
    academic_year: str
    class_id: Optional[int] = None
