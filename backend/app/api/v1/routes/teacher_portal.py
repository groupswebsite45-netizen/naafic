from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, status, UploadFile, File, Body
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.api.dependencies.database import get_db
from app.api.dependencies.auth import get_current_active_teacher
from app.models.user import User
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.models.teacher_assignment import TeacherAssignment
from app.services.teacher_portal_service import TeacherPortalService
from app.schemas.teacher_portal import (
    TeacherDashboardResponse,
    TeacherClassStudentsResponse,
    TeacherClassDetailResponse,
    TeacherExamItemResponse,
    TeacherExamRosterResponse,
    TeacherIdentityResponse,
    TeacherPortalProfileResponse,
)
from app.schemas.teacher import TeacherAssignmentResponse
from app.schemas.timetable import TimetableResponse
from app.schemas.exam import ExamResponse, BulkExamResultsCreate, ExamResultResponse, ExamCreate

router = APIRouter(prefix="/teacher-portal", tags=["Teacher Portal"])
teacher_alias_router = APIRouter(prefix="/teacher", tags=["Teacher Identity & Assignments"])


@router.get(
    "/me",
    response_model=TeacherIdentityResponse,
    summary="Get canonical teacher identity for authenticated teacher"
)
@teacher_alias_router.get(
    "/me",
    response_model=TeacherIdentityResponse,
    summary="Get canonical teacher identity for authenticated teacher"
)
def get_teacher_me(
    current_teacher_user: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    service = TeacherPortalService(db)
    return service.get_teacher_me(current_teacher_user)


@router.get(
    "/profile",
    response_model=TeacherPortalProfileResponse,
    summary="Get complete teacher portal profile including active assignments"
)
@teacher_alias_router.get(
    "/profile",
    response_model=TeacherPortalProfileResponse,
    summary="Get complete teacher portal profile including active assignments"
)
def get_teacher_profile(
    current_teacher_user: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    service = TeacherPortalService(db)
    return service.get_profile(current_teacher_user)


@router.get(
    "/subjects",
    summary="Get assigned subjects for authenticated teacher"
)
@teacher_alias_router.get(
    "/subjects",
    summary="Get assigned subjects for authenticated teacher"
)
def get_teacher_subjects(
    academic_year: Optional[str] = Query(None),
    current_teacher_user: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    service = TeacherPortalService(db)
    return service.get_teacher_subjects(current_teacher_user, academic_year=academic_year)


@teacher_alias_router.get(
    "/assignments",
    response_model=List[TeacherAssignmentResponse],
    summary="Get assigned classes and subjects for authenticated teacher (canonical alias)"
)
def get_teacher_assignments_alias(
    academic_year: Optional[str] = Query(None, description="Optional filter by academic year"),
    current_teacher_user: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    service = TeacherPortalService(db)
    return service.get_my_classes(current_teacher_user, academic_year=academic_year)


@teacher_alias_router.get(
    "/classes",
    response_model=List[TeacherAssignmentResponse],
    summary="Get assigned classes and subjects for authenticated teacher"
)
def get_teacher_classes_alias(
    academic_year: Optional[str] = Query(None, description="Optional filter by academic year"),
    current_teacher_user: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    service = TeacherPortalService(db)
    return service.get_my_classes(current_teacher_user, academic_year=academic_year)


@router.get(
    "/dashboard",
    response_model=TeacherDashboardResponse,
    summary="Get teacher portal dashboard telemetry and schedule"
)
def get_dashboard(
    current_teacher_user: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    service = TeacherPortalService(db)
    return service.get_dashboard(current_teacher_user)


@router.get(
    "/classes",
    response_model=List[TeacherAssignmentResponse],
    summary="Get assigned classes and subjects for authenticated teacher"
)
def get_my_classes(
    academic_year: Optional[str] = Query(None, description="Optional filter by academic year"),
    current_teacher_user: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    service = TeacherPortalService(db)
    return service.get_my_classes(current_teacher_user, academic_year=academic_year)


@router.get(
    "/classes/{class_id}/detail",
    response_model=TeacherClassDetailResponse,
    summary="Get comprehensive class details for assigned teacher"
)
def get_class_detail(
    class_id: int,
    subject_id: Optional[int] = Query(None, description="Optional filter by subject id"),
    current_teacher_user: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    service = TeacherPortalService(db)
    return service.get_class_detail(current_teacher_user, class_id=class_id, subject_id=subject_id)


@router.get(
    "/classes/{class_id}/students",
    response_model=TeacherClassStudentsResponse,
    summary="Get students in an assigned class"
)
def get_class_students(
    class_id: int,
    current_teacher_user: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    service = TeacherPortalService(db)
    return service.get_students_in_class(current_teacher_user, class_id)


@router.get(
    "/students",
    summary="Get all assigned students across teacher's classes with search & filter"
)
def get_my_assigned_students(
    class_id: Optional[int] = Query(None, description="Filter by assigned class"),
    query: Optional[str] = Query(None, description="Search by name or admission number"),
    current_teacher_user: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    service = TeacherPortalService(db)
    teacher = service.get_authenticated_teacher(current_teacher_user)
    assignments = service.teacher_repo.get_teacher_assignments(teacher.id)

    assigned_class_ids = list(set(a.class_id for a in assignments))
    if not assigned_class_ids:
        return []

    target_class_ids = [class_id] if class_id and class_id in assigned_class_ids else assigned_class_ids

    stmt = db.query(
        Student.id.label("student_id"),
        Student.first_name,
        Student.middle_name,
        Student.last_name,
        Student.admission_number,
        Student.gender,
        StudentEnrollment.class_id,
        StudentEnrollment.academic_year
    ).join(
        StudentEnrollment,
        StudentEnrollment.student_id == Student.id
    ).filter(
        StudentEnrollment.class_id.in_(target_class_ids),
        StudentEnrollment.status == "ACTIVE",
        Student.status == "ACTIVE"
    )

    if query:
        search = f"%{query.strip()}%"
        stmt = stmt.filter(
            (Student.first_name.ilike(search)) |
            (Student.last_name.ilike(search)) |
            (Student.admission_number.ilike(search))
        )

    rows = stmt.order_by(Student.first_name.asc(), Student.last_name.asc()).all()
    classes_map = {a.class_id: a.school_class.name for a in assignments}

    results = []
    seen = set()
    for r in rows:
        key = (r.student_id, r.class_id)
        if key not in seen:
            seen.add(key)
            results.append({
                "student_id": r.student_id,
                "first_name": r.first_name,
                "middle_name": r.middle_name,
                "last_name": r.last_name,
                "full_name": f"{r.first_name} {r.last_name}".strip(),
                "admission_number": r.admission_number,
                "gender": r.gender,
                "class_id": r.class_id,
                "class_name": classes_map.get(r.class_id, f"Class {r.class_id}"),
                "academic_year": r.academic_year
            })

    return results


@router.get(
    "/timetable",
    response_model=List[TimetableResponse],
    summary="Get weekly timetable for authenticated teacher"
)
def get_my_timetable(
    current_teacher_user: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    service = TeacherPortalService(db)
    return service.get_my_timetable(current_teacher_user)


@router.get(
    "/exam-options",
    summary="Get available academic years, subjects, and classes for exam creation — strictly from teacher's active assignments"
)
@router.get(
    "/exam-assignments",
    summary="Alias for exam creation options"
)
@teacher_alias_router.get(
    "/exam-options",
    summary="Get available academic years, subjects, and classes for exam creation"
)
@teacher_alias_router.get(
    "/exam-assignments",
    summary="Alias for exam creation options"
)
def get_exam_creation_options(
    academic_year: Optional[str] = Query(None),
    subject_id: Optional[int] = Query(None, description="If provided, filter classes by this subject"),
    current_teacher_user: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    """
    Returns available options for the exam creation form.
    All options are strictly scoped to the authenticated teacher's active assignments.

    Flow:
      1. Fetch all active assignments for authenticated teacher.
      2. Extract distinct academic years from teacher's active assignments.
      3. Select active academic year: requested year (if teacher has assignments in it) or first available year.
      4. Filter teacher's assignments for this academic year.
      5. Extract distinct assigned subjects (de-duplicated).
      6. If subject_id provided: extract allowed classes where teacher teaches that subject in that year,
         verifying that the class is ACTIVE and has active enrolled students.
    """
    service = TeacherPortalService(db)
    teacher = service.get_authenticated_teacher(current_teacher_user)

    # 1. Fetch ALL active assignments for this teacher with active classes & subjects
    raw_assignments = db.query(TeacherAssignment).filter(
        TeacherAssignment.teacher_id == teacher.id,
        TeacherAssignment.status == "ACTIVE"
    ).all()

    all_assignments = [
        a for a in raw_assignments
        if a.school_class and a.school_class.status == "ACTIVE"
        and a.subject and a.subject.status == "ACTIVE"
    ]

    # 2. Canonical distinct academic years across all teacher's active assignments
    years_set = set()
    for a in all_assignments:
        norm_y = a.academic_year.replace("-", "/") if "-" in a.academic_year else a.academic_year
        years_set.add(norm_y)
    years = sorted(list(years_set), reverse=True)

    if not years:
        return {
            "academic_years": [],
            "selected_academic_year": None,
            "subjects": [],
            "classes": [],
            "teacher_id": teacher.id,
            "teacher_name": teacher.full_name
        }

    # 3. Determine selected academic year
    target_year = None
    if academic_year and academic_year.strip():
        y_req = academic_year.strip()
        y_req_variants = [y_req, y_req.replace("/", "-"), y_req.replace("-", "/")]
        for yr in years:
            if yr in y_req_variants:
                target_year = yr
                break

    if not target_year:
        target_year = years[0]

    # Filter assignments for selected year
    target_variants = [target_year, target_year.replace("/", "-"), target_year.replace("-", "/")]
    year_assignments = [a for a in all_assignments if a.academic_year in target_variants]

    # 4. De-duplicated subjects for this academic year
    seen_subj = set()
    subjects_list = []
    for a in year_assignments:
        if a.subject_id not in seen_subj and a.subject and a.subject.status == "ACTIVE":
            seen_subj.add(a.subject_id)
            subjects_list.append({
                "id": a.subject_id,
                "name": a.subject.name,
                "code": a.subject.code,
                "division": a.subject.division
            })
    subjects_list.sort(key=lambda x: x["name"])

    # 5. Cascading classes: strictly classes where teacher is assigned to teach the selected subject in this year
    if subject_id:
        class_assignments = [a for a in year_assignments if a.subject_id == subject_id]
    else:
        class_assignments = year_assignments

    seen_cls = set()
    classes_list = []
    for a in class_assignments:
        if a.class_id not in seen_cls and a.school_class and a.school_class.status == "ACTIVE":
            seen_cls.add(a.class_id)
            student_count = db.query(StudentEnrollment).filter(
                StudentEnrollment.class_id == a.class_id,
                StudentEnrollment.academic_year.in_(target_variants),
                StudentEnrollment.status == "ACTIVE"
            ).count()
            if student_count == 0:
                student_count = db.query(StudentEnrollment).filter(
                    StudentEnrollment.class_id == a.class_id,
                    StudentEnrollment.status == "ACTIVE"
                ).count()

            classes_list.append({
                "id": a.class_id,
                "name": a.school_class.name,
                "code": a.school_class.code,
                "division": a.school_class.division,
                "level": a.school_class.level,
                "section": a.school_class.section,
                "academic_year": a.school_class.academic_year,
                "student_count": student_count
            })
    classes_list.sort(key=lambda x: x["name"])

    return {
        "academic_years": years,
        "selected_academic_year": target_year,
        "subjects": subjects_list,
        "classes": classes_list,
        "teacher_id": teacher.id,
        "teacher_name": teacher.full_name
    }


@router.get(
    "/exams",
    response_model=List[TeacherExamItemResponse],
    summary="Get active examinations for teacher's assigned classes with submission telemetry"
)
@teacher_alias_router.get(
    "/exams",
    response_model=List[TeacherExamItemResponse],
    summary="Get active examinations for teacher's assigned classes with submission telemetry"
)
def get_my_exams(
    academic_year: Optional[str] = Query(None),
    class_id: Optional[int] = Query(None),
    subject_id: Optional[int] = Query(None),
    exam_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_teacher_user: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    service = TeacherPortalService(db)
    return service.get_my_exams(
        current_teacher_user,
        academic_year=academic_year,
        class_id=class_id,
        subject_id=subject_id,
        exam_type=exam_type,
        status_filter=status
    )


@router.post(
    "/exams",
    response_model=ExamResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Teacher creates a new examination for assigned class and subject"
)
@teacher_alias_router.post(
    "/exams",
    response_model=ExamResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Teacher creates a new examination for assigned class and subject"
)
def create_exam_as_teacher(
    payload: ExamCreate,
    current_teacher_user: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    service = TeacherPortalService(db)
    return service.create_exam(current_teacher_user, payload)


@router.get(
    "/exams/{exam_id}/roster",
    response_model=TeacherExamRosterResponse,
    summary="Get student roster with marks and attendance for an assigned exam"
)
@router.get(
    "/exams/{exam_id}",
    response_model=TeacherExamRosterResponse,
    summary="Get exam detail and roster"
)
@teacher_alias_router.get(
    "/exams/{exam_id}/roster",
    response_model=TeacherExamRosterResponse,
    summary="Get student roster with marks and attendance for an assigned exam"
)
@teacher_alias_router.get(
    "/exams/{exam_id}",
    response_model=TeacherExamRosterResponse,
    summary="Get exam detail and roster"
)
def get_exam_roster(
    exam_id: int,
    current_teacher_user: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    service = TeacherPortalService(db)
    return service.get_exam_roster(current_teacher_user, exam_id)


@router.post(
    "/exams/{exam_id}/draft",
    summary="Save draft exam results without submitting"
)
@router.put(
    "/exams/{exam_id}/draft",
    summary="Save draft exam results without submitting (PUT)"
)
@router.post(
    "/exams/{exam_id}/save-draft",
    summary="Save draft exam results without submitting (alias)"
)
@teacher_alias_router.post(
    "/exams/{exam_id}/draft",
    summary="Save draft exam results without submitting"
)
@teacher_alias_router.put(
    "/exams/{exam_id}/draft",
    summary="Save draft exam results without submitting (PUT)"
)
@teacher_alias_router.post(
    "/exams/{exam_id}/save-draft",
    summary="Save draft exam results without submitting (alias)"
)
def save_exam_draft(
    exam_id: int,
    payload: Dict[str, Any] = Body(...),
    current_teacher_user: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    service = TeacherPortalService(db)
    results = payload.get("results") or payload.get("marks") or []
    return service.save_draft_results(current_teacher_user, exam_id, results)


@router.post(
    "/exams/{exam_id}/submit",
    summary="Submit exam results to Administration for review"
)
@teacher_alias_router.post(
    "/exams/{exam_id}/submit",
    summary="Submit exam results to Administration for review"
)
def submit_exam_results(
    exam_id: int,
    payload: Dict[str, Any] = Body(...),
    current_teacher_user: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    service = TeacherPortalService(db)
    results = payload.get("results", [])
    notes = payload.get("confirmation_notes")
    return service.submit_exam_results(current_teacher_user, exam_id, results, confirmation_notes=notes)


@router.post(
    "/exams/{exam_id}/recall",
    summary="Recall submitted results back to draft before Admin approval"
)
@teacher_alias_router.post(
    "/exams/{exam_id}/recall",
    summary="Recall submitted results back to draft before Admin approval"
)
def recall_exam_results(
    exam_id: int,
    current_teacher_user: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    service = TeacherPortalService(db)
    return service.recall_exam_results(current_teacher_user, exam_id)


@router.post(
    "/exams/{exam_id}/results",
    response_model=List[ExamResultResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Enter exam marks for assigned class students (Teacher only)"
)
def enter_exam_results(
    exam_id: int,
    payload: BulkExamResultsCreate,
    current_teacher_user: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    service = TeacherPortalService(db)
    return service.enter_exam_results(current_teacher_user, exam_id, payload)


# =============================================================================
# EXAM PAPER ATTACHMENT ENDPOINTS
# =============================================================================

@router.post(
    "/exams/{exam_id}/students/{student_id}/paper",
    summary="Upload optional exam paper/document for a student result"
)
async def upload_exam_paper(
    exam_id: int,
    student_id: int,
    file: UploadFile = File(...),
    current_teacher_user: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    service = TeacherPortalService(db)
    return await service.upload_exam_paper(current_teacher_user, exam_id, student_id, file)


@router.get(
    "/exams/{exam_id}/students/{student_id}/paper",
    summary="Download or view uploaded exam paper document"
)
def get_exam_paper(
    exam_id: int,
    student_id: int,
    current_teacher_user: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    service = TeacherPortalService(db)
    paper_info = service.get_exam_paper_file(current_teacher_user, exam_id, student_id)
    return FileResponse(
        path=paper_info["full_path"],
        filename=paper_info["original_name"],
        media_type=paper_info["mime_type"]
    )


@router.delete(
    "/exams/{exam_id}/students/{student_id}/paper",
    summary="Remove uploaded exam paper document before final submission"
)
def delete_exam_paper(
    exam_id: int,
    student_id: int,
    current_teacher_user: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    service = TeacherPortalService(db)
    return service.delete_exam_paper(current_teacher_user, exam_id, student_id)

