from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.api.dependencies.database import get_db
from app.api.dependencies.auth import get_current_active_admin, get_current_user
from app.models.user import User
from app.services.subject_service import SubjectService
from app.schemas.subject import (
    SubjectCreate,
    SubjectUpdate,
    SubjectResponse,
    SubjectSummary,
    SubjectFullProfileResponse,
    SubjectStatusUpdate,
    SubjectAssignClassPayload,
    SubjectAssignTeacherPayload
)

router = APIRouter(prefix="/subjects", tags=["Subjects"])


@router.get(
    "/summary",
    response_model=SubjectSummary,
    summary="Get aggregated subject metrics from PostgreSQL"
)
def get_subjects_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = SubjectService(db)
    return service.get_summary()


@router.get(
    "/departments",
    response_model=List[str],
    summary="Get distinct department list from PostgreSQL"
)
def get_distinct_departments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = SubjectService(db)
    return service.get_departments()


@router.get(
    "",
    response_model=List[SubjectResponse],
    summary="List and search academic subjects"
)
def list_subjects(
    query: Optional[str] = None,
    division: Optional[str] = None,
    level: Optional[str] = None,
    class_id: Optional[int] = None,
    department: Optional[str] = None,
    status: Optional[str] = None,
    assigned_filter: Optional[str] = None,
    academic_year: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = SubjectService(db)
    subjects, _ = service.list_subjects(
        query=query,
        division=division,
        level=level,
        class_id=class_id,
        department=department,
        status_filter=status,
        assigned_filter=assigned_filter,
        academic_year=academic_year,
        skip=skip,
        limit=limit
    )
    return subjects


@router.get(
    "/{subject_id}/full",
    response_model=SubjectFullProfileResponse,
    summary="Get comprehensive subject profile with classes, teachers, timetable, and exams"
)
def get_subject_full_profile(
    subject_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = SubjectService(db)
    return service.get_full_profile(subject_id)


@router.get(
    "/{subject_id}",
    response_model=SubjectResponse,
    summary="Get basic subject details by ID"
)
def get_subject(
    subject_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = SubjectService(db)
    s = service.get_subject(subject_id)
    return SubjectResponse(
        id=s.id,
        name=s.name,
        code=s.code,
        division=s.division or "ALL",
        applicable_levels=s.applicable_levels,
        department=s.department,
        description=s.description,
        status=s.status,
        created_at=s.created_at,
        updated_at=s.updated_at,
        classes_count=0,
        teachers_count=0,
        timetables_count=0,
        exams_count=0
    )


@router.post(
    "",
    response_model=SubjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new academic subject (Admin only)"
)
def create_subject(
    payload: SubjectCreate,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = SubjectService(db)
    s = service.create_subject(payload, user_id=current_admin.id)
    return SubjectResponse(
        id=s.id,
        name=s.name,
        code=s.code,
        division=s.division or "ALL",
        applicable_levels=s.applicable_levels,
        department=s.department,
        description=s.description,
        status=s.status,
        created_at=s.created_at,
        updated_at=s.updated_at,
        classes_count=0,
        teachers_count=0,
        timetables_count=0,
        exams_count=0
    )


@router.put(
    "/{subject_id}",
    response_model=SubjectResponse,
    summary="Update subject details (Admin only)"
)
def update_subject(
    subject_id: int,
    payload: SubjectUpdate,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = SubjectService(db)
    s = service.update_subject(subject_id, payload, user_id=current_admin.id)
    return SubjectResponse(
        id=s.id,
        name=s.name,
        code=s.code,
        division=s.division or "ALL",
        applicable_levels=s.applicable_levels,
        department=s.department,
        description=s.description,
        status=s.status,
        created_at=s.created_at,
        updated_at=s.updated_at,
        classes_count=0,
        teachers_count=0,
        timetables_count=0,
        exams_count=0
    )


@router.patch(
    "/{subject_id}/status",
    response_model=SubjectResponse,
    summary="Update subject active/inactive status (Admin only)"
)
def update_subject_status(
    subject_id: int,
    payload: SubjectStatusUpdate,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = SubjectService(db)
    s = service.update_status(subject_id, payload.status, payload.reason, user_id=current_admin.id)
    return SubjectResponse(
        id=s.id,
        name=s.name,
        code=s.code,
        division=s.division or "ALL",
        applicable_levels=s.applicable_levels,
        department=s.department,
        description=s.description,
        status=s.status,
        created_at=s.created_at,
        updated_at=s.updated_at,
        classes_count=0,
        teachers_count=0,
        timetables_count=0,
        exams_count=0
    )


@router.delete(
    "/{subject_id}",
    status_code=status.HTTP_200_OK,
    summary="Deactivate subject (Admin only)"
)
def delete_subject(
    subject_id: int,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = SubjectService(db)
    service.delete_subject(subject_id, user_id=current_admin.id)
    return {"message": "Subject marked as inactive successfully."}


@router.post(
    "/{subject_id}/classes",
    status_code=status.HTTP_201_CREATED,
    summary="Assign subject to class (Admin only)"
)
def assign_subject_to_class(
    subject_id: int,
    payload: SubjectAssignClassPayload,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = SubjectService(db)
    assignment = service.assign_to_class(
        subject_id=subject_id,
        data=payload,
        user_id=current_admin.id
    )
    return {
        "message": "Subject successfully assigned to class.",
        "assignment_id": assignment.id,
        "subject_id": assignment.subject_id,
        "class_id": assignment.class_id,
        "academic_year": assignment.academic_year
    }


@router.delete(
    "/{subject_id}/classes/{assignment_id}",
    status_code=status.HTTP_200_OK,
    summary="Remove subject assignment from class (Admin only)"
)
def remove_subject_class_assignment(
    subject_id: int,
    assignment_id: int,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = SubjectService(db)
    service.remove_class_assignment(subject_id=subject_id, assignment_id=assignment_id, user_id=current_admin.id)
    return {"message": "Subject removed from class assignment successfully."}


@router.post(
    "/{subject_id}/teachers",
    status_code=status.HTTP_201_CREATED,
    summary="Assign teacher to teach subject in class (Admin only)"
)
def assign_teacher_to_subject(
    subject_id: int,
    payload: SubjectAssignTeacherPayload,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = SubjectService(db)
    assignment = service.assign_teacher(
        subject_id=subject_id,
        data=payload,
        user_id=current_admin.id
    )
    return {
        "message": "Teacher allocated to subject successfully.",
        "assignment_id": assignment.id,
        "subject_id": assignment.subject_id,
        "teacher_id": assignment.teacher_id,
        "class_id": assignment.class_id
    }


@router.delete(
    "/{subject_id}/teachers/{assignment_id}",
    status_code=status.HTTP_200_OK,
    summary="Remove teacher allocation from subject (Admin only)"
)
def remove_teacher_from_subject(
    subject_id: int,
    assignment_id: int,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = SubjectService(db)
    service.remove_teacher_assignment(subject_id=subject_id, assignment_id=assignment_id, user_id=current_admin.id)
    return {"message": "Teacher assignment removed from subject successfully."}
