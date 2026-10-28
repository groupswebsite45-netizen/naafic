from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field


class StudentPromotionOverrideItem(BaseModel):
    """Specific override action for an individual student within a batch or class promotion."""
    student_id: int
    action: str = Field(..., description="PROMOTE, REPEAT, TRANSFER, GRADUATE, EXCLUDE")
    target_class_id: Optional[int] = None
    reason: Optional[str] = None


class ClassPromotionMappingItem(BaseModel):
    """Mapping from a source class to a destination class for promotion."""
    from_class_id: int
    to_class_id: Optional[int] = None  # None indicates graduate / leave class / no automatic promotion
    action: str = Field("PROMOTE", description="PROMOTE, GRADUATE, or NO_CHANGE")


class ClassPromotionMappingSuggestion(BaseModel):
    from_class_id: int
    from_class_name: str
    from_class_code: str
    education_level: Optional[str] = "PRIMARY"  # PRIMARY or SECONDARY
    level_name: Optional[str] = None           # e.g., "Grade 4", "Form 1"
    level_number: Optional[int] = None          # e.g., 4, 1
    section: Optional[str] = None               # e.g., "A", "B", "C"
    to_class_id: Optional[int] = None
    to_class_name: Optional[str] = None
    to_class_code: Optional[str] = None
    action: str = "PROMOTE"
    student_count: int = 0
    is_terminal_class: bool = False             # e.g., Grade 8 (Primary) or Form 4 (Secondary)
    missing_destination_warning: bool = False
    warning_message: Optional[str] = None


class TargetClassOption(BaseModel):
    id: int
    name: str
    code: str
    division: Optional[str] = "PRIMARY"
    level: Optional[str] = None
    section: Optional[str] = None
    academic_year: str
    capacity: int
    enrolled_count: int = 0
    status: str


class SuggestedMappingsResponse(BaseModel):
    source_academic_year: str
    target_academic_year: str
    education_level: Optional[str] = None  # PRIMARY, SECONDARY, or None
    mappings: List[ClassPromotionMappingSuggestion]
    available_target_classes: List[TargetClassOption]
    academic_years: List[str]


class PromotionPreviewRequest(BaseModel):
    source_academic_year: str
    target_academic_year: str
    education_level: Optional[str] = None
    mappings: List[ClassPromotionMappingItem]
    student_overrides: Optional[List[StudentPromotionOverrideItem]] = None


class StudentPromotionPreviewItem(BaseModel):
    student_id: int
    admission_number: str
    student_name: str
    gender: Optional[str] = None
    education_level: Optional[str] = "PRIMARY"
    current_class_id: int
    current_class_name: str
    current_section: Optional[str] = None
    target_class_id: Optional[int] = None
    target_class_name: Optional[str] = None
    target_section: Optional[str] = None
    source_academic_year: Optional[str] = None
    target_academic_year: Optional[str] = None
    action: str  # PROMOTED, REPEATED, TRANSFERRED, GRADUATED, EXCLUDED, SKIPPED
    status: str  # READY, VALIDATION_ERROR, ALREADY_ENROLLED, GRADUATING, REPEATING, EXCLUDED
    is_valid: bool = True
    validation_message: Optional[str] = None


class ClassMappingPreviewSummary(BaseModel):
    from_class_id: int
    from_class_name: str
    from_class_code: str
    education_level: Optional[str] = "PRIMARY"
    section: Optional[str] = None
    to_class_id: Optional[int] = None
    to_class_name: Optional[str] = None
    to_class_code: Optional[str] = None
    action: str
    students_count: int
    valid_count: int
    error_count: int
    warning_message: Optional[str] = None


class BulkPromotionPreviewResponse(BaseModel):
    source_academic_year: str
    target_academic_year: str
    education_level: Optional[str] = None
    total_students_affected: int
    total_to_promote: int
    total_to_repeat: int = 0
    total_to_graduate: int = 0
    total_excluded: int = 0
    total_validation_errors: int = 0
    missing_destination_classes_count: int = 0
    can_execute: bool
    class_summaries: List[ClassMappingPreviewSummary]
    student_previews: List[StudentPromotionPreviewItem]
    validation_errors: List[str]


class ExecuteBulkPromotionPayload(BaseModel):
    source_academic_year: str
    target_academic_year: str
    education_level: Optional[str] = None
    mappings: List[ClassPromotionMappingItem]
    student_overrides: Optional[List[StudentPromotionOverrideItem]] = None
    reason: Optional[str] = "Annual Academic Promotion"


class IndividualClassChangePayload(BaseModel):
    new_class_id: int
    academic_year: str
    reason: Optional[str] = None
    is_promotion: Optional[bool] = False
    preserve_history: Optional[bool] = True


class IndividualClassChangeResponse(BaseModel):
    message: str
    student_id: int
    student_name: str
    old_class_name: Optional[str]
    new_class_name: str
    academic_year: str
    enrollment_id: int
    batch_code: Optional[str] = None
    timestamp: datetime


class ClassLevelPromotionPayload(BaseModel):
    from_class_id: int
    to_class_id: Optional[int] = None
    source_academic_year: str
    target_academic_year: str
    action: str = "PROMOTE"  # PROMOTE, GRADUATE
    student_ids: Optional[List[int]] = None  # None means all active students in from_class
    student_overrides: Optional[List[StudentPromotionOverrideItem]] = None
    reason: Optional[str] = "Class-Level Promotion"


class IndividualStudentPromotionPayload(BaseModel):
    student_id: int
    source_academic_year: str
    target_academic_year: str
    action: str = Field("PROMOTE", description="PROMOTE, REPEAT, TRANSFER, GRADUATE, EXCLUDE")
    target_class_id: Optional[int] = None
    reason: Optional[str] = "Individual Student Promotion"


class StudentSearchForPromotionItem(BaseModel):
    student_id: int
    admission_number: str
    student_name: str
    gender: Optional[str] = None
    current_class_id: Optional[int] = None
    current_class_name: Optional[str] = None
    current_division: Optional[str] = None
    current_level: Optional[str] = None
    current_section: Optional[str] = None
    current_academic_year: Optional[str] = None
    status: str
    suggested_next_class_id: Optional[int] = None
    suggested_next_class_name: Optional[str] = None
    is_terminal: bool = False


class PromotionRecordItemResponse(BaseModel):
    id: int
    batch_id: int
    student_id: int
    student_name: str
    admission_number: str
    from_class_name: Optional[str] = None
    to_class_name: Optional[str] = None
    source_academic_year: str
    target_academic_year: str
    action: str
    status: str
    reason: Optional[str] = None
    created_at: datetime


class PromotionBatchResponse(BaseModel):
    id: int
    batch_code: str
    source_academic_year: str
    target_academic_year: str
    promotion_type: str
    status: str
    total_promoted: int
    total_graduated: int
    total_skipped: int
    reason: Optional[str] = None
    created_by_name: Optional[str] = None
    created_at: datetime
    records_count: int
    records: Optional[List[PromotionRecordItemResponse]] = None


class BatchRollbackResponse(BaseModel):
    success: bool
    message: str
    batch_code: str
    restored_students_count: int

