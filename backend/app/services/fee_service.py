import io
import csv
from typing import Optional, List, Tuple, Dict, Any
from datetime import date, datetime, timezone
from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.fee import FeeStructure, StudentFee, FeePayment
from app.models.student import Student
from app.models.school_class import SchoolClass
from app.models.user import User
from app.models.notification import Notification, NotificationDelivery
from app.repositories.fee_repo import FeeRepository
from app.repositories.student_repo import StudentRepository
from app.repositories.audit_repo import AuditLogRepository
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
    FeeFinancialSummaryResponse,
    ClassFinancialSummaryResponse,
    PaymentMethodSummaryResponse,
    MonthlyCollectionTrendResponse,
    FeeNotificationPreviewResponse,
    FeeNotificationPreviewItem,
    FeeNotificationSendRequest,
    FeeNotificationSendResponse,
    StudentFinancialProfileSummary,
    StudentFinancialProfileResponse,
    ClassStudentsFinancialResponse,
    OutstandingStudentsResponse,
    FeeEligibleStudentItem,
    FeeEligibleStudentsResponse,
)
from app.schemas.school_class import SchoolClassResponse
from app.services.notification_service import NotificationService
from app.utils.logger import logger


class FeeService:
    """Enterprise domain service for School Fees, Invoicing, Verified Payment Receipts, and Financial Telemetry."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = FeeRepository(db)
        self.student_repo = StudentRepository(db)
        self.audit_repo = AuditLogRepository(db)

    # =========================================================================
    # 1. FEE STRUCTURE MANAGEMENT
    # =========================================================================

    def create_fee_structure(self, data: FeeStructureCreate, user_id: Optional[int] = None) -> FeeStructureResponse:
        if data.amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Fee amount must be greater than zero."
            )

        # Multi-class support
        target_class_ids = []
        if data.class_ids and len(data.class_ids) > 1:
            target_class_ids = data.class_ids
        elif data.class_ids and len(data.class_ids) == 1:
            target_class_ids = [data.class_ids[0]]
        elif not data.apply_to_all_in_level and data.class_id:
            target_class_ids = [data.class_id]
        else:
            # Null applies to all classes in the level/school as a single unified structure
            target_class_ids = [None]

        # Duplicate active structure check
        for c_id in target_class_ids:
            ed_lvl = data.education_level
            if c_id:
                cls_row = self.db.query(SchoolClass).filter(SchoolClass.id == c_id).first()
                if cls_row and cls_row.division:
                    ed_lvl = cls_row.division

            existing = self.repo.check_duplicate_active_structure(
                name=data.name,
                academic_year=data.academic_year,
                class_id=c_id,
                education_level=ed_lvl,
            )
            if existing:
                scope_str = f"class {existing.school_class.name}" if existing.school_class else (f"level {ed_lvl}" if ed_lvl else "all classes")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"An active fee structure named '{data.name}' already exists for {data.academic_year} in {scope_str}."
                )

        primary_structure = None
        for c_id in target_class_ids:
            ed_lvl = data.education_level.upper().strip() if data.education_level else None
            if c_id:
                cls_row = self.db.query(SchoolClass).filter(SchoolClass.id == c_id).first()
                if cls_row and cls_row.division:
                    ed_lvl = cls_row.division

            st = FeeStructure(
                name=data.name.strip(),
                academic_year=data.academic_year.strip(),
                class_id=c_id,
                education_level=ed_lvl,
                created_by_id=user_id,
                amount=data.amount,
                frequency=data.frequency.strip() if data.frequency else "Monthly",
                due_date=data.due_date,
                description=data.description.strip() if data.description else None,
                status=data.status.upper().strip() if data.status else "ACTIVE",
            )
            created = self.repo.create_structure(st)
            if not primary_structure:
                primary_structure = created

        self.audit_repo.log_event(
            action="FEE_STRUCTURE_CREATED",
            user_id=user_id,
            details={
                "structure_id": primary_structure.id,
                "name": primary_structure.name,
                "amount": float(primary_structure.amount),
                "frequency": primary_structure.frequency,
                "academic_year": primary_structure.academic_year,
                "education_level": primary_structure.education_level,
            }
        )

        res = FeeStructureResponse.model_validate(primary_structure)
        res.class_name = primary_structure.school_class.name if primary_structure.school_class else "All Classes"
        res.created_by_name = primary_structure.created_by.full_name if primary_structure.created_by else "Administrator"
        res.assigned_students_count = 0
        return res

    def update_fee_structure(self, structure_id: int, data: FeeStructureUpdate, user_id: Optional[int] = None) -> FeeStructureResponse:
        update_dict = data.model_dump(exclude_unset=True)
        if "amount" in update_dict and update_dict["amount"] is not None and update_dict["amount"] <= 0:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Fee amount must be greater than zero.")

        # Check duplicate if name, academic_year, class_id, or education_level is being changed
        structure = self.repo.get_structure_by_id(structure_id)
        if not structure:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Fee structure ID {structure_id} not found.")

        chk_name = update_dict.get("name", structure.name)
        chk_ay = update_dict.get("academic_year", structure.academic_year)
        chk_cid = update_dict.get("class_id", structure.class_id)
        chk_lvl = update_dict.get("education_level", structure.education_level)
        chk_status = update_dict.get("status", structure.status)

        if chk_status == "ACTIVE":
            dup = self.repo.check_duplicate_active_structure(
                name=chk_name,
                academic_year=chk_ay,
                class_id=chk_cid,
                education_level=chk_lvl,
                exclude_id=structure_id,
            )
            if dup:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Another active fee structure named '{chk_name}' already exists for {chk_ay} in this scope."
                )

        updated = self.repo.update_structure(structure_id, update_dict)

        self.audit_repo.log_event(
            action="FEE_STRUCTURE_UPDATED",
            user_id=user_id,
            details={"structure_id": structure_id, "updated_fields": list(update_dict.keys())}
        )

        res = FeeStructureResponse.model_validate(updated)
        res.class_name = updated.school_class.name if updated.school_class else "All Classes"
        res.created_by_name = updated.created_by.full_name if updated.created_by else "Administrator"
        res.assigned_students_count = self.repo.count_assigned_students(updated.id)
        return res

    def list_fee_structures(
        self,
        academic_year: Optional[str] = None,
        class_id: Optional[int] = None,
        status_filter: Optional[str] = None,
        education_level: Optional[str] = None,
    ) -> List[FeeStructureResponse]:
        structures = self.repo.get_all_structures(
            academic_year=academic_year,
            class_id=class_id,
            status=status_filter,
            education_level=education_level,
        )
        output = []
        for st in structures:
            item = FeeStructureResponse.model_validate(st)
            item.class_name = st.school_class.name if st.school_class else "All Classes"
            item.created_by_name = st.created_by.full_name if st.created_by else "Administrator"
            item.assigned_students_count = self.repo.count_assigned_students(st.id)
            output.append(item)
        return output

    def delete_fee_structure(self, structure_id: int, user_id: Optional[int] = None) -> dict:
        structure = self.repo.get_structure_by_id(structure_id)
        if not structure:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Fee structure ID {structure_id} not found."
            )

        name = structure.name
        self.repo.delete_structure(structure_id)

        self.audit_repo.log_event(
            action="FEE_STRUCTURE_DELETED",
            user_id=user_id,
            details={"structure_id": structure_id, "name": name}
        )

        return {"success": True, "message": f"Fee structure '{name}' deleted successfully."}

    # =========================================================================
    # 2. INVOICE GENERATION & FEE ASSIGNMENT
    # =========================================================================

    def assign_fee_structure(self, data: AssignFeePayload, user_id: Optional[int] = None) -> AssignFeeResponse:
        """Assign fee structure to single student, selected students, or a whole class with transaction safety."""
        structure = self.repo.get_structure_by_id(data.fee_structure_id)
        if not structure:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Fee structure ID {data.fee_structure_id} not found.")

        try:
            created_invoices, created_cnt, skipped_cnt = self.repo.assign_fee_structure_atomic(
                target_type=data.target_type,
                fee_structure_id=data.fee_structure_id,
                student_id=data.student_id,
                student_ids=data.student_ids,
                class_id=data.class_id,
                academic_year=data.academic_year,
                custom_amount=data.amount_due,
                custom_due_date=data.due_date,
            )
        except ValueError as ve:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve))

        total_billed = sum(float(inv.net_amount) for inv in created_invoices)

        self.audit_repo.log_event(
            action="FEE_INVOICES_ASSIGNED",
            user_id=user_id,
            details={
                "fee_structure_id": structure.id,
                "target_type": data.target_type,
                "created_count": created_cnt,
                "skipped_count": skipped_cnt,
                "total_billed": total_billed,
            }
        )

        invoices_res = [self._format_student_fee_response(inv) for inv in created_invoices]

        return AssignFeeResponse(
            success=True,
            created_count=created_cnt,
            skipped_count=skipped_cnt,
            total_amount_billed=round(total_billed, 2),
            academic_year=data.academic_year or structure.academic_year,
            message=f"Successfully generated {created_cnt} invoice(s) totaling ${total_billed:,.2f} ({skipped_cnt} already assigned).",
            created_invoices=invoices_res,
        )

    def _format_student_fee_response(self, sf: StudentFee) -> StudentFeeResponse:
        today = date.today()
        is_ovd = bool(sf.due_date < today and sf.balance_remaining > 0 and sf.status != "CANCELLED")

        payments_res = []
        for p in sf.payments:
            payments_res.append(
                FeePaymentResponse(
                    id=p.id,
                    student_fee_id=p.student_fee_id,
                    student_id=p.student_id,
                    student_name=sf.student_name,
                    student_admission_number=sf.student_admission_number,
                    invoice_number=sf.invoice_number,
                    receipt_number=p.receipt_number,
                    amount_paid=p.amount_paid,
                    payment_date=p.payment_date,
                    payment_method=p.payment_method,
                    reference_number=p.reference_number,
                    recorded_by_id=p.recorded_by_id,
                    recorded_by_name=p.recorded_by_name,
                    notes=p.notes,
                    status=p.status,
                    created_at=p.created_at,
                )
            )

        fee_struct_res = None
        if sf.fee_structure:
            fee_struct_res = FeeStructureResponse.model_validate(sf.fee_structure)
            fee_struct_res.class_name = sf.fee_structure.school_class.name if sf.fee_structure.school_class else "All Classes"

        # Resolve authoritative class from student's current enrollment
        res_class_id = sf.class_id
        res_class_name = sf.class_name
        if sf.student and sf.student.current_class:
            res_class_id = sf.student.current_class.id
            res_class_name = sf.student.current_class.name

        return StudentFeeResponse(
            id=sf.id,
            invoice_number=sf.invoice_number,
            student_id=sf.student_id,
            student_name=sf.student_name,
            student_admission_number=sf.student_admission_number,
            class_id=res_class_id,
            class_name=res_class_name,
            fee_structure_id=sf.fee_structure_id,
            fee_name=sf.fee_structure.name if sf.fee_structure else (sf.fee_type or "Fee Invoice"),
            academic_year=sf.academic_year,
            fee_type=sf.fee_type or (sf.fee_structure.name if sf.fee_structure else "Tuition"),
            amount_due=sf.amount_due,
            discount_amount=sf.discount_amount,
            net_amount=sf.net_amount,
            total_paid=sf.total_paid,
            balance_remaining=sf.balance_remaining,
            due_date=sf.due_date,
            status=sf.status,
            is_overdue=is_ovd,
            fee_structure=fee_struct_res,
            payments=payments_res,
            created_at=sf.created_at,
            updated_at=sf.updated_at,
        )

    def search_student_invoices(
        self,
        query: Optional[str] = None,
        class_id: Optional[int] = None,
        student_id: Optional[int] = None,
        fee_structure_id: Optional[int] = None,
        status_filter: Optional[str] = None,
        academic_year: Optional[str] = None,
        education_level: Optional[str] = None,
        is_overdue_only: bool = False,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[StudentFeeResponse], int]:
        invoices, total = self.repo.search_student_fees(
            query=query,
            class_id=class_id,
            student_id=student_id,
            fee_structure_id=fee_structure_id,
            status=status_filter,
            academic_year=academic_year,
            education_level=education_level,
            is_overdue_only=is_overdue_only,
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=limit,
        )
        formatted = [self._format_student_fee_response(inv) for inv in invoices]
        return formatted, total

    def get_student_fee(self, student_fee_id: int) -> StudentFeeResponse:
        sf = self.repo.get_student_fee_by_id(student_fee_id)
        if not sf:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Student fee invoice ID {student_fee_id} not found.")
        return self._format_student_fee_response(sf)

    # =========================================================================
    # 3. PAYMENT RECORDING & RECEIPTS
    # =========================================================================

    def record_payment(self, data: FeePaymentCreate, recorded_by_user_id: Optional[int] = None) -> FeePaymentResponse:
        """Atomically record verified payment with row lock and receipt numbering."""
        if data.amount_paid <= 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Payment amount must be strictly greater than zero."
            )

        try:
            payment = self.repo.record_payment_atomic(
                student_fee_id=data.student_fee_id,
                amount_paid=data.amount_paid,
                payment_date=data.payment_date or date.today(),
                payment_method=data.payment_method,
                recorded_by_id=recorded_by_user_id,
                reference_number=data.reference_number,
                notes=data.notes,
            )
        except ValueError as ve:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve))

        self.audit_repo.log_event(
            action="FEE_PAYMENT_RECORDED",
            user_id=recorded_by_user_id,
            details={
                "payment_id": payment.id,
                "receipt_number": payment.receipt_number,
                "student_id": payment.student_id,
                "student_fee_id": payment.student_fee_id,
                "amount": float(payment.amount_paid),
                "method": payment.payment_method,
                "reference": payment.reference_number,
            }
        )

        return FeePaymentResponse(
            id=payment.id,
            student_fee_id=payment.student_fee_id,
            student_id=payment.student_id,
            student_name=payment.student_name,
            student_admission_number=payment.student_admission_number,
            invoice_number=payment.invoice_number,
            receipt_number=payment.receipt_number,
            amount_paid=payment.amount_paid,
            payment_date=payment.payment_date,
            payment_method=payment.payment_method,
            reference_number=payment.reference_number,
            recorded_by_id=payment.recorded_by_id,
            recorded_by_name=payment.recorded_by_name,
            notes=payment.notes,
            status=payment.status,
            created_at=payment.created_at,
        )

    def cancel_payment(self, payment_id: int, user_id: Optional[int] = None, reason: Optional[str] = None) -> FeePaymentResponse:
        try:
            payment = self.repo.cancel_payment_atomic(payment_id=payment_id, user_id=user_id, reason=reason)
        except ValueError as ve:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))

        self.audit_repo.log_event(
            action="FEE_PAYMENT_CANCELLED",
            user_id=user_id,
            details={"payment_id": payment.id, "receipt_number": payment.receipt_number, "reason": reason}
        )

        return FeePaymentResponse(
            id=payment.id,
            student_fee_id=payment.student_fee_id,
            student_id=payment.student_id,
            student_name=payment.student_name,
            student_admission_number=payment.student_admission_number,
            invoice_number=payment.invoice_number,
            receipt_number=payment.receipt_number,
            amount_paid=payment.amount_paid,
            payment_date=payment.payment_date,
            payment_method=payment.payment_method,
            reference_number=payment.reference_number,
            recorded_by_id=payment.recorded_by_id,
            recorded_by_name=payment.recorded_by_name,
            notes=payment.notes,
            status=payment.status,
            created_at=payment.created_at,
        )

    def get_payment_receipt(self, payment_id: int) -> OfficialReceiptData:
        """Construct authoritative, single-page official receipt payload."""
        payment = self.repo.get_payment_by_id(payment_id)
        if not payment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Payment ID {payment_id} not found.")

        student_fee = payment.student_fee
        student = payment.student
        class_name = student_fee.class_name if student_fee else (student.current_class.name if student and student.current_class else "Standard")

        fee_name = student_fee.fee_structure.name if student_fee and student_fee.fee_structure else (student_fee.fee_type or "School Fee")

        return OfficialReceiptData(
            receipt_number=payment.receipt_number,
            invoice_number=payment.invoice_number,
            payment_date=payment.payment_date.strftime("%d %B %Y"),
            student_name=payment.student_name,
            student_admission_number=payment.student_admission_number,
            class_name=class_name,
            academic_year=student_fee.academic_year if student_fee else "2026/2027",
            fee_name=fee_name,
            amount_paid=float(payment.amount_paid),
            payment_method=payment.payment_method,
            reference_number=payment.reference_number,
            recorded_by_name=payment.recorded_by_name,
            invoice_total_amount=float(student_fee.net_amount) if student_fee else float(payment.amount_paid),
            total_amount_paid_to_date=float(student_fee.total_paid) if student_fee else float(payment.amount_paid),
            remaining_balance=float(student_fee.balance_remaining) if student_fee else 0.0,
            payment_status=payment.status,
            notes=payment.notes,
            school_name="Hawlwadaag Primary and Secondary School",
            school_address="Hawlwadaag District, Mogadishu, Somalia",
            school_contact="+252 61 5000000 | finance@hawlwadaagschool.edu.so",
            verified_stamp="OFFICIAL FINANCE RECEIPT - VERIFIED",
        )

    def list_payments(
        self,
        student_id: Optional[int] = None,
        student_fee_id: Optional[int] = None,
        payment_method: Optional[str] = None,
        status_filter: Optional[str] = None,
        academic_year: Optional[str] = None,
        education_level: Optional[str] = None,
        class_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        query: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[FeePaymentResponse], int]:
        payments, total = self.repo.list_payments(
            student_id=student_id,
            student_fee_id=student_fee_id,
            payment_method=payment_method,
            status=status_filter,
            academic_year=academic_year,
            education_level=education_level,
            class_id=class_id,
            start_date=start_date,
            end_date=end_date,
            query=query,
            skip=skip,
            limit=limit,
        )
        formatted = [
            FeePaymentResponse(
                id=p.id,
                payment_id=p.id,
                student_fee_id=p.student_fee_id,
                student_id=p.student_id,
                student_name=p.student_name,
                student_admission_number=p.student_admission_number,
                invoice_number=p.invoice_number,
                receipt_number=p.receipt_number,
                amount_paid=p.amount_paid,
                amount=float(p.amount_paid),
                payment_date=p.payment_date,
                payment_method=p.payment_method,
                reference_number=p.reference_number,
                reference=p.reference_number,
                recorded_by_id=p.recorded_by_id,
                recorded_by_name=p.recorded_by_name,
                notes=p.notes,
                status=p.status,
                created_at=p.created_at,
            )
            for p in payments
        ]
        return formatted, total

    # =========================================================================
    # 4. DASHBOARD & FINANCIAL TELEMETRY
    # =========================================================================

    def get_financial_summary(
        self,
        academic_year: Optional[str] = None,
        education_level: Optional[str] = None,
        class_id: Optional[int] = None,
    ) -> FeeFinancialSummaryResponse:
        data = self.repo.get_financial_summary(
            academic_year=academic_year,
            education_level=education_level,
            class_id=class_id,
        )
        return FeeFinancialSummaryResponse(**data)

    def get_class_financial_summary(
        self,
        academic_year: Optional[str] = None,
        education_level: Optional[str] = None,
    ) -> ClassFinancialSummaryResponse:
        items = self.repo.get_class_financial_summary(
            academic_year=academic_year,
            education_level=education_level,
        )
        grand_billed = sum(i["total_billed"] for i in items)
        grand_collected = sum(i["total_collected"] for i in items)
        grand_outstanding = max(0.0, grand_billed - grand_collected)
        return ClassFinancialSummaryResponse(
            classes=items,
            grand_total_billed=round(grand_billed, 2),
            grand_total_collected=round(grand_collected, 2),
            grand_total_outstanding=round(grand_outstanding, 2),
        )

    def get_payment_method_summary(
        self,
        academic_year: Optional[str] = None,
        education_level: Optional[str] = None,
    ) -> PaymentMethodSummaryResponse:
        methods = self.repo.get_payment_method_summary(
            academic_year=academic_year,
            education_level=education_level,
        )
        grand_total = sum(m["total_amount"] for m in methods)
        return PaymentMethodSummaryResponse(
            methods=methods,
            grand_total=round(grand_total, 2),
        )

    def get_monthly_collection_trends(
        self,
        academic_year: Optional[str] = None,
        education_level: Optional[str] = None,
    ) -> MonthlyCollectionTrendResponse:
        trends = self.repo.get_monthly_collection_trends(
            academic_year=academic_year,
            education_level=education_level,
        )
        total_collected = sum(t["amount"] for t in trends)
        return MonthlyCollectionTrendResponse(
            trends=trends,
            total_collected=round(total_collected, 2),
        )

    def get_student_financial_profile(
        self,
        student_id: int,
        academic_year: Optional[str] = None,
    ) -> StudentFinancialProfileResponse:
        profile = self.repo.get_student_financial_profile(student_id=student_id, academic_year=academic_year)
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Student ID {student_id} not found.")

        formatted_invoices = [self._format_student_fee_response(inv) for inv in profile["invoices"]]
        formatted_payments = [
            FeePaymentResponse(
                id=p.id,
                payment_id=p.id,
                student_fee_id=p.student_fee_id,
                student_id=p.student_id,
                student_name=p.student_name,
                student_admission_number=p.student_admission_number,
                invoice_number=p.invoice_number,
                receipt_number=p.receipt_number,
                amount_paid=p.amount_paid,
                amount=float(p.amount_paid),
                payment_date=p.payment_date,
                payment_method=p.payment_method,
                reference_number=p.reference_number,
                reference=p.reference_number,
                recorded_by_id=p.recorded_by_id,
                recorded_by_name=p.recorded_by_name,
                notes=p.notes,
                status=p.status,
                created_at=p.created_at,
            )
            for p in profile["payments"]
        ]

        fin_sum = None
        if profile.get("financial_summary"):
            fin_sum = StudentFinancialProfileSummary(**profile["financial_summary"])

        return StudentFinancialProfileResponse(
            student_id=profile["student_id"],
            admission_number=profile["admission_number"],
            full_name=profile["full_name"],
            student_name=profile.get("student_name") or profile["full_name"],
            status=profile.get("status", "ACTIVE"),
            class_id=profile.get("class_id"),
            class_name=profile["class_name"],
            current_class=profile.get("current_class") or profile["class_name"],
            education_level=profile.get("education_level", "PRIMARY"),
            academic_year=profile["academic_year"],
            guardian_name=profile.get("guardian_name"),
            guardian_phone=profile.get("guardian_phone"),
            total_billed=profile["total_billed"],
            total_paid=profile["total_paid"],
            outstanding_balance=profile["outstanding_balance"],
            overdue_balance=profile["overdue_balance"],
            financial_summary=fin_sum,
            invoices=formatted_invoices,
            payments=formatted_payments,
        )

    # =========================================================================
    # 5. GUARDIAN SMS NOTIFICATION INTEGRATION (HORMUUD)
    # =========================================================================

    def preview_fee_notifications(
        self,
        target_type: str = "OVERDUE_ONLY",
        class_id: Optional[int] = None,
        student_ids: Optional[List[int]] = None,
    ) -> FeeNotificationPreviewResponse:
        """Calculate eligible guardians, missing contacts, total outstanding amount, and sample Somali message."""
        today = date.today()
        q = self.db.query(StudentFee).join(Student, StudentFee.student_id == Student.id).filter(StudentFee.status != "CANCELLED")

        if target_type == "OVERDUE_ONLY":
            q = q.filter(StudentFee.due_date < today, StudentFee.status.in_(["PENDING", "PARTIALLY_PAID", "OVERDUE", "UNPAID"]))
        elif target_type == "ALL_OUTSTANDING":
            q = q.filter(StudentFee.status.in_(["PENDING", "PARTIALLY_PAID", "OVERDUE", "UNPAID"]))

        if class_id:
            q = q.filter(or_(StudentFee.class_id == class_id, Student.current_class_id == class_id))
        if student_ids:
            q = q.filter(StudentFee.student_id.in_(student_ids))

        invoices = q.all()

        # Group by student
        student_map: Dict[int, List[StudentFee]] = {}
        for inv in invoices:
            student_map.setdefault(inv.student_id, []).append(inv)

        previews: List[FeeNotificationPreviewItem] = []
        eligible_cnt = 0
        missing_phone_cnt = 0
        total_outstanding_amt = 0.0

        school_name = "Hawlwadaag School"
        template = "Asc {{guardian_name}}, waxaan ku xasuusinaynaa in ardaygaaga {{student_name}} uu leeyahay lacag dugsi oo dhan ${{fee_balance}} oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — {{school_name}}"

        for s_id, inv_list in student_map.items():
            student = inv_list[0].student
            st_balance = sum(float(inv.balance_remaining) for inv in inv_list)
            if st_balance <= 0:
                continue

            total_outstanding_amt += st_balance
            overdue_cnt = sum(1 for inv in inv_list if inv.due_date < today and inv.balance_remaining > 0)

            has_valid = bool(student.guardian_phone and student.guardian_phone.strip())
            if has_valid:
                eligible_cnt += 1
            else:
                missing_phone_cnt += 1

            g_name = student.guardian_name or "Waalid"
            sample_msg = (
                template.replace("{{guardian_name}}", g_name)
                .replace("{{student_name}}", student.full_name)
                .replace("{{fee_balance}}", f"{st_balance:,.2f}")
                .replace("{{school_name}}", school_name)
            )

            previews.append(
                FeeNotificationPreviewItem(
                    student_id=student.id,
                    student_name=student.full_name,
                    admission_number=student.admission_number,
                    class_name=student.current_class.name if student.current_class else "",
                    guardian_name=g_name,
                    guardian_phone=student.guardian_phone,
                    has_valid_phone=has_valid,
                    total_outstanding=round(st_balance, 2),
                    overdue_count=overdue_cnt,
                    sample_message=sample_msg,
                )
            )

        return FeeNotificationPreviewResponse(
            total_students=len(previews),
            eligible_count=eligible_cnt,
            missing_phone_count=missing_phone_cnt,
            total_outstanding_amount=round(total_outstanding_amt, 2),
            sample_previews=previews,
        )

    def send_fee_notifications(
        self,
        admin_user: User,
        payload: FeeNotificationSendRequest
    ) -> FeeNotificationSendResponse:
        """Send automated Hormuud SMS fee notifications to guardians with deduplication and delivery tracking."""
        notif_service = NotificationService(self.db)
        today = date.today()
        today_str = today.isoformat()

        preview = self.preview_fee_notifications(
            target_type=payload.target_type,
            class_id=payload.class_id,
            student_ids=payload.student_ids,
        )

        sent_or_queued = 0
        missing_cnt = 0
        already_notified = 0

        for item in preview.sample_previews:
            if not item.has_valid_phone or not item.guardian_phone:
                missing_cnt += 1
                continue

            # Idempotency key per student and date to prevent duplicate SMS within same day
            idempotency_key = f"fee_reminder:{item.student_id}:{today_str}"
            existing_notif = notif_service.repo.get_by_idempotency_key(idempotency_key)
            if existing_notif:
                already_notified += 1
                continue

            # Create notification record in PostgreSQL
            notif = Notification(
                notification_type="FEE_REMINDER",
                title="Xasuusin Lacagta Dugsiga",
                message=item.sample_message,
                channel="SMS",
                status="PENDING",
                student_id=item.student_id,
                guardian_name=item.guardian_name,
                guardian_phone=item.guardian_phone,
                academic_year="2026/2027",
                idempotency_key=idempotency_key,
                created_by_id=admin_user.id,
                created_at=datetime.now(timezone.utc),
                attempt_count=0,
            )
            self.db.add(notif)
            self.db.flush()

            # Dispatch via Hormuud SMS provider
            notif_service._dispatch_channel(notif, item.guardian_phone)
            sent_or_queued += 1

        self.db.commit()

        self.audit_repo.log_event(
            action="FEE_NOTIFICATIONS_SENT",
            user_id=admin_user.id,
            details={
                "target_type": payload.target_type,
                "sent_count": sent_or_queued,
                "missing_phone_count": missing_cnt,
                "already_notified_count": already_notified,
            }
        )

        return FeeNotificationSendResponse(
            success=True,
            sent_or_queued_count=sent_or_queued,
            missing_contact_count=missing_cnt,
            already_notified_count=already_notified,
            total_recipients=len(preview.sample_previews),
            message=f"Dispatched {sent_or_queued} fee reminder(s) via Hormuud SMS ({already_notified} already notified today, {missing_cnt} missing phone).",
        )

    # =========================================================================
    # 6. CSV REPORT EXPORTS
    # =========================================================================

    def export_invoices_csv(self, academic_year: Optional[str] = None) -> str:
        invoices, _ = self.repo.search_student_fees(academic_year=academic_year, limit=5000)
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow([
            "Invoice Number",
            "Admission Number",
            "Student Name",
            "Class",
            "Fee Type",
            "Academic Year",
            "Amount Due ($)",
            "Discount ($)",
            "Net Due ($)",
            "Paid ($)",
            "Remaining Balance ($)",
            "Due Date",
            "Status",
            "Invoice Date",
        ])

        for inv in invoices:
            writer.writerow([
                inv.invoice_number,
                inv.student_admission_number,
                inv.student_name,
                inv.class_name,
                inv.fee_type,
                inv.academic_year,
                f"{float(inv.amount_due):.2f}",
                f"{float(inv.discount_amount):.2f}",
                f"{float(inv.net_amount):.2f}",
                f"{float(inv.total_paid):.2f}",
                f"{float(inv.balance_remaining):.2f}",
                inv.due_date.isoformat(),
                inv.status,
                inv.created_at.strftime("%Y-%m-%d %H:%M"),
            ])

        return output.getvalue()

    # =========================================================================
    # 7. CANONICAL FEES CLASS & ENROLLMENT INTEGRATION
    # =========================================================================

    def get_fee_classes(
        self,
        academic_year: Optional[str] = None,
        division: Optional[str] = None,
        has_students_only: bool = False,
    ) -> List[SchoolClassResponse]:
        classes = self.repo.get_classes_for_fees(academic_year=academic_year, division=division, has_students_only=has_students_only)
        res = []
        for c in classes:
            res.append(SchoolClassResponse(
                id=c.id,
                name=c.name,
                code=c.code,
                division=c.division or "PRIMARY",
                level=c.level or c.name,
                section=c.section,
                academic_year=c.academic_year,
                capacity=c.capacity,
                description=c.description,
                status=c.status,
                created_at=c.created_at,
                updated_at=c.updated_at,
                students_count=getattr(c, "students_count", 0),
                teachers_count=0,
                subjects_count=0,
                available_seats=max(0, c.capacity - getattr(c, "students_count", 0)),
                utilization_rate=round(getattr(c, "students_count", 0) / max(1, c.capacity), 2),
                capacity_status="NORMAL",
            ))
        return res

    def get_class_students_financial(
        self,
        class_id: int,
        academic_year: str,
    ) -> ClassStudentsFinancialResponse:
        data = self.repo.get_class_enrolled_students_with_finance(class_id=class_id, academic_year=academic_year)
        return ClassStudentsFinancialResponse(**data)

    def get_outstanding_students(
        self,
        academic_year: str,
        division: Optional[str] = None,
        class_id: Optional[int] = None,
        status_filter: Optional[str] = None,
        query: Optional[str] = None,
    ) -> OutstandingStudentsResponse:
        data = self.repo.get_outstanding_students(
            academic_year=academic_year,
            education_level=division,
            class_id=class_id,
            status_filter=status_filter,
            query=query,
        )
        return OutstandingStudentsResponse(**data)

    def get_eligible_students(
        self,
        academic_year: Optional[str] = None,
        education_level: Optional[str] = None,
        class_id: Optional[int] = None,
        query: Optional[str] = None,
        status_filter: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> FeeEligibleStudentsResponse:
        data = self.repo.get_eligible_students(
            academic_year=academic_year,
            education_level=education_level,
            class_id=class_id,
            query=query,
            status_filter=status_filter,
            skip=skip,
            limit=limit,
        )
        return FeeEligibleStudentsResponse(**data)

