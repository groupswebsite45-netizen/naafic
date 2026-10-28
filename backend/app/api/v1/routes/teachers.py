from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.api.dependencies.database import get_db
from app.api.dependencies.auth import get_current_active_admin, get_current_user
from app.models.user import User
from app.services.teacher_service import TeacherService
from app.schemas.teacher import (
    TeacherCreate,
    TeacherUpdate,
    TeacherResponse,
    TeacherAssignmentCreate,
    TeacherAssignmentResponse,
    TeacherSummary,
    TeacherFullProfile,
    TeacherStatusUpdate,
)

router = APIRouter(prefix="/teachers", tags=["Teachers"])


class CreatePortalAccountPayload(BaseModel):
    username: str
    password: str


@router.get(
    "/summary",
    response_model=TeacherSummary,
    summary="Get teacher summary statistics (Admin only)"
)
def get_teacher_summary(
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = TeacherService(db)
    return service.get_summary()


@router.get(
    "",
    response_model=List[TeacherResponse],
    summary="List and search teachers with multi-filtering"
)
def list_teachers(
    query: Optional[str] = None,
    status: Optional[str] = None,
    class_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    has_portal: Optional[bool] = None,
    academic_year: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = TeacherService(db)
    teachers, _ = service.list_teachers(
        query=query,
        status_filter=status,
        class_id=class_id,
        subject_id=subject_id,
        has_portal=has_portal,
        academic_year=academic_year,
        skip=skip,
        limit=limit
    )
    return teachers


@router.get(
    "/{teacher_id}/full",
    response_model=TeacherFullProfile,
    summary="Get comprehensive teacher profile including assignments and timetable"
)
def get_teacher_full_profile(
    teacher_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = TeacherService(db)
    return service.get_full_profile(teacher_id)


@router.get(
    "/{teacher_id}",
    response_model=TeacherResponse,
    summary="Get teacher details by ID"
)
def get_teacher(
    teacher_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = TeacherService(db)
    return service.get_teacher(teacher_id)


@router.post(
    "",
    response_model=TeacherResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new teacher (Admin only)"
)
def create_teacher(
    payload: TeacherCreate,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = TeacherService(db)
    return service.create_teacher(payload, creator_user_id=current_admin.id)


@router.put(
    "/{teacher_id}",
    response_model=TeacherResponse,
    summary="Update teacher details (Admin only)"
)
def update_teacher(
    teacher_id: int,
    payload: TeacherUpdate,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = TeacherService(db)
    return service.update_teacher(teacher_id, payload, user_id=current_admin.id)


@router.patch(
    "/{teacher_id}/status",
    response_model=TeacherResponse,
    summary="Update teacher active/inactive status (Admin only)"
)
def update_teacher_status(
    teacher_id: int,
    payload: TeacherStatusUpdate,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = TeacherService(db)
    return service.update_status(teacher_id, payload.status, payload.reason, user_id=current_admin.id)


@router.post(
    "/{teacher_id}/account",
    status_code=status.HTTP_201_CREATED,
    summary="Create teacher portal login account (Admin only)"
)
def create_portal_account(
    teacher_id: int,
    payload: CreatePortalAccountPayload,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = TeacherService(db)
    user = service.create_portal_account(
        teacher_id=teacher_id,
        username=payload.username,
        password=payload.password,
        creator_id=current_admin.id
    )
    return {"message": "Teacher portal account created successfully.", "username": user.username}


@router.post(
    "/{teacher_id}/assignments",
    response_model=TeacherAssignmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Assign teacher to class and subject (Admin only)"
)
def assign_class_subject(
    teacher_id: int,
    payload: TeacherAssignmentCreate,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = TeacherService(db)
    return service.assign_class_subject(teacher_id, payload, user_id=current_admin.id)


@router.delete(
    "/assignments/{assignment_id}",
    status_code=status.HTTP_200_OK,
    summary="Remove teacher class assignment (Admin only)"
)
def remove_assignment(
    assignment_id: int,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = TeacherService(db)
    service.remove_assignment(assignment_id, user_id=current_admin.id)
    return {"message": "Teacher assignment removed successfully."}
