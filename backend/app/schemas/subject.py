from datetime import date, datetime, time
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class SubjectBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    code: str = Field(..., min_length=2, max_length=50)
    division: str = Field(default="ALL", description="PRIMARY, SECONDARY, ALL")
    applicable_levels: Optional[str] = Field(default=None, description="Comma-separated levels e.g. 'Grade 1,Grade 2' or 'Form 1,Form 2'")
    department: Optional[str] = None
    description: Optional[str] = None
    status: str = Field(default="ACTIVE")


class SubjectCreate(SubjectBase):
    pass


class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    division: Optional[str] = None
    applicable_levels: Optional[str] = None
    department: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class SubjectStatusUpdate(BaseModel):
    status: str
    reason: Optional[str] = None


class SubjectResponse(SubjectBase):
    id: int
    created_at: datetime
    updated_at: datetime
    classes_count: int = 0
    teachers_count: int = 0
    timetables_count: int = 0
    exams_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class SubjectSummary(BaseModel):
    total_subjects: int
    active_subjects: int
    assigned_subjects: int
    unassigned_subjects: int
    departments_count: int


class SubjectClassAssignmentItem(BaseModel):
    id: int
    class_id: int
    class_name: str
    class_code: str
    section: Optional[str] = None
    academic_year: str
    teacher_id: Optional[int] = None
    teacher_name: Optional[str] = None
    students_count: int = 0
    status: str = "ACTIVE"

    model_config = ConfigDict(from_attributes=True)


class SubjectTeacherAssignmentItem(BaseModel):
    id: int
    teacher_id: int
    teacher_number: str
    full_name: str
    class_id: int
    class_name: str
    academic_year: str
    status: str = "ACTIVE"

    model_config = ConfigDict(from_attributes=True)


class SubjectTimetableItem(BaseModel):
    id: int
    day_of_week: str
    start_time: time
    end_time: time
    class_name: str
    class_code: str
    teacher_name: Optional[str] = None
    room: Optional[str] = None
    status: str = "ACTIVE"

    model_config = ConfigDict(from_attributes=True)


class SubjectExamItem(BaseModel):
    id: int
    name: str
    exam_type: str
    class_name: str
    academic_year: str
    start_date: Optional[date] = None
    max_marks: float = 100.0
    status: str = "SCHEDULED"

    model_config = ConfigDict(from_attributes=True)


class SubjectAssignClassPayload(BaseModel):
    class_id: int
    academic_year: str
    teacher_id: Optional[int] = None


class SubjectAssignTeacherPayload(BaseModel):
    teacher_id: int
    class_id: int
    academic_year: str


class SubjectFullProfileResponse(SubjectResponse):
    classes: List[SubjectClassAssignmentItem] = []
    teachers: List[SubjectTeacherAssignmentItem] = []
    timetables: List[SubjectTimetableItem] = []
    exams: List[SubjectExamItem] = []

    model_config = ConfigDict(from_attributes=True)
