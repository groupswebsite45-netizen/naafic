from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.database import get_db
from app.api.dependencies.auth import get_current_active_admin
from app.models.user import User
from app.services.form_master_service import FormMasterAdminService
from app.schemas.form_master import (
    FormMasterAppointPayload,
    FormMasterReplacePayload,
    FormMasterRevokePayload,
    FormMasterAssignmentResponse,
    ClassFormMasterItem,
    AvailableTeacherItem,
    FormMasterAdminOverview,
)

router = APIRouter(prefix="/form-masters", tags=["Admin Form Master Management"])


@router.get(
    "/overview",
    response_model=FormMasterAdminOverview,
    summary="Get overall Form Master assignment statistics (Admin only)"
)
def get_form_master_overview(
    academic_year: Optional[str] = Query(None, description="Optional academic year filter"),
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = FormMasterAdminService(db)
    return service.get_overview(academic_year=academic_year)


@router.get(
    "/classes",
    response_model=List[ClassFormMasterItem],
    summary="List all classes and their Form Master status (Admin only)"
)
def list_classes_with_form_masters(
    academic_year: Optional[str] = Query(None, description="Filter by academic year"),
    division: Optional[str] = Query(None, description="Filter by division: PRIMARY, SECONDARY, or ALL"),
    status: Optional[str] = Query(None, description="Filter: ASSIGNED, UNASSIGNED, or None"),
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = FormMasterAdminService(db)
    return service.list_classes_with_form_masters(
        academic_year=academic_year,
        division=division,
        status_filter=status
    )


@router.get(
    "/available-teachers",
    response_model=List[AvailableTeacherItem],
    summary="List teachers with their current active Form Master workload (Admin only)"
)
def list_available_teachers(
    academic_year: Optional[str] = Query(None, description="Filter by academic year"),
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = FormMasterAdminService(db)
    return service.list_available_teachers(academic_year=academic_year)


@router.post(
    "/appoint",
    response_model=List[FormMasterAssignmentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Appoint a teacher as Form Master for one or two specific classes (Admin only)"
)
def appoint_form_master(
    payload: FormMasterAppointPayload,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = FormMasterAdminService(db)
    return service.appoint_form_master(payload, current_admin)


@router.post(
    "/{assignment_id}/replace",
    response_model=FormMasterAssignmentResponse,
    summary="Replace current Form Master with a new teacher (Admin only)"
)
def replace_form_master(
    assignment_id: int,
    payload: FormMasterReplacePayload,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = FormMasterAdminService(db)
    return service.replace_form_master(assignment_id, payload, current_admin)


@router.post(
    "/{assignment_id}/revoke",
    response_model=FormMasterAssignmentResponse,
    summary="Revoke an active Form Master appointment (Admin only)"
)
def revoke_form_master(
    assignment_id: int,
    payload: FormMasterRevokePayload,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = FormMasterAdminService(db)
    return service.revoke_form_master(assignment_id, payload, current_admin)


@router.get(
    "/{assignment_id}",
    response_model=FormMasterAssignmentResponse,
    summary="Get single Form Master assignment details (Admin only)"
)
def get_assignment_detail(
    assignment_id: int,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = FormMasterAdminService(db)
    return service.get_assignment(assignment_id)

