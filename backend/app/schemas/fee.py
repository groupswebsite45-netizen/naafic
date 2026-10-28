from datetime import date, datetime
from typing import List, Optional, Any, Dict
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.school_class import SchoolClassResponse


# =========================================================================
# 1. FEE STRUCTURE SCHEMAS
# =========================================================================

class FeeStructureBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="e.g. Monthly Tuition Fee")
    academic_year: str = Field(..., min_length=4, max_length=50, description="e.g. 2026/2027")
    class_id: Optional[int] = Field(None, description="Optional class filter; null for all classes")
    education_level: Optional[str] = Field(None, description="PRIMARY, SECONDARY, or ALL")
    amount: Decimal = Field(..., gt=0, description="Standard fee amount in USD")
    frequency: str = Field(default="Monthly", description="Monthly, Term, Semester, Annual, One-Time")
    due_date: date = Field(..., description="Default payment due date")
    description: Optional[str] = None
    status: str = Field(default="ACTIVE", description="ACTIVE, INACTIVE, ARCHIVED")


class FeeStructureCreate(FeeStructureBase):
    class_ids: Optional[List[int]] = Field(None, description="Multiple class IDs to apply fee structure to")
    apply_to_all_in_level: Optional[bool] = Field(False, description="Apply to all classes in selected level")


class FeeStructureUpdate(BaseModel):
    name: Optional[str] = None
    academic_year: Optional[str] = None
    class_id: Optional[int] = None
    education_level: Optional[str] = None
    amount: Optional[Decimal] = Field(None, gt=0)
    frequency: Optional[str] = None
    due_date: Optional[date] = None
    description: Optional[str] = None
    status: Optional[str] = None


class FeeStructureResponse(FeeStructureBase):
    id: int
    school_class: Optional[SchoolClassResponse] = None
    class_name: Optional[str] = None
    created_by_id: Optional[int] = None
    created_by_name: Optional[str] = None
    assigned_students_count: Optional[int] = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =========================================================================
# 2. PAYMENT SCHEMAS & RECEIPTS
# =========================================================================

class FeePaymentCreate(BaseModel):
    student_fee_id: int = Field(..., description="Target invoice ID")
    amount_paid: Decimal = Field(..., gt=0, description="Payment amount")
    payment_date: date = Field(default_factory=date.today)
    payment_method: str = Field(
        ...,
        description="CASH, EVC_PLUS, EDAHAB, ZAAD, SAHAL, BANK_TRANSFER, CHEQUE, OTHER"
    )
    reference_number: Optional[str] = Field(None, description="Transaction ID or mobile money code")
    notes: Optional[str] = None


class FeePaymentResponse(BaseModel):
    id: int
    payment_id: Optional[int] = None  # Canonical alias
    student_fee_id: int
    student_id: int
    student_name: Optional[str] = None
    student_admission_number: Optional[str] = None
    invoice_number: Optional[str] = None
    receipt_number: str
    amount_paid: Decimal
    amount: Optional[Decimal] = None  # Canonical alias
    payment_date: date
    payment_method: str
    reference_number: Optional[str] = None
    reference: Optional[str] = None  # Canonical alias
    recorded_by_id: Optional[int] = None
    recorded_by_name: Optional[str] = None
    notes: Optional[str] = None
    status: str = "VERIFIED"
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OfficialReceiptData(BaseModel):
    receipt_number: str
    invoice_number: str
    payment_date: str
    student_name: str
    student_admission_number: str
    class_name: str
    academic_year: str
    fee_name: str
    amount_paid: float
    payment_method: str
    reference_number: Optional[str] = None
    recorded_by_name: str
    invoice_total_amount: float
    total_amount_paid_to_date: float
    remaining_balance: float
    payment_status: str
    notes: Optional[str] = None
    school_name: str = "Education Management System"
    school_address: str = "Hawlwadaag District, Mogadishu, Somalia"
    school_contact: str = "+252 61 5000000 | finance@hawlwadaagschool.edu.so"
    verified_stamp: str = "OFFICIAL FINANCE RECEIPT - VERIFIED"


# =========================================================================
# 3. STUDENT FEE INVOICES SCHEMAS
# =========================================================================

