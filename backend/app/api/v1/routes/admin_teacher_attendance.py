from datetime import date
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status, Response, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies.database import get_db
from app.api.dependencies.auth import get_current_active_admin
from app.models.user import User
from app.services.admin_teacher_attendance_service import AdminTeacherAttendanceService
from app.schemas.admin_teacher_attendance import (
    TeacherDailyRosterResponse,
    TeacherBulkSavePayload,
    TeacherAttendanceDashboardResponse,
    TeacherAttendanceRecordsResponse,
    StaffAttendanceSummaryResponse,
)

router = APIRouter(prefix="/admin/teacher-attendance", tags=["Admin Teacher Attendance Management"])


@router.get(
    "/roster",
    response_model=TeacherDailyRosterResponse,
    summary="Get daily teacher roster for marking staff attendance"
)
def get_daily_teacher_roster(
    attendance_date: date = Query(..., alias="date", description="Attendance date (YYYY-MM-DD)"),
    academic_year: Optional[str] = Query(None, description="Academic year filter"),
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = AdminTeacherAttendanceService(db)
    return service.get_daily_roster(attendance_date=attendance_date, academic_year=academic_year)


@router.post(
    "/save",
    status_code=status.HTTP_200_OK,
    summary="Record or update daily attendance for registered teachers in bulk"
)
def save_teacher_attendance(
    payload: TeacherBulkSavePayload,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = AdminTeacherAttendanceService(db)
    return service.save_daily_attendance(admin_user=current_admin, payload=payload)


@router.get(
    "/dashboard",
    response_model=TeacherAttendanceDashboardResponse,
    summary="Get teacher attendance dashboard KPIs and historical staff turnout trends"
)
def get_teacher_attendance_dashboard(
    academic_year: Optional[str] = Query(None, description="Academic year filter"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Month filter (1-12)"),
    year: Optional[int] = Query(None, description="Year filter"),
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = AdminTeacherAttendanceService(db)
    return service.get_dashboard(academic_year=academic_year, month=month, year=year)


@router.get(
    "/records",
    response_model=TeacherAttendanceRecordsResponse,
    summary="Get historical individual teacher attendance audit records"
)
def get_teacher_attendance_records(
    teacher_id: Optional[int] = Query(None, description="Teacher ID filter"),
    academic_year: Optional[str] = Query(None, description="Academic year filter"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Month filter (1-12)"),
    year: Optional[int] = Query(None, description="Year filter"),
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    status: Optional[str] = Query(None, description="Status filter: ALL, PRESENT, ABSENT, LATE, ON_LEAVE"),
    search: Optional[str] = Query(None, description="Teacher name or staff ID search"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=200, description="Page size"),
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = AdminTeacherAttendanceService(db)
    return service.get_records(
        teacher_id=teacher_id,
        academic_year=academic_year,
        month=month,
        year=year,
        start_date=start_date,
        end_date=end_date,
        status_filter=status,
        search=search,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/summary",
    response_model=StaffAttendanceSummaryResponse,
    summary="Get complete staff-by-staff attendance breakdown and totals"
)
def get_staff_attendance_summary(
    academic_year: Optional[str] = Query(None, description="Academic year filter"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Month filter (1-12)"),
    year: Optional[int] = Query(None, description="Year filter"),
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = AdminTeacherAttendanceService(db)
    return service.get_staff_summary(
        academic_year=academic_year,
        month=month,
        year=year,
        start_date=start_date,
        end_date=end_date,
    )


@router.get(
    "/export/excel",
    summary="Export daily or staff summary teacher attendance to styled Excel (.xlsx)"
)
def export_teacher_attendance_excel(
    report_type: str = Query("daily", description="Report type: 'daily' or 'staff_summary'"),
    teacher_id: Optional[int] = Query(None, description="Teacher ID filter"),
    target_date: Optional[date] = Query(None, alias="date", description="Target date for daily report"),
    academic_year: Optional[str] = Query(None, description="Academic year filter"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Month filter"),
    year: Optional[int] = Query(None, description="Year filter"),
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = AdminTeacherAttendanceService(db)
    excel_bytes = service.export_excel(
        report_type=report_type,
        teacher_id=teacher_id,
        target_date=target_date,
        academic_year=academic_year,
        month=month,
        year=year,
    )

    prefix = "Teacher_Daily_Attendance" if report_type == "daily" else "Staff_Attendance_Summary"
    safe_date = (target_date or date.today()).isoformat()
    filename = f"{prefix}_{safe_date}.xlsx"

    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get(
    "/export/pdf",
    summary="Download print-ready official PDF report for teacher attendance"
)
def export_teacher_attendance_pdf(
    report_type: str = Query("daily", description="Report type: 'daily' or 'staff_summary'"),
    teacher_id: Optional[int] = Query(None, description="Teacher ID filter"),
    target_date: Optional[date] = Query(None, alias="date", description="Target date for daily report"),
    academic_year: Optional[str] = Query(None, description="Academic year filter"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Month filter"),
    year: Optional[int] = Query(None, description="Year filter"),
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = AdminTeacherAttendanceService(db)
    pdf_bytes = service.export_pdf(
        report_type=report_type,
        teacher_id=teacher_id,
        target_date=target_date,
        academic_year=academic_year,
        month=month,
        year=year,
    )

    prefix = "Teacher_Daily_Attendance" if report_type == "daily" else "Staff_Attendance_Summary"
    safe_date = (target_date or date.today()).isoformat()
    filename = f"{prefix}_{safe_date}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

