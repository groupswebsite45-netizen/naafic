from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException, Response
from sqlalchemy.orm import Session
from app.api.dependencies.database import get_db
from app.api.dependencies.auth import (
    get_current_user,
    get_current_active_admin,
    get_current_active_teacher,
    get_current_active_student,
)
from app.models.user import User
from app.models.student import Student
from app.services.result_workflow_service import ResultWorkflowService
from app.services.pdf_report_service import PDFReportService
from app.services.excel_export_service import ExcelExportService
from app.schemas.result_workflow import (
    ResultOverviewStats,
    ClassResultSummaryItem,
    ClassResultDashboardResponse,
    ClassReceiptSummary,
    TeacherSubmissionItem,
    TeacherAccountabilitySummary,
    SubmissionReviewDetail,
    TeacherSaveDraftPayload,
    TeacherSubmitPayload,
    ReturnSubmissionPayload,
    ApproveSubmissionPayload,
    ReleaseClassResultsPayload,
    RecordStudentViewPayload,
    TeacherExamAssignmentItem,
)
from app.schemas.exam import ExamResultResponse

router = APIRouter(prefix="/results", tags=["Examination Result Management & Workflow"])


# =============================================================================
# FILTER & OVERVIEW ENDPOINTS
# =============================================================================

@router.get(
    "/filter-options",
    summary="Get available academic years, exams, teachers, classes, and subjects for scoping"
)
def get_filter_options(
    academic_year: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from app.models.teacher import Teacher
    from app.services.class_service import ClassService

    service = ResultWorkflowService(db)
    class_service = ClassService(db)

    years = service.sub_repo.get_filter_academic_years()
    selected_year = academic_year or (years[0] if years else "2026/2027")
    exams = service.sub_repo.get_exam_series_for_year(selected_year)
    teachers = db.query(Teacher).filter(Teacher.status == "ACTIVE").order_by(Teacher.first_name).all()

    # Use active-classes-with-students rule for dropdowns
    active_classes = class_service.get_active_classes_with_students(academic_year=selected_year)

    from app.models.subject import Subject
    subjects = db.query(Subject).filter(Subject.status == "ACTIVE").order_by(Subject.name).all()

    return {
        "academic_years": years,
        "selected_academic_year": selected_year,
        "exam_names": exams if exams else [],
        "teachers": [{"id": t.id, "name": t.full_name, "email": t.email} for t in teachers],
        "classes": [{"id": c.id, "name": c.name, "code": c.code, "division": c.division, "students_count": c.students_count} for c in active_classes],
        "subjects": [{"id": s.id, "name": s.name, "code": s.code} for s in subjects],
    }



@router.get(
    "/overview",
    response_model=ResultOverviewStats,
    summary="Get top-level result statistics from PostgreSQL"
)
def get_result_overview(
    academic_year: str = Query(..., description="e.g., 2025-2026"),
    exam_name: str = Query(..., description="e.g., Final Examination"),
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = ResultWorkflowService(db)
    return service.sub_repo.get_overview_stats(academic_year, exam_name)


# =============================================================================
# ADMIN CLASS-FIRST RESULT MONITORING & MATRIX
# =============================================================================

@router.get(
    "/classes",
    response_model=List[ClassResultSummaryItem],
    summary="Get all classes with result completion summaries for academic year & exam"
)
def get_classes_result_summary(
    academic_year: str = Query(...),
    exam_name: str = Query(...),
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = ResultWorkflowService(db)
    return service.sub_repo.get_classes_summary(academic_year, exam_name)


@router.get(
    "/classes/{class_id}",
    response_model=ClassResultDashboardResponse,
    summary="Get Class Result Dashboard & Subject Matrix"
)
def get_class_result_detail(
    class_id: int,
    academic_year: str = Query(...),
    exam_name: str = Query(...),
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = ResultWorkflowService(db)
    data = service.sub_repo.get_class_dashboard(class_id, academic_year, exam_name)
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class result data not found.")
    return data


@router.post(
    "/classes/{class_id}/release",
    summary="Release results by class (Admin only)"
)
def release_class_results(
    class_id: int,
    payload: ReleaseClassResultsPayload,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    payload.class_id = class_id
    service = ResultWorkflowService(db)
    return service.release_class_results(current_admin, payload)


@router.get(
    "/classes/{class_id}/receipt",
    response_model=ClassReceiptSummary,
    summary="Get Student Result Receipt and Visibility Verification"
)
def get_class_receipt_status(
    class_id: int,
    academic_year: str = Query(...),
    exam_name: str = Query(...),
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = ResultWorkflowService(db)
    return service.rel_repo.get_class_receipt_status(class_id, academic_year, exam_name)


# =============================================================================
# ADMIN TEACHER SUBMISSION DASHBOARD
# =============================================================================

@router.get(
    "/submissions",
    response_model=List[TeacherSubmissionItem],
    summary="Admin Teacher Submissions Monitoring list with filters"
)
def list_teacher_submissions(
    academic_year: Optional[str] = None,
    exam_name: Optional[str] = None,
    exam_type: Optional[str] = None,
    teacher_id: Optional[int] = None,
    class_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = ResultWorkflowService(db)
    return service.sub_repo.get_teacher_submissions(
        academic_year=academic_year,
        exam_name=exam_name,
        exam_type=exam_type,
        teacher_id=teacher_id,
        class_id=class_id,
        subject_id=subject_id,
        status=status_filter
    )


@router.get(
    "/submissions/{submission_id}",
    response_model=SubmissionReviewDetail,
    summary="Get full submission detail for Admin review"
)
def get_submission_detail(
    submission_id: int,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = ResultWorkflowService(db)
    data = service.sub_repo.get_submission_detail(submission_id)
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found.")
    return data


@router.post(
    "/submissions/{submission_id}/approve",
    summary="Admin approves submitted marks"
)
def approve_submission(
    submission_id: int,
    payload: ApproveSubmissionPayload,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = ResultWorkflowService(db)
    return service.approve_submission(current_admin, submission_id, payload)


@router.post(
    "/submissions/{submission_id}/return",
    summary="Admin returns submission to teacher for correction"
)
def return_submission(
    submission_id: int,
    payload: ReturnSubmissionPayload,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = ResultWorkflowService(db)
    return service.return_submission(current_admin, submission_id, payload)


@router.post(
    "/submissions/{submission_id}/release",
    summary="Admin releases completed result set to students"
)
def release_submission(
    submission_id: int,
    payload: Optional[ApproveSubmissionPayload] = None,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = ResultWorkflowService(db)
    return service.release_submission(current_admin, submission_id, payload)


@router.get(
    "/teachers/{teacher_id}/accountability",
    response_model=TeacherAccountabilitySummary,
    summary="Get teacher result submission responsibilities summary"
)
def get_teacher_accountability(
    teacher_id: int,
    academic_year: Optional[str] = None,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = ResultWorkflowService(db)
    data = service.sub_repo.get_teacher_accountability(teacher_id, academic_year)
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found.")
    return data


# =============================================================================
# TEACHER RESULT PORTAL ENDPOINTS
# =============================================================================

@router.get(
    "/teacher/assignments",
    response_model=List[TeacherExamAssignmentItem],
    summary="Get assigned examination streams for authenticated teacher"
)
def get_teacher_assignments(
    current_teacher: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    service = ResultWorkflowService(db)
    return service.get_teacher_assigned_exams(current_teacher)


@router.get(
    "/teacher/exams/{exam_id}/roster",
    summary="Get student roster for teacher marks and attendance entry"
)
def get_teacher_exam_roster(
    exam_id: int,
    current_teacher: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    service = ResultWorkflowService(db)
    return service.get_teacher_roster_for_exam(current_teacher, exam_id)


@router.post(
    "/teacher/draft",
    summary="Teacher saves draft results without submitting"
)
def save_teacher_draft(
    payload: TeacherSaveDraftPayload,
    current_teacher: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    service = ResultWorkflowService(db)
    return service.save_teacher_draft(current_teacher, payload)


@router.post(
    "/teacher/submit",
    summary="Teacher formally submits marks to Admin for review"
)
def submit_teacher_results(
    payload: TeacherSubmitPayload,
    current_teacher: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    service = ResultWorkflowService(db)
    return service.submit_teacher_results(current_teacher, payload)


# =============================================================================
# STUDENT RESULT PORTAL ENDPOINTS
# =============================================================================

@router.get(
    "/student/my-results",
    response_model=List[ExamResultResponse],
    summary="Get only published/released results for authenticated student"
)
def get_student_released_results(
    current_student: User = Depends(get_current_active_student),
    db: Session = Depends(get_db)
):
    service = ResultWorkflowService(db)
    return service.get_student_released_results(current_student)


@router.post(
    "/student/record-view",
    summary="Record event when student inspects released results"
)
def record_student_view(
    payload: RecordStudentViewPayload,
    current_student: User = Depends(get_current_active_student),
    db: Session = Depends(get_db)
):
    service = ResultWorkflowService(db)
    return service.record_student_view_event(current_student, payload)


# =============================================================================
# ADVANCED RESULTS MANAGEMENT SYSTEM ENDPOINTS
# =============================================================================

@router.get(
    "/dashboard/statistics",
    summary="Get 10 real-time KPIs for Results Management Dashboard"
)
def get_dashboard_statistics(
    academic_year: str = Query(...),
    exam_name: str = Query(...),
    division: Optional[str] = Query(None),
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = ResultWorkflowService(db)
    return service.sub_repo.get_dashboard_statistics(academic_year, exam_name, division)


@router.get(
    "/classes/{class_id}/sheet",
    summary="Get complete Class Result Sheet matrix and summary statistics"
)
def get_class_result_sheet(
    class_id: int,
    academic_year: str = Query(...),
    exam_name: str = Query(...),
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = ResultWorkflowService(db)
    data = service.sub_repo.get_class_result_sheet(class_id, academic_year, exam_name)
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class result sheet not found.")
    return data


@router.get(
    "/classes/{class_id}/sheet/pdf",
    summary="Download complete Class Result Sheet as landscape print-ready PDF"
)
def download_class_result_sheet_pdf(
    class_id: int,
    academic_year: str = Query(...),
    exam_name: str = Query(...),
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = ResultWorkflowService(db)
    data = service.sub_repo.get_class_result_sheet(class_id, academic_year, exam_name)
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class result sheet not found.")

    pdf_service = PDFReportService()
    pdf_bytes = pdf_service.generate_class_result_sheet_pdf(data)

    c_code = data["class_info"]["code"] or f"Class_{class_id}"
    safe_year = academic_year.replace("/", "-")
    filename = f"Class_Result_Sheet_{c_code}_{safe_year}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get(
    "/classes/{class_id}/rankings",
    summary="Get Class Rankings & Merit List with competition ranking (1, 2, 2, 4)"
)
def get_class_rankings(
    class_id: int,
    academic_year: str = Query(...),
    exam_name: str = Query(...),
    division: Optional[str] = Query(None),
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = ResultWorkflowService(db)
    target_class_id = class_id if class_id > 0 else None
    return service.sub_repo.get_class_rankings(target_class_id, academic_year, exam_name, division)


@router.get(
    "/classes/{class_id}/rankings/pdf",
    summary="Download Class Rankings & Merit List as print-ready PDF"
)
def download_class_rankings_pdf(
    class_id: int,
    academic_year: str = Query(...),
    exam_name: str = Query(...),
    division: Optional[str] = Query(None),
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = ResultWorkflowService(db)
    target_class_id = class_id if class_id > 0 else None
    data = service.sub_repo.get_class_rankings(target_class_id, academic_year, exam_name, division)

    pdf_service = PDFReportService()
    pdf_bytes = pdf_service.generate_class_ranking_pdf(data)

    c_name = data["class_info"]["name"].replace(" ", "_")
    safe_year = academic_year.replace("/", "-")
    filename = f"Class_Rankings_{c_name}_{safe_year}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get(
    "/classes/{class_id}/rankings/excel",
    summary="Download Class Rankings & Merit List as styled Excel (.xlsx) spreadsheet"
)
def download_class_rankings_excel(
    class_id: int,
    academic_year: str = Query(...),
    exam_name: str = Query(...),
    division: Optional[str] = Query(None),
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = ResultWorkflowService(db)
    target_class_id = class_id if class_id > 0 else None
    data = service.sub_repo.get_class_rankings(target_class_id, academic_year, exam_name, division)

    excel_service = ExcelExportService()
    excel_bytes = excel_service.generate_class_ranking_excel(data)

    c_name = data["class_info"]["name"].replace(" ", "_")
    safe_year = academic_year.replace("/", "-")
    filename = f"Class_Rankings_{c_name}_{safe_year}.xlsx"
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get(
    "/students/{student_id}/report",
    summary="Get individual student result report/transcript"
)
def get_student_result_report(
    student_id: int,
    academic_year: str = Query(...),
    exam_name: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    is_admin = current_user.has_role("ADMIN") or current_user.has_role("SUPERADMIN")
    is_student = current_user.has_role("STUDENT")

    if is_admin:
        only_published = False
    elif is_student:
        std = db.query(Student).filter(Student.user_id == current_user.id).first()
        if not std or std.id != student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to view another student's report."
            )
        only_published = True
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized access to student results."
        )

    service = ResultWorkflowService(db)
    data = service.sub_repo.get_student_result_report(student_id, academic_year, exam_name, only_published=only_published)
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student result report not found.")
    return data


@router.get(
    "/students/{student_id}/report/pdf",
    summary="Download individual student academic report card as PDF"
)
def download_student_report_card_pdf(
    student_id: int,
    academic_year: str = Query(...),
    exam_name: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    is_admin = current_user.has_role("ADMIN") or current_user.has_role("SUPERADMIN")
    is_student = current_user.has_role("STUDENT")

    if is_admin:
        only_published = False
    elif is_student:
        std = db.query(Student).filter(Student.user_id == current_user.id).first()
        if not std or std.id != student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to download another student's report."
            )
        only_published = True
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized access to student results."
        )

    service = ResultWorkflowService(db)
    data = service.sub_repo.get_student_result_report(student_id, academic_year, exam_name, only_published=only_published)
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student result report not found.")

    pdf_service = PDFReportService()
    pdf_bytes = pdf_service.generate_student_report_card_pdf(data)

    adm_no = data["student"]["admission_number"].replace("/", "-")
    safe_year = academic_year.replace("/", "-")
    filename = f"Report_Card_{adm_no}_{safe_year}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get(
    "/subject-performance",
    summary="Get subject-by-subject performance analysis across classes"
)
def get_subject_performance_list(
    academic_year: str = Query(...),
    exam_name: str = Query(...),
    class_id: Optional[int] = Query(None),
    subject_id: Optional[int] = Query(None),
    division: Optional[str] = Query(None),
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = ResultWorkflowService(db)
    return service.sub_repo.get_subject_performance_list(
        academic_year, exam_name, class_id=class_id, subject_id=subject_id, division=division
    )


@router.get(
    "/absent-students",
    summary="Get absent students tracker with recorded absence reasons and complaints"
)
def get_absent_students_list(
    academic_year: str = Query(...),
    exam_name: str = Query(...),
    class_id: Optional[int] = Query(None),
    subject_id: Optional[int] = Query(None),
    division: Optional[str] = Query(None),
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = ResultWorkflowService(db)
    return service.sub_repo.get_absent_students_list(
        academic_year, exam_name, class_id=class_id, subject_id=subject_id, division=division
    )

