from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, Query, status, Response, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies.database import get_db
from app.api.dependencies.auth import get_current_active_admin, get_current_user
from app.models.user import User
from app.services.fee_service import FeeService
from app.schemas.fee import (
    FeeStructureCreate,
    FeeStructureUpdate,
    FeeStructureResponse,
    AssignFeePayload,
    AssignFeeResponse,
    FeePaymentCreate,
    FeePaymentResponse,
    OfficialReceiptData,
    StudentFeeResponse,
    PaginatedStudentFeeResponse,
    FeeFinancialSummaryResponse,
    ClassFinancialSummaryResponse,
    PaymentMethodSummaryResponse,
    MonthlyCollectionTrendResponse,
    FeeNotificationPreviewResponse,
    FeeNotificationSendRequest,
    FeeNotificationSendResponse,
    StudentFinancialProfileResponse,
    ClassStudentsFinancialResponse,
    OutstandingStudentsResponse,
    FeeEligibleStudentsResponse,
    FeeEligibleStudentItem,
)
from app.schemas.school_class import SchoolClassResponse

router = APIRouter(prefix="/fees", tags=["Fees & Financial Management"])


# =========================================================================
# 1. FINANCIAL DASHBOARD TELEMETRY & SUMMARIES
# =========================================================================

@router.get(
    "/summary",
    response_model=FeeFinancialSummaryResponse,
    summary="Get authoritative real-time financial telemetry KPIs from PostgreSQL"
)
def get_financial_summary(
    academic_year: Optional[str] = Query(None, description="Optional academic year filter"),
    education_level: Optional[str] = Query(None, description="PRIMARY or SECONDARY"),
    class_id: Optional[int] = Query(None, description="Optional class filter"),
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    service = FeeService(db)
    return service.get_financial_summary(
        academic_year=academic_year,
        education_level=education_level,
        class_id=class_id,
    )


@router.get(
    "/reports/class-summary",
    response_model=ClassFinancialSummaryResponse,
    summary="Get financial performance and collection rates grouped by class"
)
def get_class_financial_summary(
    academic_year: Optional[str] = Query(None),
    education_level: Optional[str] = Query(None),
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    service = FeeService(db)
    return service.get_class_financial_summary(
        academic_year=academic_year,
        education_level=education_level,
    )


@router.get(
    "/reports/payment-methods",
    response_model=PaymentMethodSummaryResponse,
    summary="Get payment collection breakdown grouped by payment method (EVC Plus, Cash, etc.)"
)
def get_payment_method_summary(
    academic_year: Optional[str] = Query(None),
    education_level: Optional[str] = Query(None),
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    service = FeeService(db)
    return service.get_payment_method_summary(
        academic_year=academic_year,
        education_level=education_level,
    )


@router.get(
    "/reports/collection-trends",
    response_model=MonthlyCollectionTrendResponse,
    summary="Get monthly revenue and collection velocity trends"
)
@router.get(
    "/reports/monthly-trends",
    response_model=MonthlyCollectionTrendResponse,
    summary="Get monthly revenue and collection velocity trends alias"
)
def get_monthly_collection_trends(
    academic_year: Optional[str] = Query(None),
    education_level: Optional[str] = Query(None),
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    service = FeeService(db)
    return service.get_monthly_collection_trends(
        academic_year=academic_year,
        education_level=education_level,
    )


# =========================================================================
# 2. FEE STRUCTURES
# =========================================================================

@router.get(
    "/structures",
    response_model=List[FeeStructureResponse],
    summary="List configured fee structures"
)
def list_fee_structures(
    academic_year: Optional[str] = Query(None),
    class_id: Optional[int] = Query(None),
    education_level: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = FeeService(db)
    return service.list_fee_structures(
        academic_year=academic_year,
        class_id=class_id,
        status_filter=status_filter,
        education_level=education_level,
    )


@router.post(
    "/structures",
    response_model=FeeStructureResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new fee structure item (Admin only)"
)
def create_fee_structure(
    payload: FeeStructureCreate,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    service = FeeService(db)
    return service.create_fee_structure(payload, user_id=current_admin.id)


@router.put(
    "/structures/{structure_id}",
    response_model=FeeStructureResponse,
    summary="Update an existing fee structure item (Admin only)"
)
def update_fee_structure(
    structure_id: int,
    payload: FeeStructureUpdate,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    service = FeeService(db)
    return service.update_fee_structure(structure_id, payload, user_id=current_admin.id)


@router.delete(
    "/structures/{structure_id}",
    summary="Delete a fee structure item (Admin only)"
)
def delete_fee_structure(
    structure_id: int,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    service = FeeService(db)
    return service.delete_fee_structure(structure_id, user_id=current_admin.id)


# =========================================================================
# 3. STUDENT FEE INVOICES & ASSIGNMENT
# =========================================================================

@router.post(
    "/invoices/assign",
    response_model=AssignFeeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Assign a fee structure to a student, selected students, or an entire class"
)
def assign_fee_structure(
    payload: AssignFeePayload,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    service = FeeService(db)
    return service.assign_fee_structure(payload, user_id=current_admin.id)


# Backward-compatible alias for frontend compatibility
@router.post(
    "/student-fees/assign",
    response_model=AssignFeeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Assign fee alias route"
)
@router.post(
    "/assign",
    response_model=AssignFeeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Assign fee root alias"
)
def assign_fee_alias(
    payload: AssignFeePayload,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    service = FeeService(db)
    return service.assign_fee_structure(payload, user_id=current_admin.id)


@router.get(
    "/invoices",
    response_model=PaginatedStudentFeeResponse,
    summary="Search and filter student fee invoices with pagination"
)
def list_student_invoices(
    query: Optional[str] = Query(None, description="Search student name, admission #, or invoice #"),
    class_id: Optional[int] = Query(None),
    education_level: Optional[str] = Query(None, description="PRIMARY or SECONDARY"),
    student_id: Optional[int] = Query(None),
    fee_structure_id: Optional[int] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    academic_year: Optional[str] = Query(None),
    is_overdue_only: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = FeeService(db)
    skip = (page - 1) * page_size
    items, total = service.search_student_invoices(
        query=query,
        class_id=class_id,
        student_id=student_id,
        fee_structure_id=fee_structure_id,
        status_filter=status_filter,
        academic_year=academic_year,
        education_level=education_level,
        is_overdue_only=is_overdue_only,
        skip=skip,
        limit=page_size,
    )
    total_pages = max(1, (total + page_size - 1) // page_size) if total > 0 else 1
    return PaginatedStudentFeeResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


# Backward-compatible alias for frontend
@router.get(
    "/student-fees",
    response_model=PaginatedStudentFeeResponse,
    summary="List student fees alias route"
)
def list_student_fees_alias(
    query: Optional[str] = Query(None),
    class_id: Optional[int] = Query(None),
    education_level: Optional[str] = Query(None, description="PRIMARY or SECONDARY"),
    student_id: Optional[int] = Query(None),
    fee_structure_id: Optional[int] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    academic_year: Optional[str] = Query(None),
    is_overdue_only: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = FeeService(db)
    skip = (page - 1) * page_size
    items, total = service.search_student_invoices(
        query=query,
        class_id=class_id,
        student_id=student_id,
        fee_structure_id=fee_structure_id,
        status_filter=status_filter,
        academic_year=academic_year,
        education_level=education_level,
        is_overdue_only=is_overdue_only,
        skip=skip,
        limit=page_size,
    )
    total_pages = max(1, (total + page_size - 1) // page_size) if total > 0 else 1
    return PaginatedStudentFeeResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get(
    "/invoices/{invoice_id}",
    response_model=StudentFeeResponse,
    summary="Get detailed invoice ledger and payment history"
)
def get_invoice_detail(
    invoice_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = FeeService(db)
    return service.get_student_fee(invoice_id)


# Backward-compatible alias
@router.get(
    "/student-fees/{student_fee_id}",
    response_model=StudentFeeResponse,
    summary="Get student fee detail alias"
)
def get_student_fee_alias(
    student_fee_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = FeeService(db)
    return service.get_student_fee(student_fee_id)


# =========================================================================
# 4. PAYMENTS & OFFICIAL RECEIPTS
# =========================================================================

@router.post(
    "/payments",
    response_model=FeePaymentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record verified student fee payment receipt (Admin only)"
)
def record_payment(
    payload: FeePaymentCreate,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    service = FeeService(db)
    return service.record_payment(payload, recorded_by_user_id=current_admin.id)


@router.get(
    "/payments",
    response_model=List[FeePaymentResponse],
    summary="List verified payment ledger records"
)
def list_payments(
    student_id: Optional[int] = Query(None),
    student_fee_id: Optional[int] = Query(None),
    class_id: Optional[int] = Query(None),
    education_level: Optional[str] = Query(None),
    payment_method: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    academic_year: Optional[str] = Query(None),
    query: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    service = FeeService(db)
    payments, _ = service.list_payments(
        student_id=student_id,
        student_fee_id=student_fee_id,
        payment_method=payment_method,
        status_filter=status_filter,
        academic_year=academic_year,
        education_level=education_level,
        class_id=class_id,
        query=query,
        skip=skip,
        limit=limit,
    )
    return payments


@router.get(
    "/payments/{payment_id}/receipt",
    response_model=OfficialReceiptData,
    summary="Get single-page official printable receipt data"
)
def get_payment_receipt(
    payment_id: int,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    service = FeeService(db)
    return service.get_payment_receipt(payment_id)


@router.post(
    "/payments/{payment_id}/cancel",
    response_model=FeePaymentResponse,
    summary="Cancel / void a payment transaction (Admin only)"
)
def cancel_payment(
    payment_id: int,
    reason: Optional[str] = Query(None),
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    service = FeeService(db)
    return service.cancel_payment(payment_id, user_id=current_admin.id, reason=reason)


# =========================================================================
# 5. GUARDIAN SMS NOTIFICATION INTEGRATION
# =========================================================================

@router.post(
    "/notifications/preview",
    response_model=FeeNotificationPreviewResponse,
    summary="Preview guardian fee reminder SMS messages and recipient eligibility"
)
@router.get(
    "/notifications/preview",
    response_model=FeeNotificationPreviewResponse,
    summary="Preview guardian fee reminder SMS messages GET alias"
)
def preview_fee_notifications(
    target_type: str = Query("OVERDUE_ONLY", description="OVERDUE_ONLY, ALL_OUTSTANDING, CLASS"),
    class_id: Optional[int] = Query(None),
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    service = FeeService(db)
    return service.preview_fee_notifications(
        target_type=target_type,
        class_id=class_id,
    )


@router.post(
    "/notifications/send",
    response_model=FeeNotificationSendResponse,
    summary="Dispatch automated SMS fee reminder alerts via Hormuud Gateway (Admin only)"
)
def send_fee_notifications(
    payload: FeeNotificationSendRequest,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    service = FeeService(db)
    return service.send_fee_notifications(admin_user=current_admin, payload=payload)


# =========================================================================
# 6. STUDENT FINANCIAL PROFILE & CSV EXPORT
# =========================================================================

@router.get(
    "/students/{student_id}/financial-profile",
    response_model=StudentFinancialProfileResponse,
    summary="Get authoritative student financial dossier (Admin only)"
)
@router.get(
    "/student/{student_id}/financial-profile",
    response_model=StudentFinancialProfileResponse,
    summary="Get authoritative student financial dossier alias (Admin only)"
)
@router.get(
    "/students/{student_id}/finance",
    response_model=StudentFinancialProfileResponse,
    summary="Get student finance ledger alias (Admin only)"
)
@router.get(
    "/student/{student_id}",
    response_model=StudentFinancialProfileResponse,
    summary="Get complete student financial profile alias (Admin only)"
)
def get_student_financial_profile(
    student_id: int,
    academic_year: Optional[str] = Query(None, description="Optional academic year filter"),
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    service = FeeService(db)
    return service.get_student_financial_profile(student_id=student_id, academic_year=academic_year)


@router.get(
    "/export",
    summary="Export financial invoices ledger to CSV"
)
def export_fees_csv(
    academic_year: Optional[str] = Query(None),
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    service = FeeService(db)
    csv_data = service.export_invoices_csv(academic_year=academic_year)
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=fees_export_{date.today().isoformat()}.csv"}
    )


# =========================================================================
# 7. CANONICAL FEES CLASS & ENROLLMENT INTEGRATION (SINGLE SOURCE OF TRUTH)
# =========================================================================

@router.get(
    "/classes",
    response_model=List[SchoolClassResponse],
    summary="Get canonical active classes filtered by academic year and education level for Fees"
)
def get_fee_classes(
    academic_year: Optional[str] = Query(None, description="e.g. 2026/2027"),
    education_level: Optional[str] = Query(None, description="PRIMARY or SECONDARY"),
    has_students_only: bool = Query(False, description="Filter only classes with active enrollments"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = FeeService(db)
    return service.get_fee_classes(academic_year=academic_year, division=education_level, has_students_only=has_students_only)


@router.get(
    "/classes/{class_id}/students",
    response_model=ClassStudentsFinancialResponse,
    summary="Get authoritative active enrolled students for class and academic year with live financial balances"
)
def get_class_students_financial(
    class_id: int,
    academic_year: str = Query(..., description="Required academic year, e.g. 2026/2027"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = FeeService(db)
    try:
        return service.get_class_students_financial(class_id=class_id, academic_year=academic_year)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/outstanding",
    response_model=OutstandingStudentsResponse,
    summary="Get authoritative list of outstanding/unpaid students with exact PostgreSQL Decimal balances"
)
def get_outstanding_students(
    academic_year: str = Query(..., description="Required academic year, e.g. 2026/2027"),
    education_level: Optional[str] = Query(None, description="PRIMARY or SECONDARY"),
    class_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None, description="UNPAID, PARTIAL, OVERDUE, PAID, ALL_OUTSTANDING"),
    query: Optional[str] = Query(None, description="Student name or admission number"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = FeeService(db)
    return service.get_outstanding_students(
        academic_year=academic_year,
        division=education_level,
        class_id=class_id,
        status_filter=status,
        query=query,
    )


@router.get(
    "/eligible-students",
    response_model=FeeEligibleStudentsResponse,
    summary="Get authoritative fee-eligible students derived from PostgreSQL active enrollments"
)
@router.get(
    "/students/eligible",
    response_model=FeeEligibleStudentsResponse,
    summary="Get authoritative fee-eligible students alias"
)
@router.get(
    "/students",
    response_model=FeeEligibleStudentsResponse,
    summary="Get authoritative fee-eligible students alias"
)
def get_fee_eligible_students(
    academic_year: Optional[str] = Query(None, description="e.g. 2026/2027"),
    education_level: Optional[str] = Query(None, description="PRIMARY or SECONDARY"),
    class_id: Optional[int] = Query(None),
    query: Optional[str] = Query(None, description="Student name or admission number"),
    status: Optional[str] = Query(None, description="ALL, INVOICED, UNINVOICED, PAID, UNPAID, PARTIAL, OVERDUE"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = FeeService(db)
    return service.get_eligible_students(
        academic_year=academic_year,
        education_level=education_level,
        class_id=class_id,
        query=query,
        status_filter=status,
        skip=skip,
        limit=limit,
    )

