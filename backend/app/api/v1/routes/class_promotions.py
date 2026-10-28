from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies.database import get_db
from app.api.dependencies.auth import get_current_active_admin
from app.models.user import User
from app.services.class_promotion_service import ClassPromotionService
from app.schemas.class_promotion import (
    SuggestedMappingsResponse,
    PromotionPreviewRequest,
    BulkPromotionPreviewResponse,
    ExecuteBulkPromotionPayload,
    IndividualClassChangePayload,
    IndividualClassChangeResponse,
    ClassLevelPromotionPayload,
    IndividualStudentPromotionPayload,
    StudentSearchForPromotionItem,
    PromotionBatchResponse,
    BatchRollbackResponse,
)

router = APIRouter(prefix="/class-promotions", tags=["Class Promotion & Changes"])


@router.get(
    "/suggested-mappings",
    response_model=SuggestedMappingsResponse,
    summary="Get auto-generated class promotion mappings with section preservation (Admin only)"
)
def get_suggested_mappings(
    source_year: Optional[str] = Query(None, description="Source academic year e.g. 2026/2027"),
    target_year: Optional[str] = Query(None, description="Target academic year e.g. 2027/2028"),
    education_level: Optional[str] = Query(None, description="Filter level: PRIMARY or SECONDARY"),
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = ClassPromotionService(db)
    return service.get_suggested_mappings(
        source_year=source_year,
        target_year=target_year,
        education_level=education_level
    )


@router.post(
    "/preview",
    response_model=BulkPromotionPreviewResponse,
    summary="Preview and validate bulk, class, or student promotion before execution (Admin only)"
)
def preview_bulk_promotion(
    payload: PromotionPreviewRequest,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = ClassPromotionService(db)
    return service.preview_bulk_promotion(payload)


@router.post(
    "/bulk",
    response_model=PromotionBatchResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Execute bulk promotion in ONE atomic database transaction (Admin only)"
)
def execute_bulk_promotion(
    payload: ExecuteBulkPromotionPayload,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = ClassPromotionService(db)
    return service.execute_bulk_promotion(payload, admin_user=current_admin)


@router.post(
    "/class-level",
    response_model=PromotionBatchResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Promote all eligible students in a single class to a new class (Admin only)"
)
def execute_class_level_promotion(
    payload: ClassLevelPromotionPayload,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = ClassPromotionService(db)
    return service.execute_class_level_promotion(payload, admin_user=current_admin)


@router.post(
    "/individual-promote",
    response_model=PromotionBatchResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Promote, repeat, transfer, or graduate an individual student (Admin only)"
)
def execute_individual_student_promotion(
    payload: IndividualStudentPromotionPayload,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = ClassPromotionService(db)
    return service.execute_individual_student_promotion(payload, admin_user=current_admin)


@router.get(
    "/students/search",
    response_model=List[StudentSearchForPromotionItem],
    summary="Search students for promotion with suggested next class (Admin only)"
)
def search_students_for_promotion(
    q: Optional[str] = Query(None, description="Search query: name or admission number"),
    class_id: Optional[int] = Query(None, description="Filter by class ID"),
    education_level: Optional[str] = Query(None, description="PRIMARY or SECONDARY"),
    academic_year: Optional[str] = Query(None, description="Academic year"),
    limit: int = Query(50, ge=1, le=100),
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = ClassPromotionService(db)
    return service.search_students_for_promotion(
        q=q,
        class_id=class_id,
        education_level=education_level,
        academic_year=academic_year,
        limit=limit
    )


@router.post(
    "/students/{student_id}/change-class",
    response_model=IndividualClassChangeResponse,
    status_code=status.HTTP_200_OK,
    summary="Change an individual student's class with historical record preservation (Admin only)"
)
def change_student_class(
    student_id: int,
    payload: IndividualClassChangePayload,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = ClassPromotionService(db)
    return service.execute_individual_class_change(
        student_id=student_id,
        payload=payload,
        admin_user=current_admin
    )


@router.get(
    "/history",
    response_model=List[PromotionBatchResponse],
    summary="Get promotion batches and audit history (Admin only)"
)
def list_promotion_history(
    academic_year: Optional[str] = Query(None, description="Filter by source or target academic year"),
    promotion_type: Optional[str] = Query(None, description="Filter by type: BULK_PROMOTION, CLASS_LEVEL, INDIVIDUAL_PROMOTION, INDIVIDUAL_CHANGE"),
    status: Optional[str] = Query(None, description="Filter by status: COMPLETED, ROLLED_BACK"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = ClassPromotionService(db)
    batches, _ = service.list_batches(
        academic_year=academic_year,
        promotion_type=promotion_type,
        status=status,
        skip=skip,
        limit=limit
    )
    return batches


@router.get(
    "/history/{batch_id}",
    response_model=PromotionBatchResponse,
    summary="Get full details and student records for a promotion batch (Admin only)"
)
def get_promotion_batch_details(
    batch_id: int,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = ClassPromotionService(db)
    return service.get_batch_details(batch_id)


@router.post(
    "/history/{batch_id}/rollback",
    response_model=BatchRollbackResponse,
    summary="Safely rollback a promotion batch by ID (Admin only)"
)
def rollback_promotion_batch(
    batch_id: int,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = ClassPromotionService(db)
    return service.rollback_batch(batch_id=batch_id, admin_user=current_admin)
