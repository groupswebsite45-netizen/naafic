from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.api.dependencies.database import get_db
from app.api.dependencies.auth import get_current_active_admin, get_current_user
from app.models.user import User
from app.services.class_service import ClassService
from app.schemas.school_class import (
    SchoolClassCreate,
    SchoolClassUpdate,
    SchoolClassResponse,
    ClassSummary,
    ClassFullProfileResponse,
    ClassStatusUpdate,
    ClassEnrollmentCreate,
    ClassTeacherAssignPayload
)

router = APIRouter(prefix="/classes", tags=["Classes"])


@router.get(
    "/summary",
    response_model=ClassSummary,
    summary="Get aggregated class and capacity metrics from PostgreSQL"
)
def get_classes_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ClassService(db)
    return service.get_summary()


@router.get(
    "/active",
    response_model=List[SchoolClassResponse],
    summary="Get only ACTIVE classes that have at least 1 enrolled student — use this for all dropdowns/selectors"
)
def get_active_classes_with_students(
    academic_year: Optional[str] = None,
    division: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns classes satisfying the core business rule:
      - status == ACTIVE
      - has >= 1 active student enrollment

    Use this endpoint for ALL class selector dropdowns in the system.
    Never shows test, empty, historical, or inactive classes.
    """
    service = ClassService(db)
    return service.get_active_classes_with_students(
        academic_year=academic_year,
        division=division
    )


@router.get(
    "",
    response_model=List[SchoolClassResponse],
    summary="List and search school classes with capacity metrics"
)
def list_classes(
    query: Optional[str] = None,
    academic_year: Optional[str] = None,
    division: Optional[str] = None,
    status: Optional[str] = None,
    level: Optional[str] = None,
    section: Optional[str] = None,
    capacity_filter: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ClassService(db)
    classes, _ = service.list_classes(
        query=query,
        academic_year=academic_year,
        division=division,
        status_filter=status,
        level=level,
        section=section,
        capacity_filter=capacity_filter,
        skip=skip,
        limit=limit
    )
    return classes



@router.get(
    "/{class_id}/full",
    response_model=ClassFullProfileResponse,
    summary="Get comprehensive class profile with capacity, students, teachers, subjects, timetable, and exams"
)
def get_class_full_profile(
    class_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ClassService(db)
    return service.get_full_profile(class_id)


@router.get(
    "/{class_id}",
    response_model=SchoolClassResponse,
    summary="Get class basic details by ID"
)
def get_class(
    class_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ClassService(db)
    c = service.get_class(class_id)
    metrics = service.repo.get_class_capacity_metrics(c)
    teachers = service.repo.get_class_teachers(class_id)
    subjects = service.repo.get_class_subjects(class_id)
    return SchoolClassResponse(
        id=c.id,
        name=c.name,
        code=c.code,
        division=c.division or "PRIMARY",
        level=c.level or c.name,
        section=c.section,
        academic_year=c.academic_year,
        capacity=c.capacity,
        description=c.description,
        status=c.status,
        created_at=c.created_at,
        updated_at=c.updated_at,
        students_count=metrics.enrolled,
        teachers_count=len(set(t.teacher_id for t in teachers)),
        subjects_count=len(subjects),
        available_seats=metrics.available_seats,
        utilization_rate=metrics.utilization_rate,
        capacity_status=metrics.capacity_status
    )


@router.post(
    "",
    response_model=SchoolClassResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new class (Admin only)"
)
def create_class(
    payload: SchoolClassCreate,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = ClassService(db)
    c = service.create_class(payload, user_id=current_admin.id)
    return SchoolClassResponse(
        id=c.id,
        name=c.name,
        code=c.code,
        division=c.division or "PRIMARY",
        level=c.level or c.name,
        section=c.section,
        academic_year=c.academic_year,
        capacity=c.capacity,
        description=c.description,
        status=c.status,
        created_at=c.created_at,
        updated_at=c.updated_at,
        students_count=0,
        teachers_count=0,
        subjects_count=0,
        available_seats=c.capacity,
        utilization_rate=0.0,
        capacity_status="NORMAL"
    )


@router.put(
    "/{class_id}",
    response_model=SchoolClassResponse,
    summary="Update class details (Admin only)"
)
def update_class(
    class_id: int,
    payload: SchoolClassUpdate,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = ClassService(db)
    c = service.update_class(class_id, payload, user_id=current_admin.id)
    metrics = service.repo.get_class_capacity_metrics(c)
    teachers = service.repo.get_class_teachers(class_id)
    subjects = service.repo.get_class_subjects(class_id)
    return SchoolClassResponse(
        id=c.id,
        name=c.name,
        code=c.code,
        division=c.division or "PRIMARY",
        level=c.level or c.name,
        section=c.section,
        academic_year=c.academic_year,
        capacity=c.capacity,
        description=c.description,
        status=c.status,
        created_at=c.created_at,
        updated_at=c.updated_at,
        students_count=metrics.enrolled,
        teachers_count=len(set(t.teacher_id for t in teachers)),
        subjects_count=len(subjects),
        available_seats=metrics.available_seats,
        utilization_rate=metrics.utilization_rate,
        capacity_status=metrics.capacity_status
    )


@router.patch(
    "/{class_id}/status",
    response_model=SchoolClassResponse,
    summary="Update class status (ACTIVE / INACTIVE / ARCHIVED) (Admin only)"
)
def update_class_status(
    class_id: int,
    payload: ClassStatusUpdate,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = ClassService(db)
    c = service.update_status(class_id, payload.status, payload.reason, user_id=current_admin.id)
    metrics = service.repo.get_class_capacity_metrics(c)
    return SchoolClassResponse(
        id=c.id,
        name=c.name,
        code=c.code,
        division=c.division or "PRIMARY",
        level=c.level or c.name,
        section=c.section,
        academic_year=c.academic_year,
        capacity=c.capacity,
        description=c.description,
        status=c.status,
        created_at=c.created_at,
        updated_at=c.updated_at,
        students_count=metrics.enrolled,
        teachers_count=0,
        subjects_count=0,
        available_seats=metrics.available_seats,
        utilization_rate=metrics.utilization_rate,
        capacity_status=metrics.capacity_status
    )


@router.delete(
    "/{class_id}",
    status_code=status.HTTP_200_OK,
    summary="Deactivate class (Admin only)"
)
def delete_class(
    class_id: int,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = ClassService(db)
    service.delete_class(class_id, user_id=current_admin.id)
    return {"message": "Class marked as inactive successfully."}


@router.post(
    "/{class_id}/students",
    status_code=status.HTTP_201_CREATED,
    summary="Enroll student into class (Admin only)"
)
def enroll_student_to_class(
    class_id: int,
    payload: ClassEnrollmentCreate,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = ClassService(db)
    enrollment = service.enroll_student(
        class_id=class_id,
        student_id=payload.student_id,
        academic_year=payload.academic_year,
        enrollment_date=payload.enrollment_date,
        user_id=current_admin.id
    )
    return {
        "message": "Student successfully enrolled in class.",
        "enrollment_id": enrollment.id,
        "class_id": enrollment.class_id,
        "student_id": enrollment.student_id,
        "academic_year": enrollment.academic_year
    }


@router.delete(
    "/{class_id}/students/{student_id}",
    status_code=status.HTTP_200_OK,
    summary="Remove or transfer student from class (Admin only)"
)
def remove_student_from_class(
    class_id: int,
    student_id: int,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = ClassService(db)
    service.remove_student_enrollment(class_id=class_id, student_id=student_id, user_id=current_admin.id)
    return {"message": "Student removed from class enrollment successfully."}


@router.post(
    "/{class_id}/teachers",
    status_code=status.HTTP_201_CREATED,
    summary="Assign teacher and subject to class (Admin only)"
)
def assign_teacher_to_class(
    class_id: int,
    payload: ClassTeacherAssignPayload,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = ClassService(db)
    assignment = service.assign_teacher_subject(
        class_id=class_id,
        teacher_id=payload.teacher_id,
        subject_id=payload.subject_id,
        academic_year=payload.academic_year,
        user_id=current_admin.id
    )
    return {
        "message": "Teacher assigned to class and subject successfully.",
        "assignment_id": assignment.id,
        "class_id": assignment.class_id,
        "teacher_id": assignment.teacher_id,
        "subject_id": assignment.subject_id
    }


@router.put(
    "/{class_id}/teachers/{assignment_id}",
    status_code=status.HTTP_200_OK,
    summary="Update teacher assignment for class (Admin only)"
)
def update_teacher_for_class(
    class_id: int,
    assignment_id: int,
    payload: ClassTeacherAssignPayload,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = ClassService(db)
    assignment = service.update_teacher_assignment(
        class_id=class_id,
        assignment_id=assignment_id,
        teacher_id=payload.teacher_id,
        subject_id=payload.subject_id,
        academic_year=payload.academic_year,
        user_id=current_admin.id
    )
    return {
        "message": "Teacher assignment updated successfully.",
        "assignment_id": assignment.id,
        "class_id": assignment.class_id,
        "teacher_id": assignment.teacher_id,
        "subject_id": assignment.subject_id
    }


@router.delete(
    "/{class_id}/teachers/{assignment_id}",
    status_code=status.HTTP_200_OK,
    summary="Remove teacher assignment from class (Admin only)"
)
def remove_teacher_from_class(
    class_id: int,
    assignment_id: int,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = ClassService(db)
    service.remove_teacher_assignment(class_id=class_id, assignment_id=assignment_id, user_id=current_admin.id)
    return {"message": "Teacher assignment removed from class successfully."}
