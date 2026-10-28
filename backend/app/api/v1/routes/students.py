from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, Query, status, UploadFile, File, Form, Response, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies.database import get_db
from app.api.dependencies.auth import get_current_active_admin, get_current_user, get_current_staff_user
from app.models.user import User
from app.services.student_service import StudentService
from app.services.student_import_service import StudentImportService
from app.schemas.student import (
    StudentCreate,
    StudentUpdate,
    StudentResponse,
    StudentEnrollmentCreate,
    StudentEnrollmentResponse,
    StudentSummaryMetrics,
    StudentStatusUpdate,
    StudentFullProfileResponse,
    CreateStudentPortalAccountPayload,
    ResetStudentPortalPasswordPayload,
    UpdateStudentPortalStatusPayload,
    UpdateStudentPortalUsernamePayload,
)
from app.schemas.student_import import (
    StudentImportPreviewResponse,
    StudentImportExecuteRequest,
    StudentImportSummaryResponse,
    StudentImportLogResponse,
)

router = APIRouter(prefix="/students", tags=["Students"])


# =========================================================================
# BULK EXCEL STUDENT IMPORT ENDPOINTS (ADMIN ONLY)
# =========================================================================

@router.get(
    "/import/template",
    summary="Download formatted Excel (.xlsx) template for student batch import",
    response_class=Response,
)
def download_student_import_template(
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    """Generate and download formatted Excel template with column instructions and example rows."""
    service = StudentImportService(db)
    excel_bytes = service.generate_template()
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=Hawlwadaag_Student_Import_Template.xlsx",
            "Cache-Control": "no-cache",
        }
    )


@router.post(
    "/import/preview",
    response_model=StudentImportPreviewResponse,
    summary="Parse and preview Excel student data with server-side PostgreSQL validation (Admin only)"
)
async def preview_student_import(
    file: UploadFile = File(...),
    class_id: int = Form(...),
    academic_year: Optional[str] = Form(None),
    academic_year_id: Optional[str] = Form(None),
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    """Validates uploaded Excel file row-by-row and returns detailed status preview without modifying database."""
    year = (academic_year or academic_year_id or "2026/2027").strip()

    if not file.filename.lower().endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Please upload an .xlsx Excel file."
        )

    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is empty. Please select a valid Excel spreadsheet."
        )

    service = StudentImportService(db)
    return service.parse_and_validate_excel(
        file_bytes=file_bytes,
        class_id=class_id,
        academic_year=year,
    )


