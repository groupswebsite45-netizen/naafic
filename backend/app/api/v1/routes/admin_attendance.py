from datetime import date
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status, Response, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies.database import get_db
from app.api.dependencies.auth import get_current_active_admin
from app.models.user import User
from app.services.admin_attendance_service import AdminAttendanceService
from app.schemas.admin_attendance import (
    AdminAttendanceFilterOptionsResponse,
    AdminAttendanceDashboardResponse,
    AdminAttendanceRecordsListResponse,
    AdminClassAttendanceReportResponse,
    AdminAttendanceFrequentAbsenteeItem,
)
from app.schemas.attendance import StudentAttendanceHistoryDetailResponse

router = APIRouter(prefix="/admin/attendance", tags=["Admin Attendance Monitoring & Absence Reports"])


@router.get(
    "/filter-options",
    response_model=AdminAttendanceFilterOptionsResponse,
    summary="Get filter options (academic years, classes, subjects, months) for attendance monitoring"
)
def get_filter_options(
    academic_year: Optional[str] = Query(None, description="Academic year filter e.g. 2026/2027"),
    class_id: Optional[int] = Query(None, description="Class ID filter to load class-specific subjects and teachers"),
    subject_id: Optional[int] = Query(None, description="Subject ID filter to narrow assigned teachers"),
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = AdminAttendanceService(db)
    return service.get_filter_options(
        academic_year=academic_year,
        class_id=class_id,
        subject_id=subject_id,
    )


@router.get(
    "/dashboard",
    response_model=AdminAttendanceDashboardResponse,
    summary="Get school-wide attendance dashboard KPIs, daily/weekly/monthly trends, and frequent absentees"
)
def get_attendance_dashboard(
    academic_year: Optional[str] = Query(None, description="Academic year filter e.g. 2026/2027"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Month filter (1-12)"),
    year: Optional[int] = Query(None, description="Year filter e.g. 2026"),
    class_id: Optional[int] = Query(None, description="Class ID filter"),
    subject_id: Optional[int] = Query(None, description="Subject ID filter"),
    teacher_id: Optional[int] = Query(None, description="Teacher ID filter"),
    attendance_date: Optional[date] = Query(None, alias="date", description="Specific Date filter"),
    threshold: int = Query(3, ge=1, description="Absence count threshold for frequent absentee detection"),
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = AdminAttendanceService(db)
    return service.get_dashboard(
        academic_year=academic_year,
        month=month,
        year=year,
        class_id=class_id,
        subject_id=subject_id,
        teacher_id=teacher_id,
        attendance_date=attendance_date,
        threshold=threshold,
    )


@router.get(
    "/records",
    response_model=AdminAttendanceRecordsListResponse,
    summary="Get individual historical attendance records across school with full filtering"
)
def get_attendance_records(
    academic_year: Optional[str] = Query(None, description="Academic year filter"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Month filter (1-12)"),
    year: Optional[int] = Query(None, description="Year filter"),
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    class_id: Optional[int] = Query(None, description="Class ID filter"),
    subject_id: Optional[int] = Query(None, description="Subject ID filter"),
    teacher_id: Optional[int] = Query(None, description="Teacher ID filter"),
    student_id: Optional[int] = Query(None, description="Student ID filter"),
    attendance_date: Optional[date] = Query(None, alias="date", description="Specific date filter"),
    status: Optional[str] = Query(None, description="Attendance status filter: ALL, PRESENT, ABSENT, LATE, EXCUSED"),
    search: Optional[str] = Query(None, description="Student name or admission number search query"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=200, description="Page size"),
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = AdminAttendanceService(db)
    return service.get_records(
        academic_year=academic_year,
        month=month,
        year=year,
        start_date=start_date,
        end_date=end_date,
        class_id=class_id,
        subject_id=subject_id,
        teacher_id=teacher_id,
        student_id=student_id,
        status_filter=status,
        search=search,
        attendance_date=attendance_date,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/classes/{class_id}/report",
    response_model=AdminClassAttendanceReportResponse,
    summary="Get comprehensive class-based attendance report, student attendance percentages, and absence dates"
)
def get_class_attendance_report(
    class_id: int,
    subject_id: Optional[int] = Query(None, description="Subject ID filter"),
    teacher_id: Optional[int] = Query(None, description="Teacher ID filter"),
    academic_year: Optional[str] = Query(None, description="Academic year filter"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Month filter (1-12)"),
    year: Optional[int] = Query(None, description="Year filter"),
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    attendance_date: Optional[date] = Query(None, alias="date", description="Specific date filter"),
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = AdminAttendanceService(db)
    return service.get_class_report(
        class_id=class_id,
        subject_id=subject_id,
        teacher_id=teacher_id,
        academic_year=academic_year,
        month=month,
        year=year,
        start_date=start_date,
        end_date=end_date,
        attendance_date=attendance_date,
    )


@router.get(
    "/frequent-absences",
    response_model=List[AdminAttendanceFrequentAbsenteeItem],
    summary="Get ranked list of students with frequent absences exceeding threshold"
)
def get_frequent_absences(
    class_id: Optional[int] = Query(None, description="Class ID filter"),
    subject_id: Optional[int] = Query(None, description="Subject ID filter"),
    teacher_id: Optional[int] = Query(None, description="Teacher ID filter"),
    academic_year: Optional[str] = Query(None, description="Academic year filter"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Month filter (1-12)"),
    year: Optional[int] = Query(None, description="Year filter"),
    threshold: int = Query(3, ge=1, description="Absence count threshold"),
    percentage_threshold: Optional[float] = Query(None, ge=0.0, le=100.0, description="Attendance percentage threshold"),
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = AdminAttendanceService(db)
    return service.get_frequent_absentees(
        class_id=class_id,
        subject_id=subject_id,
        teacher_id=teacher_id,
        academic_year=academic_year,
        month=month,
        year=year,
        threshold=threshold,
        percentage_threshold=percentage_threshold,
    )


@router.get(
    "/students/{student_id}/breakdown",
    response_model=StudentAttendanceHistoryDetailResponse,
    summary="Get detailed subject-by-subject attendance breakdown and history for any student across school"
)
@router.get(
    "/students/{student_id}/history",
    response_model=StudentAttendanceHistoryDetailResponse,
    include_in_schema=False
)
def get_student_attendance_breakdown(
    student_id: int,
    academic_year: Optional[str] = Query(None, description="Academic Year filter"),
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = AdminAttendanceService(db)
    return service.get_student_breakdown(
        student_id=student_id,
        academic_year=academic_year
    )


@router.get(
    "/export/excel",
    summary="Export class attendance report or frequent absentees to styled Excel (.xlsx)"
)
def export_attendance_excel(
    report_type: str = Query("class_report", description="Report type: 'class_report' or 'frequent_absentees'"),
    class_id: Optional[int] = Query(None, description="Class ID (required for class_report)"),
    subject_id: Optional[int] = Query(None, description="Subject ID filter"),
    teacher_id: Optional[int] = Query(None, description="Teacher ID filter"),
    academic_year: Optional[str] = Query(None, description="Academic year filter"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Month filter"),
    year: Optional[int] = Query(None, description="Year filter"),
    threshold: int = Query(3, ge=1, description="Absence count threshold"),
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    if report_type == "class_report" and not class_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="class_id is required for class_report export.")

    service = AdminAttendanceService(db)
    excel_bytes = service.export_excel(
        report_type=report_type,
        class_id=class_id,
        subject_id=subject_id,
        teacher_id=teacher_id,
        academic_year=academic_year,
        month=month,
        year=year,
        threshold=threshold,
    )

    safe_year = (academic_year or "current").replace("/", "-")
    prefix = f"Class_{class_id}_Attendance" if report_type == "class_report" else "Frequent_Absentees"
    if subject_id:
        prefix += f"_Subj_{subject_id}"
    filename = f"{prefix}_{safe_year}_{date.today().isoformat()}.xlsx"

    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get(
    "/export/pdf",
    summary="Download print-ready official PDF attendance report"
)
def export_attendance_pdf(
    report_type: str = Query("class_report", description="Report type: 'class_report' or 'frequent_absentees'"),
    class_id: Optional[int] = Query(None, description="Class ID (required for class_report)"),
    subject_id: Optional[int] = Query(None, description="Subject ID filter"),
    teacher_id: Optional[int] = Query(None, description="Teacher ID filter"),
    academic_year: Optional[str] = Query(None, description="Academic year filter"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Month filter"),
    year: Optional[int] = Query(None, description="Year filter"),
    threshold: int = Query(3, ge=1, description="Absence count threshold"),
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    if report_type == "class_report" and not class_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="class_id is required for class_report export.")

    service = AdminAttendanceService(db)
    pdf_bytes = service.export_pdf(
        report_type=report_type,
        class_id=class_id,
        subject_id=subject_id,
        teacher_id=teacher_id,
        academic_year=academic_year,
        month=month,
        year=year,
        threshold=threshold,
    )

    safe_year = (academic_year or "current").replace("/", "-")
    prefix = f"Class_{class_id}_Attendance" if report_type == "class_report" else "Frequent_Absentees"
    if subject_id:
        prefix += f"_Subj_{subject_id}"
    filename = f"{prefix}_{safe_year}_{date.today().isoformat()}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