class StudentFeeResponse(BaseModel):
    id: int
    invoice_number: str
    student_id: int
    student_name: str = ""
    student_admission_number: str = ""
    class_id: Optional[int] = None
    class_name: str = ""
    fee_structure_id: Optional[int] = None
    fee_name: str = ""
    academic_year: str
    fee_type: Optional[str] = None
    amount_due: Decimal
    discount_amount: Decimal
    net_amount: float
    amount: Optional[float] = None  # Canonical alias
    total_paid: float
    paid: Optional[float] = None  # Canonical alias
    balance_remaining: float
    balance: Optional[float] = None  # Canonical alias
    due_date: date
    status: str  # PENDING, PARTIALLY_PAID, PAID, OVERDUE, CANCELLED
    is_overdue: bool = False
    fee_structure: Optional[FeeStructureResponse] = None
    payments: List[FeePaymentResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedStudentFeeResponse(BaseModel):
    items: List[StudentFeeResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# =========================================================================
# 4. ASSIGN FEE PAYLOADS
# =========================================================================

class AssignFeePayload(BaseModel):
    target_type: str = Field(default="SINGLE_STUDENT", description="SINGLE_STUDENT, SELECTED_STUDENTS, CLASS")
    student_id: Optional[int] = None
    student_ids: Optional[List[int]] = None
    class_id: Optional[int] = None
    fee_structure_id: int
    academic_year: Optional[str] = None
    amount_due: Optional[Decimal] = None
    due_date: Optional[date] = None


class AssignFeeResponse(BaseModel):
    success: bool
    created_count: int
    skipped_count: int
    total_amount_billed: float
    message: str
    academic_year: str
    created_invoices: List[StudentFeeResponse] = []


# =========================================================================
# 5. DASHBOARD & FINANCIAL TELEMETRY
# =========================================================================

class FeeFinancialSummaryResponse(BaseModel):
    # Core Reconciliation Totals
    total_students: int = 0
    fee_per_student: float = 0.0
    expected_total: float = 0.0
    total_billed: float = 0.0
    total_collected: float = 0.0
    total_paid: float = 0.0
    total_outstanding: float = 0.0
    total_overdue: float = 0.0
    collected_this_month: float = 0.0
    this_month_collected: float = 0.0  # Backward-compatible alias for frontend
    
    # Student Level Counts
    paid_students_count: int = 0
    unpaid_students_count: int = 0
    total_eligible_students: int = 0
    primary_eligible_students: int = 0
    secondary_eligible_students: int = 0
    invoiced_students_count: int = 0
    unbilled_students_count: int = 0
    students_without_class_count: int = 0
    
    # Invoice Counts
    total_invoices_count: int = 0
    paid_invoices_count: int = 0
    pending_invoices_count: int = 0
    partial_invoices_count: int = 0
    overdue_invoices_count: int = 0
    unpaid_invoices_count: int = 0  # Canonical alias for pending/unpaid count

    # Reconciliation Status
    is_reconciled: bool = True
    reconciliation_difference: float = 0.0
    reconciliation_message: str = "Financial records fully reconciled."


class FeeClassStudentItem(BaseModel):
    student_id: int
    student_name: str
    admission_number: str
    class_id: int
    class_name: str
    academic_year: str
    fee_amount: float
    paid_amount: float
    balance: float
    status: str  # PAID, PARTIAL, UNPAID, OVERDUE


class ClassStudentsFinancialResponse(BaseModel):
    class_id: int
    class_name: str
    academic_year: str
    total_students: int
    total_billed: float
    total_collected: float
    total_outstanding: float
    total_overdue: float
    students: List[FeeClassStudentItem]


class OutstandingStudentItem(BaseModel):
    student_id: int
    student_name: str
    admission_number: str
    class_id: int
    class_name: str
    education_level: str
    academic_year: str
    fee_type: Optional[str] = None
    invoice_number: Optional[str] = None
    amount_due: float
    paid_amount: float
    balance: float
    due_date: Optional[date] = None
    status: str  # UNPAID, PARTIAL, OVERDUE, PAID


class OutstandingStudentsResponse(BaseModel):
    academic_year: str
    education_level: Optional[str] = None
    class_id: Optional[int] = None
    total_students: int
    paid_count: int
    partial_count: int
    unpaid_count: int
    overdue_count: int
    total_outstanding_balance: float
    items: List[OutstandingStudentItem]


class ClassFinancialSummaryItem(BaseModel):
    class_id: int
    class_name: str
    class_code: str
    total_students: int
    total_billed: float
    total_collected: float
    total_outstanding: float
    collection_rate_pct: float
    unpaid_count: int
    partial_count: int
    paid_count: int


class ClassFinancialSummaryResponse(BaseModel):
    classes: List[ClassFinancialSummaryItem]
    grand_total_billed: float
    grand_total_collected: float
    grand_total_outstanding: float


class PaymentMethodSummaryItem(BaseModel):
    method: str
    count: int
    total_amount: float
    percentage: float


class PaymentMethodSummaryResponse(BaseModel):
    methods: List[PaymentMethodSummaryItem]
    grand_total: float


class MonthlyCollectionTrendItem(BaseModel):
    month_label: str  # e.g. "Sep 2026"
    month_year: str   # e.g. "2026-09"
    amount: float
    transaction_count: int


class MonthlyCollectionTrendResponse(BaseModel):
    trends: List[MonthlyCollectionTrendItem]
    total_collected: float


# =========================================================================
# 6. GUARDIAN SMS NOTIFICATION INTEGRATION
# =========================================================================

class FeeNotificationPreviewItem(BaseModel):
    student_id: int
    student_name: str
    admission_number: str
    class_name: str
    guardian_name: str
    guardian_phone: Optional[str] = None
    has_valid_phone: bool
    total_outstanding: float
    overdue_count: int
    sample_message: str


class FeeNotificationPreviewResponse(BaseModel):
    total_students: int
    eligible_count: int
    missing_phone_count: int
    total_outstanding_amount: float
    sample_previews: List[FeeNotificationPreviewItem]


class FeeNotificationSendRequest(BaseModel):
    target_type: str = Field(default="OVERDUE_ONLY", description="OVERDUE_ONLY, ALL_OUTSTANDING, CLASS, SELECTED_STUDENTS")
    class_id: Optional[int] = None
    student_ids: Optional[List[int]] = None
    template_code: str = Field(default="FEE_REMINDER", description="FEE_REMINDER, FEE_OVERDUE, PAYMENT_CONFIRMATION")
    custom_message_template: Optional[str] = None


class FeeNotificationSendResponse(BaseModel):
    success: bool
    sent_or_queued_count: int
    missing_contact_count: int
    already_notified_count: int
    total_recipients: int
    message: str


# =========================================================================
# 7. STUDENT FINANCIAL PROFILE
# =========================================================================

class StudentFinancialProfileSummary(BaseModel):
    total_billed: float = 0.0
    total_paid: float = 0.0
    outstanding_balance: float = 0.0
    overdue_balance: float = 0.0
    currency: str = "$"


class StudentFinancialProfileResponse(BaseModel):
    student_id: int
    admission_number: str
    full_name: str
    student_name: Optional[str] = None  # Frontend convenience alias
    status: str = "ACTIVE"
    class_id: Optional[int] = None
    class_name: str
    current_class: Optional[str] = None  # Frontend convenience alias
    education_level: Optional[str] = None
    academic_year: str
    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None
    total_billed: float = 0.0
    total_paid: float = 0.0
    outstanding_balance: float = 0.0
    overdue_balance: float = 0.0
    financial_summary: Optional[StudentFinancialProfileSummary] = None
    invoices: List[StudentFeeResponse] = []
    payments: List[FeePaymentResponse] = []


# =========================================================================
# 8. AUTHORITATIVE FEE-ELIGIBLE STUDENTS
# =========================================================================

class FeeEligibleStudentItem(BaseModel):
    student_id: int
    admission_number: str
    first_name: str
    last_name: str
    full_name: str
    gender: str
    class_id: Optional[int] = None
    class_name: Optional[str] = None
    education_level: Optional[str] = None
    academic_year: str
    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None
    status: str = "ACTIVE"
    invoices_count: int = 0
    total_billed: float = 0.0
    total_paid: float = 0.0
    outstanding_balance: float = 0.0
    overdue_balance: float = 0.0
    financial_status: str = "UNBILLED"  # UNBILLED, PAID, PARTIAL, UNPAID, OVERDUE


class FeeEligibleStudentsResponse(BaseModel):
    total_eligible: int
    primary_count: int
    secondary_count: int
    without_class_count: int
    invoiced_count: int
    uninvoiced_count: int
    academic_year: Optional[str] = None
    education_level: Optional[str] = None
    class_id: Optional[int] = None
    items: List[FeeEligibleStudentItem]
