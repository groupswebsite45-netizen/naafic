from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.database import get_db
from app.api.dependencies.auth import get_current_active_teacher
from app.models.user import User
from app.services.teacher_attendance_service import TeacherAttendanceService
from app.schemas.attendance import (
    TeacherAttendanceOptionsResponse,
    TeacherAttendanceRosterResponse,
    TeacherSaveAttendancePayload,
    TeacherAttendanceSessionItem,
    TeacherAttendanceSummaryResponse,
)

router = APIRouter(prefix="/teacher-portal/attendance", tags=["Teacher Attendance Management"])


@router.get(
    "/options",
    response_model=TeacherAttendanceOptionsResponse,
    summary="Get assigned classes, subjects, and academic years for attendance taking"
)
def get_attendance_options(
    current_teacher: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    service = TeacherAttendanceService(db)
    return service.get_filter_options(current_teacher)


@router.get(
    "/roster",
    response_model=TeacherAttendanceRosterResponse,
    summary="Get student roster for class, subject, and date with default PRESENT state"
)
def get_attendance_roster(
    class_id: int = Query(..., description="Class ID"),
    subject_id: int = Query(..., description="Subject ID"),
    attendance_date: date = Query(..., alias="date", description="Date (YYYY-MM-DD)"),
    academic_year: Optional[str] = Query(None, description="Academic Year e.g. 2025-2026"),
    period: Optional[str] = Query(None, description="Class period e.g. 08:00 - 09:00"),
    current_teacher: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    service = TeacherAttendanceService(db)
    return service.get_attendance_roster(
        user=current_teacher,
        class_id=class_id,
        subject_id=subject_id,
        attendance_date=attendance_date,
        academic_year=academic_year,
        period=period
    )


@router.post(
    "/save",
    status_code=status.HTTP_200_OK,
    summary="Save / update student attendance records in PostgreSQL"
)
def save_attendance(
    payload: TeacherSaveAttendancePayload,
    current_teacher: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    service = TeacherAttendanceService(db)
    return service.save_attendance(current_teacher, payload)


@router.get(
    "/history",
    response_model=List[TeacherAttendanceSessionItem],
    summary="Get historical attendance sessions for assigned classes"
)
def get_attendance_history(
    class_id: Optional[int] = Query(None, description="Filter by Class ID"),
    academic_year: Optional[str] = Query(None, description="Filter by Academic Year"),
    current_teacher: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    service = TeacherAttendanceService(db)
    return service.get_attendance_history(
        user=current_teacher,
        class_id=class_id,
        academic_year=academic_year
    )


@router.get(
    "/summary",
    response_model=TeacherAttendanceSummaryResponse,
    summary="Get per-student attendance summary, rate %, and unexcused absence history"
)
def get_attendance_summary(
    class_id: int = Query(..., description="Class ID"),
    subject_id: Optional[int] = Query(None, description="Filter by Subject ID"),
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    current_teacher: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    service = TeacherAttendanceService(db)
    return service.get_class_student_summary(
        user=current_teacher,
        class_id=class_id,
        subject_id=subject_id,
        start_date=start_date,
        end_date=end_date
    )