@router.post(
    "/import/execute",
    response_model=StudentImportSummaryResponse,
    summary="Execute atomic batch import and enroll validated students into destination class (Admin only)"
)
def execute_student_import(
    payload: StudentImportExecuteRequest,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    """Commits validated student profiles and class enrollments to PostgreSQL in an atomic transaction."""
    service = StudentImportService(db)
    return service.execute_import(
        request=payload,
        admin_user=current_admin,
    )


@router.post(
    "/import",
    response_model=StudentImportSummaryResponse,
    summary="Alias to execute student bulk import (Admin only)"
)
def execute_student_import_alias(
    payload: StudentImportExecuteRequest,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    """Alias for POST /import/execute."""
    service = StudentImportService(db)
    return service.execute_import(
        request=payload,
        admin_user=current_admin,
    )


@router.get(
    "/import/history",
    response_model=List[StudentImportLogResponse],
    summary="Get student bulk import audit history (Admin only)"
)
def get_student_import_history(
    limit: int = Query(50, ge=1, le=200),
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    """Retrieve audit history logs of student Excel imports."""
    service = StudentImportService(db)
    return service.get_import_history(limit=limit)



@router.get(
    "/class-filter-options",
    summary="Get classes that have at least 1 active student — for student filter dropdowns only"
)
def get_class_filter_options(
    academic_year: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns the list of classes available for student filtering.
    Only includes classes that have at least 1 active enrolled student.
    Used for Admin → Students page class dropdown.
    """
    from app.services.class_service import ClassService
    service = ClassService(db)
    active_classes = service.get_active_classes_with_students(academic_year=academic_year)
    return [
        {
            "id": c.id,
            "name": c.name,
            "code": c.code,
            "division": c.division,
            "level": c.level,
            "section": c.section,
            "academic_year": c.academic_year,
            "students_count": c.students_count
        }
        for c in active_classes
    ]


@router.get(
    "/summary",
    response_model=StudentSummaryMetrics,
    summary="Get student overview metrics (Admin only)"
)
def get_student_summary(
    academic_year: Optional[str] = None,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = StudentService(db)
    return service.get_summary_metrics(academic_year=academic_year)



@router.get(
    "",
    response_model=List[StudentResponse],
    summary="List and search students with rich filtering (Admin and Teachers only)"
)
def list_students(
    query: Optional[str] = None,
    search: Optional[str] = None,
    class_id: Optional[int] = None,
    academic_year: Optional[str] = None,
    gender: Optional[str] = None,
    status: Optional[str] = None,
    has_portal: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    current_staff: User = Depends(get_current_staff_user),
    db: Session = Depends(get_db)
):
    service = StudentService(db)
    search_term = query or search
    students, _ = service.list_students(
        query=search_term,
        class_id=class_id,
        academic_year=academic_year,
        gender=gender,
        status_filter=status,
        has_portal=has_portal,
        skip=skip,
        limit=limit
    )
    return students



@router.get(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Get student details by ID"
)
def get_student(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = StudentService(db)
    student = service.get_student(student_id)
    roles = [r.upper() for r in current_user.role_names]
    if "ADMIN" not in roles and "TEACHER" not in roles and not current_user.is_superuser:
        if student.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You can only view your own student record."
            )
    return student


@router.get(
    "/{student_id}/profile",
    response_model=StudentFullProfileResponse,
    summary="Get complete student profile including academic & fee records"
)
def get_student_full_profile(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = StudentService(db)
    student = service.get_student(student_id)
    roles = [r.upper() for r in current_user.role_names]
    if "ADMIN" not in roles and "TEACHER" not in roles and not current_user.is_superuser:
        if student.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You can only view your own student profile."
            )
    return service.get_full_profile(student_id)


@router.post(
    "",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new student (Admin only)"
)
def create_student(
    payload: StudentCreate,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = StudentService(db)
    return service.create_student(payload, creator_user_id=current_admin.id)


@router.put(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Update student details (Admin only)"
)
def update_student(
    student_id: int,
    payload: StudentUpdate,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = StudentService(db)
    return service.update_student(student_id, payload, user_id=current_admin.id)


@router.patch(
    "/{student_id}/status",
    response_model=StudentResponse,
    summary="Change student status (e.g. Activate/Deactivate) (Admin only)"
)
def update_student_status(
    student_id: int,
    payload: StudentStatusUpdate,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = StudentService(db)
    return service.update_status(
        student_id=student_id,
        new_status=payload.status,
        reason=payload.reason,
        user_id=current_admin.id
    )


@router.get(
    "/{student_id}/account/suggest-username",
    summary="Suggest a valid, sanitized, unique portal username for a student (Admin only)"
)
def suggest_portal_username(
    student_id: int,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = StudentService(db)
    student = service.get_student(student_id)
    suggested = service.suggest_portal_username(student_id=student_id)
    return {
        "suggested_username": suggested,
        "student_name": student.full_name or f"{student.first_name} {student.last_name}".strip(),
        "admission_number": student.admission_number
    }


@router.post(
    "/{student_id}/account",
    status_code=status.HTTP_201_CREATED,
    summary="Create student portal login account (Admin only)"
)
def create_portal_account(
    student_id: int,
    payload: CreateStudentPortalAccountPayload,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = StudentService(db)
    user = service.create_portal_account(
        student_id=student_id,
        username=payload.username,
        password=payload.password,
        creator_id=current_admin.id
    )
    return {"message": "Student portal account created successfully.", "username": user.username}


@router.post(
    "/{student_id}/account/reset-password",
    summary="Reset student portal password (Admin only)"
)
def reset_portal_password(
    student_id: int,
    payload: ResetStudentPortalPasswordPayload,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = StudentService(db)
    user = service.reset_portal_password(
        student_id=student_id,
        new_password=payload.password,
        creator_id=current_admin.id
    )
    return {"message": "Password reset successfully.", "username": user.username}


@router.patch(
    "/{student_id}/account/status",
    summary="Enable or disable student portal account (Admin only)"
)
def update_portal_status(
    student_id: int,
    payload: UpdateStudentPortalStatusPayload,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = StudentService(db)
    user = service.toggle_portal_access(
        student_id=student_id,
        is_active=payload.is_active,
        creator_id=current_admin.id
    )
    return {
        "message": f"Portal account {'enabled' if user.is_active else 'disabled'} successfully.",
        "is_active": user.is_active,
        "portal_status": "ACTIVE" if user.is_active else "DISABLED"
    }


@router.patch(
    "/{student_id}/account/username",
    summary="Update student portal username (Admin only)"
)
def update_portal_username(
    student_id: int,
    payload: UpdateStudentPortalUsernamePayload,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = StudentService(db)
    user = service.change_portal_username(
        student_id=student_id,
        new_username=payload.username,
        creator_id=current_admin.id
    )
    return {
        "message": "Portal username updated successfully.",
        "username": user.username
    }


@router.post(
    "/{student_id}/enroll",
    response_model=StudentEnrollmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Enroll student into a class (Admin only)"
)
def enroll_student(
    student_id: int,
    payload: StudentEnrollmentCreate,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = StudentService(db)
    return service.enroll_student_to_class(student_id, payload, user_id=current_admin.id)


@router.post(
    "/{student_id}/class-change",
    summary="Change an individual student's class with historical record preservation (Admin only)"
)
def change_student_class_route(
    student_id: int,
    payload: dict,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    from app.services.class_promotion_service import ClassPromotionService
    from app.schemas.class_promotion import IndividualClassChangePayload
    service = ClassPromotionService(db)
    change_payload = IndividualClassChangePayload(
        new_class_id=payload.get("new_class_id") or payload.get("class_id"),
        academic_year=payload.get("academic_year"),
        reason=payload.get("reason"),
        is_promotion=payload.get("is_promotion", False),
        preserve_history=payload.get("preserve_history", True)
    )
    return service.execute_individual_class_change(
        student_id=student_id,
        payload=change_payload,
        admin_user=current_admin
    )
