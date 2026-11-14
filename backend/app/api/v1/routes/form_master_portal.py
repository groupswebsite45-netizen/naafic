from typing import List, Optional, Dict, Any
from datetime import date
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.database import get_db
from app.api.dependencies.auth import get_current_active_teacher
from app.models.user import User
from app.services.form_master_portal_service import FormMasterPortalService
from app.schemas.form_master import (
    FormMasterClassSummary,
    FormMasterStudentItem,
    FormMasterDashboardData,
    FormMasterResultsData,
    FormMasterAttendanceData,
    FormMasterFeesData,
)

router = APIRouter(prefix="/form-master", tags=["Form Master Portal"])


@router.get(
    "/check",
    summary="Check if authenticated teacher is an appointed Form Master"
)
def check_form_master_status(
    current_teacher: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    service = FormMasterPortalService(db)
    return service.check_is_form_master(current_teacher)


@router.get(
    "/my-classes",
    response_model=List[FormMasterClassSummary],
    summary="List all classes officially assigned to authenticated Form Master"
)
def get_my_form_classes(
    academic_year: Optional[str] = Query(None, description="Optional academic year filter"),
    current_teacher: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    service = FormMasterPortalService(db)
    return service.get_my_form_classes(current_teacher, academic_year=academic_year)


@router.get(
    "/classes/{class_id}/dashboard",
    response_model=FormMasterDashboardData,
    summary="Get supervisory dashboard for an assigned Form Master class"
)
def get_form_master_dashboard(
    class_id: int,
    academic_year: Optional[str] = Query(None),
    current_teacher: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    service = FormMasterPortalService(db)
    return service.get_class_dashboard(current_teacher, class_id=class_id, academic_year=academic_year)


@router.get(
    "/classes/{class_id}/students",
    response_model=List[FormMasterStudentItem],
    summary="Get full student roster with academic, attendance, and fee status for assigned class"
)
def get_form_master_students(
    class_id: int,
    academic_year: Optional[str] = Query(None),
    current_teacher: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    service = FormMasterPortalService(db)
    return service.get_class_students(current_teacher, class_id=class_id, academic_year=academic_year)


@router.get(
    "/classes/{class_id}/results",
    response_model=FormMasterResultsData,
    summary="Cross-subject academic results monitoring for assigned class (Read-Only)"
)
def get_form_master_results(
    class_id: int,
    academic_year: Optional[str] = Query(None),
    exam_type: Optional[str] = Query(None, description="Filter: Mid-Term, Final, Monthly Test, Quiz"),
    exam_id: Optional[int] = Query(None),
    subject_id: Optional[int] = Query(None),
    current_teacher: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    service = FormMasterPortalService(db)
    return service.get_class_results(
        current_teacher,
        class_id=class_id,
        academic_year=academic_year,
        exam_type=exam_type,
        exam_id=exam_id,
        subject_id=subject_id
    )


@router.get(
    "/classes/{class_id}/attendance",
    response_model=FormMasterAttendanceData,
    summary="Attendance records across all subjects for assigned class (Read-Only)"
)
def get_form_master_attendance(
    class_id: int,
    academic_year: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    subject_id: Optional[int] = Query(None),
    current_teacher: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    service = FormMasterPortalService(db)
    return service.get_class_attendance(
        current_teacher,
        class_id=class_id,
        academic_year=academic_year,
        start_date=start_date,
        end_date=end_date,
        subject_id=subject_id
    )


@router.get(
    "/classes/{class_id}/fees",
    response_model=FormMasterFeesData,
    summary="Student fee status and payment history for assigned class (Read-Only)"
)
def get_form_master_fees(
    class_id: int,
    academic_year: Optional[str] = Query(None),
    current_teacher: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    service = FormMasterPortalService(db)
    return service.get_class_fees(current_teacher, class_id=class_id, academic_year=academic_year)

