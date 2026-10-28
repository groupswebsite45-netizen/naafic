from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session
from app.api.dependencies.database import get_db
from app.api.dependencies.auth import get_current_active_admin, get_current_user
from app.models.user import User
from app.services.timetable_service import TimetableService
from app.schemas.timetable import (
    TimetableCreate,
    TimetableUpdate,
    TimetableResponse,
    TimetableSummary,
    TimetableFilterOptions,
    TimetableCheckConflictPayload,
    TimetableConflictCheckResponse,
    TimetableGenerateRequest,
    TimetableGenerateResponse,
    TimetablePublishRequest,
    TimetablePublishResponse,
    TimetableClassOverviewResponse,
    TimetableBatchSaveRequest,
    TimetableConflictDetail,
    TimetableMoveSlotRequest,
    TimetableSwapSlotsRequest
)
from app.schemas.timetable_setting import (
    TimetableSettingCreate,
    TimetableSettingUpdate,
    TimetableSettingResponse
)
from app.schemas.teacher_availability import (
    TeacherAvailabilityCreate,
    TeacherAvailabilityUpdate,
    TeacherAvailabilityResponse,
    TeacherAvailabilityMatrixItem
)

router = APIRouter(prefix="/timetable", tags=["Timetable"])


@router.get(
    "/summary",
    response_model=TimetableSummary,
    summary="Get aggregated timetable statistics and conflict audit from PostgreSQL"
)
def get_timetable_summary(
    academic_year: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = TimetableService(db)
    return service.get_summary(academic_year=academic_year)


@router.get(
    "/filter-options",
    response_model=TimetableFilterOptions,
    summary="Get available filter options for timetable from PostgreSQL"
)
def get_filter_options(
    academic_year: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = TimetableService(db)
    return service.get_filter_options(academic_year=academic_year)


@router.post(
    "/check-conflict",
    response_model=TimetableConflictCheckResponse,
    summary="Check if a proposed timetable slot conflicts with existing entries"
)
def check_timetable_conflict(
    payload: TimetableCheckConflictPayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = TimetableService(db)
    return service.check_slot_conflict(payload)


@router.get(
    "/class-overview/{class_id}",
    response_model=TimetableClassOverviewResponse,
    summary="Get comprehensive class-first timetable overview with authorized assignments and publication status"
)
@router.get(
    "/class/{class_id}",
    response_model=TimetableClassOverviewResponse,
    include_in_schema=False
)
def get_class_timetable_overview(
    class_id: int,
    academic_year: Optional[str] = Query(None, description="Academic year (e.g. 2026/2027)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = TimetableService(db)
    return service.get_class_timetable_overview(class_id=class_id, academic_year=academic_year or "2026/2027")


@router.post(
    "/generate",
    response_model=TimetableGenerateResponse,
    summary="Automatically generate a class timetable using constraint-satisfaction engine (Admin only)"
)
def generate_class_timetable(
    payload: TimetableGenerateRequest,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = TimetableService(db)
    return service.generate_class_timetable(payload, user_id=current_admin.id)


@router.post(
    "/publish",
    response_model=TimetablePublishResponse,
    summary="Publish timetable schedule after conflict auditing (Admin only)"
)
def publish_timetable(
    payload: TimetablePublishRequest,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = TimetableService(db)
    return service.publish_timetable(payload, user_id=current_admin.id)


@router.post(
    "/unpublish",
    response_model=TimetablePublishResponse,
    summary="Unpublish timetable schedule for corrections (Admin only)"
)
def unpublish_timetable(
    payload: Optional[TimetablePublishRequest] = None,
    class_id: Optional[int] = Query(None),
    academic_year: Optional[str] = Query(None),
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = TimetableService(db)
    target_class_id = (payload.class_id if payload else None) or class_id
    target_year = (payload.academic_year if payload else None) or academic_year or "2026/2027"
    return service.unpublish_timetable(class_id=target_class_id, academic_year=target_year, user_id=current_admin.id)


@router.post(
    "/batch-save",
    response_model=List[TimetableResponse],
    summary="Atomically save edited weekly grid slots for a class (Admin only)"
)
@router.post(
    "/batch",
    response_model=List[TimetableResponse],
    include_in_schema=False
)
def batch_save_timetable(
    payload: TimetableBatchSaveRequest,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = TimetableService(db)
    return service.batch_save_class_timetable(payload, user_id=current_admin.id)


@router.post(
    "/move-slot",
    response_model=TimetableResponse,
    summary="Move a timetable lesson card to a new day/time with conflict validation (Admin only)"
)
def move_timetable_slot(
    payload: TimetableMoveSlotRequest,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = TimetableService(db)
    return service.move_slot(payload, user_id=current_admin.id)


@router.post(
    "/swap-slots",
    response_model=List[TimetableResponse],
    summary="Atomically swap two timetable slots with dual conflict validation (Admin only)"
)
def swap_timetable_slots(
    payload: TimetableSwapSlotsRequest,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = TimetableService(db)
    return service.swap_slots(payload, user_id=current_admin.id)



@router.get(
    "/settings",
    response_model=TimetableSettingResponse,
    summary="Get timetable schedule configuration (school hours, period duration, breaks)"
)
def get_timetable_settings(
    academic_year: Optional[str] = Query(None),
    division: Optional[str] = Query("ALL"),
    education_level: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = TimetableService(db)
    return service.get_timetable_setting(academic_year=academic_year or "2026/2027", division=education_level or division or "ALL")


@router.put(
    "/settings/{setting_id}",
    response_model=TimetableSettingResponse,
    summary="Update timetable schedule configuration (Admin only)"
)
def update_timetable_settings(
    setting_id: int,
    payload: TimetableSettingUpdate,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = TimetableService(db)
    return service.update_timetable_setting(setting_id=setting_id, payload=payload, user_id=current_admin.id)


@router.get(
    "/teacher-availability/{teacher_id}",
    response_model=List[TeacherAvailabilityResponse],
    summary="Get teacher availability configuration by path"
)
@router.get(
    "/teacher-availability",
    response_model=List[TeacherAvailabilityResponse],
    include_in_schema=False
)
def get_teacher_availability(
    teacher_id: Optional[int] = None,
    academic_year: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = TimetableService(db)
    return service.get_teacher_availabilities(teacher_id=teacher_id or 1, academic_year=academic_year or "2026/2027")


@router.post(
    "/teacher-availability",
    summary="Set or update teacher availability preferences (Admin only)"
)
def set_teacher_availability(
    payload: TeacherAvailabilityCreate,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = TimetableService(db)
    return service.set_teacher_availability(payload, user_id=current_admin.id)


@router.get(
    "/teacher-availability/matrix",
    summary="Get school-wide faculty availability matrix showing occupied and free periods"
)
@router.get(
    "/teacher-availability-matrix",
    include_in_schema=False
)
@router.get(
    "/teacher-matrix",
    include_in_schema=False
)
def get_teacher_availability_matrix(
    academic_year: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = TimetableService(db)
    return service.get_teacher_availability_matrix(academic_year=academic_year or "2026/2027")


@router.get(
    "/validate",
    summary="Run comprehensive 10-point conflict validation for class or entire school"
)
def validate_timetable(
    academic_year: Optional[str] = Query(None),
    class_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = TimetableService(db)
    target_year = academic_year or "2026/2027"
    if class_id:
        conflicts = service.conflict_service.validate_class_schedule(class_id=class_id, academic_year=target_year)
    else:
        conflicts = service.repo.detect_all_conflicts(academic_year=target_year)
    has_critical = any(getattr(c, "severity", "WARNING") == "CRITICAL" for c in conflicts)
    return {
        "is_valid": not has_critical,
        "total_conflicts": len(conflicts),
        "critical_conflicts": sum(1 for c in conflicts if getattr(c, "severity", "WARNING") == "CRITICAL"),
        "warning_conflicts": sum(1 for c in conflicts if getattr(c, "severity", "WARNING") == "WARNING"),
        "conflicts": conflicts
    }


@router.get(
    "/pdf/class/{class_id}",
    summary="Download print-ready official class timetable PDF"
)
@router.get(
    "/class/{class_id}/pdf",
    include_in_schema=False
)
def download_class_pdf(
    class_id: int,
    academic_year: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = TimetableService(db)
    target_year = academic_year or "2026/2027"
    pdf_bytes = service.generate_class_pdf(class_id=class_id, academic_year=target_year)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="timetable_class_{class_id}_{target_year.replace("/", "_")}.pdf"'}
    )


@router.get(
    "/pdf/teacher/{teacher_id}",
    summary="Download print-ready faculty teaching timetable PDF"
)
@router.get(
    "/teacher/{teacher_id}/pdf",
    include_in_schema=False
)
def download_teacher_pdf(
    teacher_id: int,
    academic_year: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = TimetableService(db)
    target_year = academic_year or "2026/2027"
    pdf_bytes = service.generate_teacher_pdf(teacher_id=teacher_id, academic_year=target_year)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="timetable_teacher_{teacher_id}_{target_year.replace("/", "_")}.pdf"'}
    )


@router.get(
    "",
    response_model=List[TimetableResponse],
    summary="List and search timetable entries"
)
def list_timetable(
    class_id: Optional[int] = None,
    teacher_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    day_of_week: Optional[str] = None,
    academic_year: Optional[str] = None,
    room: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = TimetableService(db)
    entries, _ = service.search_entries(
        class_id=class_id,
        teacher_id=teacher_id,
        subject_id=subject_id,
        day_of_week=day_of_week,
        academic_year=academic_year,
        room=room,
        status_filter=status,
        skip=skip,
        limit=limit
    )
    return entries


@router.get(
    "/{entry_id}",
    response_model=TimetableResponse,
    summary="Get timetable slot by ID"
)
def get_entry(
    entry_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = TimetableService(db)
    entry = service.get_entry(entry_id)
    return service._format_response(entry)


@router.post(
    "",
    response_model=TimetableResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a timetable slot with conflict check (Admin only)"
)
def create_entry(
    payload: TimetableCreate,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = TimetableService(db)
    return service.create_entry(payload, user_id=current_admin.id)


@router.put(
    "/{entry_id}",
    response_model=TimetableResponse,
    summary="Update timetable slot with conflict check (Admin only)"
)
def update_entry(
    entry_id: int,
    payload: TimetableUpdate,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = TimetableService(db)
    return service.update_entry(entry_id, payload, user_id=current_admin.id)


@router.delete(
    "/{entry_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete timetable slot (Admin only)"
)
def delete_entry(
    entry_id: int,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = TimetableService(db)
    service.delete_entry(entry_id, user_id=current_admin.id)
    return {"message": "Timetable slot deleted successfully."}
