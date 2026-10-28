from datetime import time, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.school_class import SchoolClassResponse
from app.schemas.subject import SubjectResponse
from app.schemas.teacher import TeacherResponse


class TimetableBase(BaseModel):
    class_id: int
    subject_id: int
    teacher_id: Optional[int] = None
    academic_year: str = Field(..., min_length=4, max_length=50)
    day_of_week: str = Field(..., description="Saturday, Sunday, Monday, Tuesday, Wednesday, Thursday, Friday")
    start_time: time
    end_time: time
    room: Optional[str] = None
    period_number: Optional[int] = None
    is_break: bool = Field(default=False)
    status: str = Field(default="ACTIVE")  # DRAFT, GENERATED, PUBLISHED, ACTIVE, ARCHIVED


class TimetableCreate(TimetableBase):
    pass


class TimetableUpdate(BaseModel):
    class_id: Optional[int] = None
    subject_id: Optional[int] = None
    teacher_id: Optional[int] = None
    academic_year: Optional[str] = None
    day_of_week: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    room: Optional[str] = None
    period_number: Optional[int] = None
    is_break: Optional[bool] = None
    status: Optional[str] = None


class TimetableResponse(BaseModel):
    id: int
    class_id: int
    subject_id: int
    teacher_id: Optional[int] = None
    academic_year: str
    day_of_week: str
    start_time: time
    end_time: time
    room: Optional[str] = None
    period_number: Optional[int] = None
    is_break: bool = False
    status: str
    published_at: Optional[datetime] = None
    published_by_id: Optional[int] = None
    
    # Flat convenience fields for portals and UI cards
    class_name: Optional[str] = None
    class_code: Optional[str] = None
    subject_name: Optional[str] = None
    subject_code: Optional[str] = None
    teacher_name: Optional[str] = None
    room_number: Optional[str] = None

    school_class: Optional[SchoolClassResponse] = None
    subject: Optional[SubjectResponse] = None
    teacher: Optional[TeacherResponse] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TimetableConflictDetail(BaseModel):
    conflict_type: str  # "CLASS", "TEACHER", "ROOM", "BREAK", "OUTSIDE_HOURS", "UNAVAILABLE"
    message: str
    conflicting_slot_id: Optional[int] = None
    day_of_week: str
    start_time: str
    end_time: str
    class_name: str
    teacher_name: Optional[str] = None
    room: Optional[str] = None
    subject_name: Optional[str] = None
    severity: str = "ERROR"  # "ERROR", "WARNING"


class TimetableSummary(BaseModel):
    total_periods: int
    scheduled_classes: int
    assigned_teachers: int
    active_rooms: int
    conflicts_count: int
    conflicts: List[TimetableConflictDetail] = Field(default_factory=list)


class TimetableFilterOptions(BaseModel):
    academic_years: List[str]
    days_of_week: List[str]
    rooms: List[str]


class TimetableCheckConflictPayload(BaseModel):
    class_id: int
    subject_id: int
    teacher_id: Optional[int] = None
    academic_year: str
    day_of_week: str
    start_time: time
    end_time: time
    room: Optional[str] = None
    exclude_id: Optional[int] = None


class TimetableConflictCheckResponse(BaseModel):
    has_conflict: bool
    conflicts_count: int
    conflicts: List[TimetableConflictDetail] = Field(default_factory=list)


class SubjectRequirement(BaseModel):
    subject_id: int
    subject_name: str
    teacher_id: Optional[int] = None
    teacher_name: Optional[str] = None
    periods_per_week: int = Field(default=4, ge=1, le=10)


class TimetableGenerateRequest(BaseModel):
    class_id: int
    academic_year: str
    school_days: Optional[List[str]] = None
    start_time: Optional[Any] = None
    end_time: Optional[Any] = None
    period_duration_minutes: Optional[int] = None
    periods_per_day: Optional[int] = None
    break_after_period: Optional[int] = None
    break_duration_minutes: Optional[int] = None
    lunch_after_period: Optional[int] = None
    lunch_duration_minutes: Optional[int] = None
    default_room: Optional[str] = None
    subject_requirements: Optional[List[SubjectRequirement]] = None
    subject_lessons_distribution: Optional[dict] = None
    respect_teacher_availability: bool = True
    replace_existing: bool = True
    overwrite_existing: Optional[bool] = None


class TimetableGenerateResponse(BaseModel):
    success: bool
    class_id: int
    class_name: str
    academic_year: str
    total_generated_periods: int
    total_slots_generated: Optional[int] = None
    generated_entries: List[TimetableResponse] = Field(default_factory=list)
    slots: Optional[List[TimetableResponse]] = None
    conflicts: List[TimetableConflictDetail] = Field(default_factory=list)
    unassigned_requirements: List[Any] = Field(default_factory=list)
    unplaced_subjects: Optional[List[Any]] = None
    message: str


class TimetablePublishRequest(BaseModel):
    class_id: Optional[int] = None  # publish for specific class or all if None
    academic_year: str
    force: bool = False  # cannot publish with critical errors unless forced if allowed


class TimetablePublishResponse(BaseModel):
    success: bool
    published_count: int
    academic_year: str
    message: str
    conflicts_found: int = 0
    conflicts: List[TimetableConflictDetail] = Field(default_factory=list)


class TimetableAuthorizedFaculty(BaseModel):
    assignment_id: Optional[int] = None
    subject_id: int
    subject_name: str
    subject_code: str
    teacher_id: Optional[int] = None
    teacher_name: Optional[str] = None
    teacher_number: Optional[str] = None
    recommended_weekly_periods: int = 4


class TimetableClassOverviewResponse(BaseModel):
    class_id: int
    class_name: str
    class_code: str
    division: str
    level: str
    section: str
    academic_year: str
    capacity: int
    enrolled_students: int
    authorized_assignments: List[TimetableAuthorizedFaculty] = Field(default_factory=list)
    assigned_subjects: Optional[List[Any]] = None
    has_assignments: bool
    timetables: List[TimetableResponse] = Field(default_factory=list)
    existing_slots: Optional[List[TimetableResponse]] = None
    publication_status: str = "DRAFT"  # "DRAFT", "PUBLISHED", "EMPTY"
    total_periods: int = 0
    total_slots: Optional[int] = None
    published_slots: Optional[int] = None
    has_unresolved_conflicts: Optional[bool] = None
    conflicts_count: int = 0
    conflicts: List[TimetableConflictDetail] = Field(default_factory=list)


class TimetableBatchSaveRequest(BaseModel):
    class_id: int
    academic_year: str
    slots: List[TimetableCreate]
    publish_immediately: bool = False


class TimetableMoveSlotRequest(BaseModel):
    slot_id: int
    target_day: str
    target_period_number: Optional[int] = None
    target_start_time: time
    target_end_time: time
    target_room: Optional[str] = None


class TimetableSwapSlotsRequest(BaseModel):
    slot_id_1: int
    slot_id_2: int

