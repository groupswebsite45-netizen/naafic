from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies.database import get_db
from app.api.dependencies.auth import get_current_active_admin, get_current_user
from app.models.user import User
from app.services.exam_service import ExamService
from app.schemas.exam import (
    ExamCreate,
    ExamBatchCreate,
    ExamUpdate,
    ExamResponse,
    ExamSummary,
    ExamFilterOptions,
    ExamDetailResponse,
    BulkExamResultsCreate,
    ExamResultResponse,
    PublishResultsPayload,
    ExamConflictCheckRequest,
    ExamConflictCheckResponse,
    ReportCardResponse,
    DeadlineExtendRequest,
    ExamReopenRequest,
    ExamStatusUpdateRequest,
)

router = APIRouter(prefix="/exams", tags=["Exams & Results"])


@router.get(
    "/summary",
    response_model=ExamSummary,
    summary="Get aggregated exam statistics from PostgreSQL"
)
def get_exam_summary(
    academic_year: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ExamService(db)
    return service.get_summary(academic_year)


@router.get(
    "/filter-options",
    response_model=ExamFilterOptions,
    summary="Get available filter options from real exam data"
)
def get_filter_options(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ExamService(db)
    return service.get_filter_options()


@router.post(
    "/check-conflict",
    response_model=ExamConflictCheckResponse,
    summary="Check if a class has overlapping exam schedules"
)
def check_exam_conflict(
    payload: ExamConflictCheckRequest,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = ExamService(db)
    return service.check_conflicts(payload)


@router.get(
    "",
    response_model=List[ExamResponse],
    summary="List and search exams with filters"
)
def list_exams(
    query: Optional[str] = None,
    class_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    academic_year: Optional[str] = None,
    exam_type: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ExamService(db)
    exams, _ = service.search_exams(query, class_id, subject_id, academic_year, exam_type, status, skip, limit)
    return exams


@router.post(
    "",
    response_model=ExamResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new official exam (Admin only)"
)
def create_exam(
    payload: ExamCreate,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = ExamService(db)
    return service.create_exam(payload, user_id=current_admin.id)


@router.post(
    "/batch",
    response_model=List[ExamResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Batch exam creation across classes and subjects (Admin only)"
)
def create_batch_exams(
    payload: ExamBatchCreate,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = ExamService(db)
    return service.create_batch_exams(payload, user_id=current_admin.id)


@router.get(
    "/{exam_id}/profile",
    summary="Get complete exam profile with student marks sheet"
)
def get_exam_profile(
    exam_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ExamService(db)
    return service.get_exam_profile(exam_id)


@router.get(
    "/{exam_id}/report-card/{student_id}",
    response_model=ReportCardResponse,
    summary="Get official Hawlwadaag School report card data for a student"
)
def get_student_report_card(
    exam_id: int,
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ExamService(db)
    return service.get_student_report_card(exam_id, student_id)


@router.get(
    "/{exam_id}",
    response_model=ExamResponse,
    summary="Get exam by ID"
)
def get_exam(
    exam_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ExamService(db)
    return service.get_exam(exam_id)


@router.put(
    "/{exam_id}",
    response_model=ExamResponse,
    summary="Update exam details (Admin only)"
)
def update_exam(
    exam_id: int,
    payload: ExamUpdate,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = ExamService(db)
    return service.update_exam(exam_id, payload, user_id=current_admin.id)


@router.delete(
    "/{exam_id}",
    summary="Delete exam (Admin only)"
)
def delete_exam(
    exam_id: int,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = ExamService(db)
    service.delete_exam(exam_id, user_id=current_admin.id)
    return {"success": True, "message": "Examination deleted successfully."}


@router.post(
    "/{exam_id}/extend-deadline",
    response_model=ExamResponse,
    summary="Extend result submission deadline (Admin only)"
)
def extend_deadline(
    exam_id: int,
    payload: DeadlineExtendRequest,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = ExamService(db)
    return service.extend_deadline(
        exam_id=exam_id,
        new_deadline=payload.new_deadline,
        reason=payload.reason,
        user_id=current_admin.id
    )


@router.post(
    "/{exam_id}/reopen",
    response_model=ExamResponse,
    summary="Reopen results submission for an exam (Admin only)"
)
def reopen_submissions(
    exam_id: int,
    payload: ExamReopenRequest,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = ExamService(db)
    return service.reopen_submissions(
        exam_id=exam_id,
        new_deadline=payload.new_deadline,
        reason=payload.reason,
        user_id=current_admin.id
    )


@router.patch(
    "/{exam_id}/status",
    response_model=ExamResponse,
    summary="Update exam status (Admin only)"
)
def update_exam_status(
    exam_id: int,
    payload: ExamStatusUpdateRequest,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = ExamService(db)
    return service.update_status(exam_id, payload.status, user_id=current_admin.id)


@router.get(
    "/{exam_id}/results",
    response_model=List[ExamResultResponse],
    summary="Get student results for an exam"
)
def get_exam_results(
    exam_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ExamService(db)
    return service.get_exam_results(exam_id)


@router.post(
    "/{exam_id}/results",
    response_model=List[ExamResultResponse],
    status_code=status.HTTP_403_FORBIDDEN,
    summary="Enter or update exam results in bulk (Forbidden for Admin - Marks entered by teachers)"
)
def enter_bulk_results(
    exam_id: int,
    payload: BulkExamResultsCreate,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Administrators cannot enter or modify examination marks. Results must be submitted by assigned teachers."
    )


@router.post(
    "/{exam_id}/publish",
    response_model=ExamResponse,
    summary="Publish or unpublish exam results (Admin only)"
)
def publish_results(
    exam_id: int,
    payload: PublishResultsPayload,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = ExamService(db)
    return service.publish_results(exam_id, payload, user_id=current_admin.id)


@router.post(
    "/{exam_id}/dispatch-to-teachers",
    summary="Release/route scheduled exam to assigned faculty teachers for marks entry (Admin only)"
)
def dispatch_to_teachers(
    exam_id: int,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = ExamService(db)
    return service.dispatch_to_teachers(exam_id, user_id=current_admin.id)

