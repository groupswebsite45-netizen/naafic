from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies.database import get_db
from app.api.dependencies.auth import get_current_active_student
from app.models.user import User
from app.services.student_portal_service import StudentPortalService
from app.schemas.student_portal import (
    StudentDashboardResponse,
    StudentProfileResponse,
    StudentClassDetailsResponse,
    StudentFeesPortalResponse,
    StudentPublishedExamItem,
)
from app.schemas.attendance import StudentAttendancePortalResponse
from app.schemas.timetable import TimetableResponse
from app.schemas.exam import ExamResultResponse
from app.schemas.result_workflow import RecordStudentViewPayload

router = APIRouter(prefix="/student-portal", tags=["Student Portal"])


@router.get(
    "/dashboard",
    response_model=StudentDashboardResponse,
    summary="Get authenticated student portal dashboard overview"
)
def get_dashboard(
    current_student_user: User = Depends(get_current_active_student),
    db: Session = Depends(get_db)
):
    """
    Returns dashboard overview data scoped strictly to the authenticated student:
    - Welcome details & enrollment status
    - 6 summary metrics (Class, Academic Year, Attendance, Fees, Latest Exam, Next Period)
    - Today's schedule
    - Recent officially released examination results
    """
    service = StudentPortalService(db)
    return service.get_dashboard(current_student_user)


@router.get(
    "/profile",
    response_model=StudentProfileResponse,
    summary="Get authenticated student read-only profile"
)
def get_profile(
    current_student_user: User = Depends(get_current_active_student),
    db: Session = Depends(get_db)
):
    """
    Returns the student's personal, guardian, and academic enrollment information.
    Note: Students have READ-ONLY access. Personal details cannot be modified via portal.
    """
    service = StudentPortalService(db)
    return service.get_profile(current_student_user)


@router.get(
    "/academic-years",
    response_model=List[str],
    summary="Get academic years for which the authenticated student has records"
)
def get_academic_years(
    current_student_user: User = Depends(get_current_active_student),
    db: Session = Depends(get_db)
):
    """
    Returns only academic years where the authenticated student was enrolled.
    """
    service = StudentPortalService(db)
    return service.get_academic_years(current_student_user)


@router.get(
    "/class",
    response_model=StudentClassDetailsResponse,
    summary="Get authenticated student enrolled class details, subjects, and history"
)
def get_my_class(
    academic_year: Optional[str] = Query(None, description="Filter by academic year e.g. 2026/2027"),
    current_student_user: User = Depends(get_current_active_student),
    db: Session = Depends(get_db)
):
    """
    Returns enrolled class information, section, class teacher, enrolled curriculum subjects
    with faculty assignments, and historical enrollment timeline.
    """
    service = StudentPortalService(db)
    return service.get_my_class_details(current_student_user, academic_year=academic_year)


@router.get(
    "/subjects",
    summary="Get enrolled curriculum subjects for authenticated student"
)
def get_my_subjects(
    academic_year: Optional[str] = Query(None, description="Filter by academic year e.g. 2026/2027"),
    current_student_user: User = Depends(get_current_active_student),
    db: Session = Depends(get_db)
):
    service = StudentPortalService(db)
    details = service.get_my_class_details(current_student_user, academic_year=academic_year)
    return details.subjects


@router.get(
    "/timetable",
    response_model=List[TimetableResponse],
    summary="Get weekly class timetable schedule for authenticated student"
)
def get_my_timetable(
    academic_year: Optional[str] = Query(None, description="Filter by academic year"),
    current_student_user: User = Depends(get_current_active_student),
    db: Session = Depends(get_db)
):
    """
    Returns the weekly timetable periods for the student's enrolled class.
    """
    service = StudentPortalService(db)
    return service.get_my_timetable(current_student_user, academic_year=academic_year)


@router.get(
    "/attendance",
    response_model=StudentAttendancePortalResponse,
    summary="Get attendance summary, subject breakdown, and history for authenticated student"
)
def get_my_attendance(
    academic_year: Optional[str] = Query(None, description="Filter by academic year e.g. 2026/2027"),
    month: Optional[int] = Query(None, description="Filter by month 1-12"),
    subject_id: Optional[int] = Query(None, description="Filter by subject ID"),
    status: Optional[str] = Query(None, description="Filter by status: PRESENT, ABSENT, EXCUSED"),
    current_student_user: User = Depends(get_current_active_student),
    db: Session = Depends(get_db)
):
    """
    Returns student's calculated attendance rate, attendance by subject, and detailed period log.
    All data is scoped strictly to authenticated student.
    """
    service = StudentPortalService(db)
    return service.get_my_attendance(
        current_student_user,
        academic_year=academic_year,
        month=month,
        subject_id=subject_id,
        status_filter=status
    )


@router.get(
    "/fees",
    response_model=StudentFeesPortalResponse,
    summary="Get fee invoices, payment receipts, and balance summary for authenticated student"
)
def get_my_fees(
    academic_year: Optional[str] = Query(None, description="Filter by academic year"),
    current_student_user: User = Depends(get_current_active_student),
    db: Session = Depends(get_db)
):
    """
    Returns student's fee ledger: total billed, total paid, outstanding balance,
    invoices breakdown with payment receipts.
    """
    service = StudentPortalService(db)
    return service.get_my_fees(current_student_user, academic_year=academic_year)


@router.get(
    "/exams",
    response_model=List[StudentPublishedExamItem],
    summary="Get published examinations and schedules for authenticated student's enrolled class"
)
@router.get(
    "/published-exams",
    response_model=List[StudentPublishedExamItem],
    summary="Get published examinations and schedules for authenticated student's enrolled class (Alias)"
)
def get_my_exams(
    academic_year: Optional[str] = Query(None, description="Filter by academic year"),
    current_student_user: User = Depends(get_current_active_student),
    db: Session = Depends(get_db)
):
    """
    CRITICAL GATE: Returns all examinations published by school administration for the
    student's currently enrolled class. Marks and scores remain strictly hidden until
    official results release.
    """
    service = StudentPortalService(db)
    return service.get_my_published_exams(current_student_user, academic_year=academic_year)


@router.get(
    "/results",
    response_model=List[ExamResultResponse],
    summary="Get officially released exam results/grades for authenticated student"
)
def get_my_results(
    academic_year: Optional[str] = Query(None, description="Filter by academic year"),
    current_student_user: User = Depends(get_current_active_student),
    db: Session = Depends(get_db)
):
    """
    CRITICAL GATE: Only returns results that have been officially RELEASED by school administration.
    Draft, submitted, and unreleased approved marks are strictly excluded.
    """
    service = StudentPortalService(db)
    return service.get_my_exam_results(current_student_user, academic_year=academic_year)


@router.post(
    "/exams/record-view",
    summary="Audit and track student viewing of officially released exam results"
)
def record_result_view(
    payload: RecordStudentViewPayload,
    current_student_user: User = Depends(get_current_active_student),
    db: Session = Depends(get_db)
):
    """
    Logs first_viewed_at and last_viewed_at in student_result_views for administrative audits.
    """
    service = StudentPortalService(db)
    return service.record_result_view(
        current_student_user,
        exam_name=payload.exam_name,
        academic_year=payload.academic_year,
        class_id=payload.class_id
    )
