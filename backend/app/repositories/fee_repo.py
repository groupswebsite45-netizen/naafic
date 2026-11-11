from typing import Optional, List, Tuple, Dict, Any
from datetime import date, datetime, timezone
from decimal import Decimal
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_, and_, extract, case
from app.models.fee import FeeStructure, StudentFee, FeePayment
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.models.school_class import SchoolClass


def _year_variants(academic_year: Optional[str]) -> List[str]:
    """Return both hyphen and slash normalized variants of an academic year, e.g. 2026/2027 and 2026-2027."""
    if not academic_year:
        return []
    cleaned = academic_year.strip()
    return list({cleaned, cleaned.replace("-", "/"), cleaned.replace("/", "-")})


class FeeRepository:
    """Enterprise repository for managing fee structures, student invoices, receipts, and PostgreSQL financial aggregates."""

    def __init__(self, db: Session):
        self.db = db

    # =========================================================================
    # 1. SEQUENTIAL NUMBER GENERATORS (DATABASE-SAFE)
    # =========================================================================

    def generate_next_invoice_number(self, academic_year: Optional[str] = None) -> str:
        """Generate unique sequential invoice number (e.g. INV-2026-000001)."""
        year = datetime.now().year
        max_id = self.db.query(func.coalesce(func.max(StudentFee.id), 0)).scalar()
        seq = int(max_id) + 1
        
        candidate = f"INV-{year}-{seq:06d}"
        while self.db.query(StudentFee).filter(StudentFee.invoice_number == candidate).first():
            seq += 1
            candidate = f"INV-{year}-{seq:06d}"
        return candidate

    def generate_next_receipt_number(self, payment_date: Optional[date] = None) -> str:
        """Generate unique sequential receipt number (e.g. RCT-2026-000001)."""
        year = (payment_date or date.today()).year
        max_id = self.db.query(func.coalesce(func.max(FeePayment.id), 0)).scalar()
        seq = int(max_id) + 1
        
        candidate = f"RCT-{year}-{seq:06d}"
        while self.db.query(FeePayment).filter(FeePayment.receipt_number == candidate).first():
            seq += 1
            candidate = f"RCT-{year}-{seq:06d}"
        return candidate

    # =========================================================================
    # 2. FEE STRUCTURES
    # =========================================================================

    def check_duplicate_active_structure(
        self,
        name: str,
        academic_year: str,
        class_id: Optional[int] = None,
        education_level: Optional[str] = None,
        exclude_id: Optional[int] = None,
    ) -> Optional[FeeStructure]:
        clean_name = name.strip().lower()
        clean_ay = academic_year.strip().replace("-", "/")
        q = (
            self.db.query(FeeStructure)
            .filter(
                FeeStructure.status == "ACTIVE",
                FeeStructure.academic_year == clean_ay,
                func.lower(FeeStructure.name) == clean_name,
            )
        )
        if class_id is not None:
            q = q.filter(FeeStructure.class_id == class_id)
        else:
            q = q.filter(FeeStructure.class_id.is_(None))
            if education_level:
                div = education_level.upper().strip()
                q = q.filter(or_(FeeStructure.education_level == div, FeeStructure.education_level.is_(None)))

        if exclude_id:
            q = q.filter(FeeStructure.id != exclude_id)
        return q.first()

    def create_structure(self, structure: FeeStructure) -> FeeStructure:
        self.db.add(structure)
        self.db.commit()
        self.db.refresh(structure)
        return structure

    def update_structure(self, structure_id: int, data: Dict[str, Any]) -> Optional[FeeStructure]:
        structure = self.get_structure_by_id(structure_id)
        if not structure:
            return None
        for key, value in data.items():
            if value is not None and hasattr(structure, key):
                setattr(structure, key, value)
        self.db.commit()
        self.db.refresh(structure)
        return structure

    def get_structure_by_id(self, structure_id: int) -> Optional[FeeStructure]:
        return (
            self.db.query(FeeStructure)
            .options(
                joinedload(FeeStructure.school_class),
                joinedload(FeeStructure.created_by),
            )
            .filter(FeeStructure.id == structure_id)
            .first()
        )

    def get_all_structures(
        self,
        academic_year: Optional[str] = None,
        class_id: Optional[int] = None,
        status: Optional[str] = None,
        education_level: Optional[str] = None,
    ) -> List[FeeStructure]:
        q = (
            self.db.query(FeeStructure)
            .outerjoin(SchoolClass, FeeStructure.class_id == SchoolClass.id)
            .options(
                joinedload(FeeStructure.school_class),
                joinedload(FeeStructure.created_by),
            )
        )
        if status and status.strip() and status.upper() != "ALL":
            q = q.filter(FeeStructure.status == status.upper().strip())
        if academic_year and academic_year.strip():
            ay = academic_year.strip().replace("-", "/")
            q = q.filter(FeeStructure.academic_year == ay)
        if class_id:
            q = q.filter(or_(FeeStructure.class_id == class_id, FeeStructure.class_id.is_(None)))
        elif education_level and education_level.strip() and education_level.upper() != "ALL":
            div = education_level.upper().strip()
            q = q.filter(
                or_(
                    FeeStructure.education_level == div,
                    SchoolClass.division == div,
                    and_(FeeStructure.class_id.is_(None), FeeStructure.education_level.is_(None))
                )
            )
        return q.order_by(
            case((FeeStructure.status == 'ACTIVE', 1), else_=2),
            FeeStructure.created_at.desc()
        ).all()

    def count_assigned_students(self, structure_id: int) -> int:
        return self.db.query(StudentFee).filter(StudentFee.fee_structure_id == structure_id).count()

    def delete_structure(self, structure_id: int) -> bool:
        structure = self.get_structure_by_id(structure_id)
        if not structure:
            return False

        # Safely detach any student fees so existing financial records are preserved
        self.db.query(StudentFee).filter(StudentFee.fee_structure_id == structure_id).update(
            {StudentFee.fee_structure_id: None},
            synchronize_session=False
        )

        self.db.delete(structure)
        self.db.commit()
        return True

    # =========================================================================
    # 3. STUDENT FEE INVOICING & ASSIGNMENT
    # =========================================================================

    def assign_fee_structure_atomic(
        self,
        target_type: str,
        fee_structure_id: int,
        student_id: Optional[int] = None,
        student_ids: Optional[List[int]] = None,
        class_id: Optional[int] = None,
        academic_year: Optional[str] = None,
        custom_amount: Optional[Decimal] = None,
        custom_due_date: Optional[date] = None,
    ) -> Tuple[List[StudentFee], int, int]:
        """
        Atomically assigns a fee structure to one student, selected students, or a whole class.
        Prevents duplicates using (student_id, fee_structure_id) unique constraint.
        Returns: (created_invoices, created_count, skipped_count)
        """
        structure = self.get_structure_by_id(fee_structure_id)
        if not structure:
            raise ValueError(f"Fee structure ID {fee_structure_id} not found.")

        target_year = academic_year.strip() if academic_year else structure.academic_year
        amount = custom_amount if custom_amount is not None else structure.amount
        due_date = custom_due_date if custom_due_date is not None else structure.due_date

        target_student_ids: List[int] = []

        if target_type == "SINGLE_STUDENT":
            if not student_id:
                raise ValueError("student_id is required for SINGLE_STUDENT assignment.")
            target_student_ids = [student_id]

        elif target_type == "SELECTED_STUDENTS":
            if not student_ids:
                raise ValueError("student_ids list is required for SELECTED_STUDENTS assignment.")
            target_student_ids = list(set(student_ids))

        elif target_type == "CLASS":
            c_id = class_id or structure.class_id
            if not c_id:
                raise ValueError("class_id is required for CLASS assignment.")
            # Find active students enrolled in target class
            enrollments = (
                self.db.query(StudentEnrollment)
                .filter(
                    StudentEnrollment.class_id == c_id,
                    StudentEnrollment.status == "ACTIVE",
                )
                .all()
            )
            target_student_ids = [en.student_id for en in enrollments]

            # If no enrollments found, fallback to students whose enrollments match
            if not target_student_ids:
                all_st = self.db.query(Student).filter(Student.status == "ACTIVE").all()
                target_student_ids = [
                    s.id for s in all_st
                    if (s.current_enrollment and s.current_enrollment.class_id == c_id) or (s.current_class and s.current_class.id == c_id)
                ]

        created_invoices: List[StudentFee] = []
        created_count = 0
        skipped_count = 0

        for s_id in target_student_ids:
            # Check for existing invoice for this student + structure
            existing = (
                self.db.query(StudentFee)
                .filter(
                    StudentFee.student_id == s_id,
                    StudentFee.fee_structure_id == structure.id,
                )
                .first()
            )
            if existing:
                skipped_count += 1
                continue

            # Determine student's class
            student = self.db.query(Student).filter(Student.id == s_id).first()
            s_class_id = None
            if student and student.current_enrollment:
                s_class_id = student.current_enrollment.class_id
            elif student and student.current_class:
                s_class_id = student.current_class.id
            else:
                s_class_id = structure.class_id

            inv_no = self.generate_next_invoice_number(target_year)

            # Determine initial status
            today = date.today()
            initial_status = "OVERDUE" if due_date < today else "PENDING"

            new_invoice = StudentFee(
                invoice_number=inv_no,
                student_id=s_id,
                class_id=s_class_id,
                fee_structure_id=structure.id,
                academic_year=target_year,
                fee_type=structure.name,
                amount_due=amount,
                discount_amount=Decimal("0.00"),
                due_date=due_date,
                status=initial_status,
            )
            self.db.add(new_invoice)
            self.db.flush()
            created_invoices.append(new_invoice)
            created_count += 1

        self.db.commit()
        for inv in created_invoices:
            self.db.refresh(inv)

        return created_invoices, created_count, skipped_count

    def get_student_fee_by_id(self, student_fee_id: int, lock_for_update: bool = False) -> Optional[StudentFee]:
        if lock_for_update:
            return self.db.query(StudentFee).filter(StudentFee.id == student_fee_id).with_for_update().first()
        return (
            self.db.query(StudentFee)
            .options(
                joinedload(StudentFee.student),
                joinedload(StudentFee.fee_structure),
                joinedload(StudentFee.school_class),
                joinedload(StudentFee.payments),
            )
            .filter(StudentFee.id == student_fee_id)
            .first()
        )

    def get_student_fee_by_invoice_number(self, invoice_number: str) -> Optional[StudentFee]:
        return (
            self.db.query(StudentFee)
            .options(
                joinedload(StudentFee.student),
                joinedload(StudentFee.fee_structure),
                joinedload(StudentFee.school_class),
                joinedload(StudentFee.payments),
            )
            .filter(StudentFee.invoice_number == invoice_number.strip())
            .first()
        )

    def search_student_fees(
        self,
        query: Optional[str] = None,
        class_id: Optional[int] = None,
        student_id: Optional[int] = None,
        fee_structure_id: Optional[int] = None,
        status: Optional[str] = None,
        academic_year: Optional[str] = None,
        education_level: Optional[str] = None,
        is_overdue_only: bool = False,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[StudentFee], int]:
        """Search student fee invoices with comprehensive multi-criteria filtering."""
        q = (
            self.db.query(StudentFee)
            .join(Student, StudentFee.student_id == Student.id)
            .options(
                joinedload(StudentFee.student),
                joinedload(StudentFee.fee_structure),
                joinedload(StudentFee.school_class),
                joinedload(StudentFee.payments),
            )
        )

        if student_id:
            q = q.filter(StudentFee.student_id == student_id)

        if class_id:
            enr_student_ids = self.db.query(StudentEnrollment.student_id).filter(
                StudentEnrollment.class_id == class_id,
                StudentEnrollment.status == "ACTIVE"
            )
            if academic_year:
                ay_c = academic_year.strip().replace("-", "/")
                enr_student_ids = enr_student_ids.filter(StudentEnrollment.academic_year == ay_c)
            q = q.filter(
                or_(
                    StudentFee.student_id.in_(enr_student_ids),
                    StudentFee.class_id == class_id
                )
            )
        elif education_level and education_level.strip() and education_level.upper() != "ALL":
            div = education_level.upper().strip()
            div_class_ids = [c[0] for c in self.db.query(SchoolClass.id).filter(SchoolClass.division == div).all()]
            enr_student_ids = self.db.query(StudentEnrollment.student_id).filter(
                StudentEnrollment.class_id.in_(div_class_ids),
                StudentEnrollment.status == "ACTIVE"
            )
            if academic_year:
                ay_clean = academic_year.strip().replace("-", "/")
                enr_student_ids = enr_student_ids.filter(StudentEnrollment.academic_year == ay_clean)
            q = q.filter(
                or_(
                    StudentFee.student_id.in_(enr_student_ids),
                    StudentFee.class_id.in_(div_class_ids)
                )
            )

        if fee_structure_id:
            q = q.filter(StudentFee.fee_structure_id == fee_structure_id)

        if academic_year:
            ay = academic_year.strip().replace("-", "/")
            q = q.filter(StudentFee.academic_year == ay)

        today = date.today()

        if is_overdue_only:
            q = q.filter(StudentFee.due_date < today, StudentFee.status.in_(["PENDING", "PARTIALLY_PAID", "OVERDUE", "UNPAID"]))

        elif status:
            st = status.upper().strip()
            if st == "OVERDUE":
                q = q.filter(
                    or_(
                        StudentFee.status == "OVERDUE",
                        and_(StudentFee.due_date < today, StudentFee.status.in_(["PENDING", "PARTIALLY_PAID", "UNPAID"])),
                    )
                )
            elif st == "UNPAID":
                q = q.filter(StudentFee.status.in_(["PENDING", "UNPAID"]))
            else:
                q = q.filter(StudentFee.status == st)

        if start_date:
            q = q.filter(StudentFee.created_at >= start_date)
        if end_date:
            q = q.filter(StudentFee.created_at <= end_date)

        if query:
            p = f"%{query.strip()}%"
            q = q.filter(
                or_(
                    Student.first_name.ilike(p),
                    Student.last_name.ilike(p),
                    Student.admission_number.ilike(p),
                    StudentFee.invoice_number.ilike(p),
                    StudentFee.fee_type.ilike(p),
                )
            )

        total = q.count()
        invoices = q.order_by(StudentFee.created_at.desc(), StudentFee.id.desc()).offset(skip).limit(limit).all()
        return invoices, total

    # =========================================================================
    # 4. PAYMENT TRANSACTIONS & RECEIPTS
    # =========================================================================

    def record_payment_atomic(
        self,
        student_fee_id: int,
        amount_paid: Decimal,
        payment_date: date,
        payment_method: str,
        recorded_by_id: Optional[int] = None,
        reference_number: Optional[str] = None,
        notes: Optional[str] = None,
        fee_month: Optional[str] = None,
    ) -> FeePayment:
        """
        Atomically records a fee payment with invoice row lock (with_for_update),
        date validation (locked past months; current + future months only),
        balance validation, unique receipt generation, and invoice status transition.
        """
        # Enforce date restriction: cannot pay for past months
        today = date.today()
        first_day_of_current_month = date(today.year, today.month, 1)
        if payment_date < first_day_of_current_month:
            raise ValueError(
                f"Payments cannot be recorded for past months ({payment_date.strftime('%B %Y')}). "
                f"Payments must be for the current month ({today.strftime('%B %Y')}) or up to future months."
            )

        student_fee = self.get_student_fee_by_id(student_fee_id, lock_for_update=True)
        if not student_fee:
            raise ValueError(f"Student fee invoice ID {student_fee_id} not found.")

        current_balance = student_fee.balance_remaining
        if current_balance <= 0.001:
            raise ValueError(
                f"Invoice {student_fee.invoice_number} for {student_fee.student_name} is already fully paid (${float(student_fee.total_paid):.2f} paid). No outstanding balance remains."
            )
        if float(amount_paid) > current_balance + 0.001:
            raise ValueError(
                f"Payment amount (${float(amount_paid):.2f}) exceeds remaining balance (${current_balance:.2f})."
            )

        receipt_no = self.generate_next_receipt_number(payment_date)

        final_notes = notes.strip() if notes else None
        if fee_month and fee_month.strip():
            month_tag = f"Fee Month: {fee_month.strip()}"
            if final_notes:
                if month_tag not in final_notes:
                    final_notes = f"{month_tag} | {final_notes}"
            else:
                final_notes = month_tag

        payment = FeePayment(
            student_fee_id=student_fee.id,
            student_id=student_fee.student_id,
            receipt_number=receipt_no,
            amount_paid=amount_paid,
            payment_date=payment_date,
            payment_method=payment_method.upper().strip(),
            reference_number=reference_number.strip() if reference_number else None,
            recorded_by_id=recorded_by_id,
            notes=final_notes,
            status="VERIFIED",
        )
        self.db.add(payment)
        self.db.flush()

        # Recalculate status from PostgreSQL
        net_due = float(student_fee.net_amount)
        total_paid_after = float(
            self.db.query(func.coalesce(func.sum(FeePayment.amount_paid), 0))
            .filter(
                FeePayment.student_fee_id == student_fee.id,
                FeePayment.status == "VERIFIED",
            )
            .scalar()
        )

        today = date.today()
        if total_paid_after >= net_due - 0.001:
            student_fee.status = "PAID"
        elif total_paid_after > 0:
            student_fee.status = "PARTIALLY_PAID"
        else:
            student_fee.status = "OVERDUE" if student_fee.due_date < today else "PENDING"

        self.db.commit()
        self.db.refresh(payment)
        self.db.refresh(student_fee)
        return payment

    def cancel_payment_atomic(self, payment_id: int, user_id: Optional[int] = None, reason: Optional[str] = None) -> FeePayment:
        """Void/cancel a payment transaction and recompute invoice status."""
        payment = self.db.query(FeePayment).filter(FeePayment.id == payment_id).with_for_update().first()
        if not payment:
            raise ValueError(f"Payment ID {payment_id} not found.")

        payment.status = "CANCELLED"
        if reason:
            payment.notes = f"{payment.notes or ''} [VOIDED: {reason}]".strip()
        self.db.flush()

        # Update parent invoice status
        student_fee = self.get_student_fee_by_id(payment.student_fee_id, lock_for_update=True)
        if student_fee:
            total_paid_after = float(
                self.db.query(func.coalesce(func.sum(FeePayment.amount_paid), 0))
                .filter(
                    FeePayment.student_fee_id == student_fee.id,
                    FeePayment.status == "VERIFIED",
                )
                .scalar()
            )
            net_due = float(student_fee.net_amount)
            today = date.today()

            if total_paid_after >= net_due - 0.001:
                student_fee.status = "PAID"
            elif total_paid_after > 0:
                student_fee.status = "PARTIALLY_PAID"
            else:
                student_fee.status = "OVERDUE" if student_fee.due_date < today else "PENDING"

        self.db.commit()
        self.db.refresh(payment)
        return payment

    def get_payment_by_id(self, payment_id: int) -> Optional[FeePayment]:
        return (
            self.db.query(FeePayment)
            .options(
                joinedload(FeePayment.student),
                joinedload(FeePayment.student_fee),
                joinedload(FeePayment.recorded_by),
            )
            .filter(FeePayment.id == payment_id)
            .first()
        )

    def list_payments(
        self,
        student_id: Optional[int] = None,
        student_fee_id: Optional[int] = None,
        payment_method: Optional[str] = None,
        status: Optional[str] = None,
        academic_year: Optional[str] = None,
        education_level: Optional[str] = None,
        class_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        query: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[FeePayment], int]:
        q = (
            self.db.query(FeePayment)
            .join(Student, FeePayment.student_id == Student.id)
            .join(StudentFee, FeePayment.student_fee_id == StudentFee.id)
            .options(
                joinedload(FeePayment.student),
                joinedload(FeePayment.student_fee),
                joinedload(FeePayment.recorded_by),
            )
        )

        if student_id:
            q = q.filter(FeePayment.student_id == student_id)
        if student_fee_id:
            q = q.filter(FeePayment.student_fee_id == student_fee_id)
        if payment_method:
            q = q.filter(FeePayment.payment_method == payment_method.upper().strip())
        if status:
            q = q.filter(FeePayment.status == status.upper().strip())
        if academic_year:
            ay = academic_year.strip().replace("-", "/")
            q = q.filter(StudentFee.academic_year == ay)
        if class_id:
            q = q.filter(StudentFee.class_id == class_id)
        elif education_level and education_level.strip() and education_level.upper() != "ALL":
            div = education_level.upper().strip()
            div_class_ids = [c[0] for c in self.db.query(SchoolClass.id).filter(SchoolClass.division == div).all()]
            enr_student_ids = self.db.query(StudentEnrollment.student_id).filter(
                StudentEnrollment.class_id.in_(div_class_ids),
                StudentEnrollment.status == "ACTIVE"
            )
            if academic_year:
                ay_clean = academic_year.strip().replace("-", "/")
                enr_student_ids = enr_student_ids.filter(StudentEnrollment.academic_year == ay_clean)
            q = q.filter(
                or_(
                    StudentFee.class_id.in_(div_class_ids),
                    and_(StudentFee.class_id.is_(None), StudentFee.student_id.in_(enr_student_ids))
                )
            )
        if start_date:
            q = q.filter(FeePayment.payment_date >= start_date)
        if end_date:
            q = q.filter(FeePayment.payment_date <= end_date)

        if query:
            p = f"%{query.strip()}%"
            q = q.filter(
                or_(
                    Student.first_name.ilike(p),
                    Student.last_name.ilike(p),
                    Student.admission_number.ilike(p),
                    FeePayment.receipt_number.ilike(p),
                    FeePayment.reference_number.ilike(p),
                )
            )

        total = q.count()
        payments = q.order_by(FeePayment.payment_date.desc(), FeePayment.id.desc()).offset(skip).limit(limit).all()
        return payments, total

    # =========================================================================
    # 5. FINANCIAL DASHBOARD & AGGREGATIONS
    # =========================================================================

    def get_financial_summary(
        self,
        academic_year: Optional[str] = None,
        education_level: Optional[str] = None,
        class_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Compute real financial telemetry KPIs directly from PostgreSQL filtered by scope."""
        today = date.today()
        ay = academic_year.strip().replace("-", "/") if academic_year else "2026/2027"

        # 1. Authoritative Student Population in target academic year
        base_enr_q = (
            self.db.query(Student.id, StudentEnrollment.class_id, SchoolClass.division)
            .join(StudentEnrollment, Student.id == StudentEnrollment.student_id)
            .join(SchoolClass, StudentEnrollment.class_id == SchoolClass.id)
            .filter(
                Student.status == "ACTIVE",
                StudentEnrollment.status == "ACTIVE",
                SchoolClass.status == "ACTIVE",
            )
        )
        if ay:
            base_enr_q = base_enr_q.filter(StudentEnrollment.academic_year == ay)

        all_enrolled_rows = base_enr_q.all()

        total_enrolled_ids = set(r[0] for r in all_enrolled_rows)
        primary_ids = set(r[0] for r in all_enrolled_rows if r[2] == "PRIMARY")
        secondary_ids = set(r[0] for r in all_enrolled_rows if r[2] == "SECONDARY")

        # Students without class in target academic year
        all_active_student_ids = set(r[0] for r in self.db.query(Student.id).filter(Student.status == "ACTIVE").all())
        students_without_class_count = len(all_active_student_ids - total_enrolled_ids)

        # Apply education level and class filters to eligible student population
        if class_id:
            scoped_student_ids = set(r[0] for r in all_enrolled_rows if r[1] == class_id)
        elif education_level and education_level.strip() and education_level.upper() != "ALL":
            div_filter = education_level.upper().strip()
            scoped_student_ids = set(r[0] for r in all_enrolled_rows if r[2] == div_filter)
        else:
            scoped_student_ids = total_enrolled_ids

        total_eligible_students = len(scoped_student_ids)
        total_students = total_eligible_students

        # 2. Determine applicable fee structure & fee rate per student
        fee_per_student = 0.0
        applicable_structure = None
        if class_id:
            # 1. Class-specific active structure
            applicable_structure = (
                self.db.query(FeeStructure)
                .filter(
                    FeeStructure.status == "ACTIVE",
                    FeeStructure.academic_year == ay,
                    FeeStructure.class_id == class_id,
                )
                .order_by(FeeStructure.created_at.desc())
                .first()
            )
            # 2. Division-level structure
            if not applicable_structure:
                cls_obj = self.db.query(SchoolClass).filter(SchoolClass.id == class_id).first()
                if cls_obj and cls_obj.division:
                    applicable_structure = (
                        self.db.query(FeeStructure)
                        .filter(
                            FeeStructure.status == "ACTIVE",
                            FeeStructure.academic_year == ay,
                            FeeStructure.class_id.is_(None),
                            or_(FeeStructure.education_level == cls_obj.division, FeeStructure.education_level.is_(None)),
                        )
                        .order_by(FeeStructure.created_at.desc())
                        .first()
                    )
        elif education_level and education_level.strip() and education_level.upper() != "ALL":
            div_f = education_level.upper().strip()
            applicable_structure = (
                self.db.query(FeeStructure)
                .filter(
                    FeeStructure.status == "ACTIVE",
                    FeeStructure.academic_year == ay,
                    FeeStructure.class_id.is_(None),
                    or_(FeeStructure.education_level == div_f, FeeStructure.education_level.is_(None)),
                )
                .order_by(FeeStructure.created_at.desc())
                .first()
            )
        else:
            applicable_structure = (
                self.db.query(FeeStructure)
                .filter(
                    FeeStructure.status == "ACTIVE",
                    FeeStructure.academic_year == ay,
                )
                .order_by(FeeStructure.created_at.desc())
                .first()
            )

        if applicable_structure:
            fee_per_student = float(applicable_structure.amount)

        # 3. Invoices in filtered scope
        inv_q = self.db.query(StudentFee).filter(StudentFee.status != "CANCELLED")
        if ay:
            inv_q = inv_q.filter(StudentFee.academic_year == ay)

        if class_id:
            inv_q = inv_q.filter(or_(StudentFee.class_id == class_id, StudentFee.student_id.in_(scoped_student_ids)))
        elif education_level and education_level.strip() and education_level.upper() != "ALL":
            inv_q = inv_q.filter(StudentFee.student_id.in_(scoped_student_ids))
        else:
            if scoped_student_ids:
                inv_q = inv_q.filter(StudentFee.student_id.in_(scoped_student_ids))

        all_invoices = inv_q.all()
        invoice_ids = [inv.id for inv in all_invoices]

        total_billed = sum(float(inv.net_amount) for inv in all_invoices)

        if invoice_ids:
            pay_q = self.db.query(FeePayment).filter(
                FeePayment.status == "VERIFIED",
                FeePayment.student_fee_id.in_(invoice_ids)
            )
            all_payments = pay_q.all()
        else:
            all_payments = []

        total_collected = sum(float(p.amount_paid) for p in all_payments)
        total_paid = total_collected

        # Total Expected:
        # If fee_per_student is configured, expected = total_students * fee_per_student
        # Otherwise fallback to total_billed
        if fee_per_student > 0:
            expected_total = round(total_students * fee_per_student, 2)
        else:
            expected_total = round(total_billed, 2)

        total_outstanding = max(0.0, round(expected_total - total_paid, 2))
        total_overdue = sum(
            float(inv.balance_remaining)
            for inv in all_invoices
            if inv.due_date < today and inv.status != "PAID" and inv.status != "CANCELLED" and inv.balance_remaining > 0.001
        )

        first_of_month = date(today.year, today.month, 1)
        collected_this_month = sum(
            float(p.amount_paid)
            for p in all_payments
            if p.payment_date >= first_of_month
        )

        total_invoices_count = len(all_invoices)
        paid_invoices_count = sum(1 for inv in all_invoices if inv.status == "PAID" or inv.balance_remaining <= 0.001)
        partial_invoices_count = sum(1 for inv in all_invoices if inv.status == "PARTIALLY_PAID" or (inv.total_paid > 0 and inv.balance_remaining > 0.001))
        overdue_invoices_count = sum(1 for inv in all_invoices if (inv.due_date < today or inv.status == "OVERDUE") and inv.status != "PAID" and inv.status != "CANCELLED" and inv.balance_remaining > 0.001)
        pending_invoices_count = sum(1 for inv in all_invoices if inv.status in ("PENDING", "UNPAID") and inv.due_date >= today and inv.total_paid == 0)
        unpaid_invoices_count = pending_invoices_count

        # 4. Distinct Student-Level Metrics
        invoiced_student_ids = set(inv.student_id for inv in all_invoices if inv.student_id in scoped_student_ids)
        invoiced_students_count = len(invoiced_student_ids)
        unbilled_students_count = max(0, total_eligible_students - invoiced_students_count)

        paid_students_count = 0
        unpaid_students_count = 0

        # Group invoices by student
        student_inv_map: Dict[int, List[StudentFee]] = {}
        for inv in all_invoices:
            if inv.student_id in scoped_student_ids:
                student_inv_map.setdefault(inv.student_id, []).append(inv)

        for sid in scoped_student_ids:
            s_invs = student_inv_map.get(sid, [])
            s_paid = sum(float(inv.total_paid) for inv in s_invs)
            s_expected = fee_per_student if fee_per_student > 0 else sum(float(i.net_amount) for i in s_invs)

            if s_expected > 0 and s_paid >= s_expected - 0.001:
                paid_students_count += 1
            else:
                unpaid_students_count += 1

        is_reconciled = bool(
            abs((total_paid + total_outstanding) - expected_total) < 0.01 and
            (paid_students_count + unpaid_students_count == total_students)
        )
        reconciliation_diff = round(abs((total_paid + total_outstanding) - expected_total), 2)
        reconciliation_msg = "Financial figures and student counts are 100% reconciled." if is_reconciled else f"Reconciliation discrepancy: ${reconciliation_diff:.2f}"

        return {
            "total_students": total_students,
            "fee_per_student": round(fee_per_student, 2),
            "expected_total": round(expected_total, 2),
            "total_billed": round(total_billed, 2),
            "total_collected": round(total_collected, 2),
            "total_paid": round(total_paid, 2),
            "total_outstanding": round(total_outstanding, 2),
            "total_overdue": round(total_overdue, 2),
            "collected_this_month": round(collected_this_month, 2),
            "this_month_collected": round(collected_this_month, 2),
            "paid_students_count": paid_students_count,
            "unpaid_students_count": unpaid_students_count,
            "total_eligible_students": total_eligible_students,
            "primary_eligible_students": len(primary_ids),
            "secondary_eligible_students": len(secondary_ids),
            "invoiced_students_count": invoiced_students_count,
            "unbilled_students_count": unbilled_students_count,
            "students_without_class_count": students_without_class_count,
            "total_invoices_count": total_invoices_count,
            "paid_invoices_count": paid_invoices_count,
            "pending_invoices_count": pending_invoices_count,
            "partial_invoices_count": partial_invoices_count,
            "overdue_invoices_count": overdue_invoices_count,
            "unpaid_invoices_count": unpaid_invoices_count,
            "is_reconciled": is_reconciled,
            "reconciliation_difference": reconciliation_diff,
            "reconciliation_message": reconciliation_msg,
        }

    def get_class_financial_summary(
        self,
        academic_year: Optional[str] = None,
        education_level: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Calculate financial totals aggregated by school class."""
        classes = self.get_classes_for_fees(academic_year=academic_year, division=education_level)
        results = []

        for c in classes:
            inv_q = self.db.query(StudentFee).filter(StudentFee.class_id == c.id, StudentFee.status != "CANCELLED")
            if academic_year:
                ay = academic_year.strip().replace("-", "/")
                inv_q = inv_q.filter(StudentFee.academic_year == ay)

            invoices = inv_q.all()
            total_students = len(set(inv.student_id for inv in invoices))
            if not total_students:
                total_students = getattr(c, "students_count", 0) or self.db.query(StudentEnrollment).filter(
                    StudentEnrollment.class_id == c.id,
                    StudentEnrollment.status == "ACTIVE"
                ).count()

            billed = sum(float(inv.net_amount) for inv in invoices)
            collected = sum(float(inv.total_paid) for inv in invoices)
            outstanding = max(0.0, billed - collected)
            rate_pct = round((collected / billed * 100), 1) if billed > 0 else 0.0

            unpaid = sum(1 for inv in invoices if inv.status in ("PENDING", "OVERDUE", "UNPAID") and inv.total_paid == 0)
            partial = sum(1 for inv in invoices if inv.status == "PARTIALLY_PAID" or (inv.total_paid > 0 and inv.balance_remaining > 0))
            paid = sum(1 for inv in invoices if inv.status == "PAID" or inv.balance_remaining <= 0)

            results.append({
                "class_id": c.id,
                "class_name": c.name,
                "class_code": c.code,
                "total_students": total_students,
                "total_billed": round(billed, 2),
                "total_collected": round(collected, 2),
                "total_outstanding": round(outstanding, 2),
                "collection_rate_pct": rate_pct,
                "unpaid_count": unpaid,
                "partial_count": partial,
                "paid_count": paid,
            })

        return results

    def get_payment_method_summary(
        self,
        academic_year: Optional[str] = None,
        education_level: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Calculate breakdown of collections grouped by payment method."""
        q = (
            self.db.query(
                FeePayment.payment_method,
                func.count(FeePayment.id).label("count"),
                func.sum(FeePayment.amount_paid).label("total_amount"),
            )
            .join(StudentFee, FeePayment.student_fee_id == StudentFee.id)
            .filter(FeePayment.status == "VERIFIED")
        )
        if academic_year:
            ay = academic_year.strip().replace("-", "/")
            q = q.filter(StudentFee.academic_year == ay)

        if education_level and education_level.strip() and education_level.upper() != "ALL":
            div = education_level.upper().strip()
            div_class_ids = [c[0] for c in self.db.query(SchoolClass.id).filter(SchoolClass.division == div).all()]
            enr_student_ids = self.db.query(StudentEnrollment.student_id).filter(
                StudentEnrollment.class_id.in_(div_class_ids),
                StudentEnrollment.status == "ACTIVE"
            )
            if academic_year:
                ay_clean = academic_year.strip().replace("-", "/")
                enr_student_ids = enr_student_ids.filter(StudentEnrollment.academic_year == ay_clean)
            q = q.filter(
                or_(
                    StudentFee.class_id.in_(div_class_ids),
                    and_(StudentFee.class_id.is_(None), StudentFee.student_id.in_(enr_student_ids))
                )
            )

        rows = q.group_by(FeePayment.payment_method).all()

        grand_total = sum(float(r[2] or 0) for r in rows)
        summary = []

        for r in rows:
            amt = float(r[2] or 0)
            pct = round((amt / grand_total * 100), 1) if grand_total > 0 else 0.0
            summary.append({
                "method": r[0],
                "count": int(r[1]),
                "total_amount": round(amt, 2),
                "percentage": pct,
            })

        return summary

    def get_monthly_collection_trends(
        self,
        academic_year: Optional[str] = None,
        education_level: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Calculate monthly collection trends for financial reporting."""
        q = (
            self.db.query(
                extract("year", FeePayment.payment_date).label("p_year"),
                extract("month", FeePayment.payment_date).label("p_month"),
                func.sum(FeePayment.amount_paid).label("total_amount"),
                func.count(FeePayment.id).label("txn_count"),
            )
            .join(StudentFee, FeePayment.student_fee_id == StudentFee.id)
            .filter(FeePayment.status == "VERIFIED")
        )
        if academic_year:
            ay = academic_year.strip().replace("-", "/")
            q = q.filter(StudentFee.academic_year == ay)

        if education_level and education_level.strip() and education_level.upper() != "ALL":
            div = education_level.upper().strip()
            div_class_ids = [c[0] for c in self.db.query(SchoolClass.id).filter(SchoolClass.division == div).all()]
            enr_student_ids = self.db.query(StudentEnrollment.student_id).filter(
                StudentEnrollment.class_id.in_(div_class_ids),
                StudentEnrollment.status == "ACTIVE"
            )
            if academic_year:
                ay_clean = academic_year.strip().replace("-", "/")
                enr_student_ids = enr_student_ids.filter(StudentEnrollment.academic_year == ay_clean)
            q = q.filter(
                or_(
                    StudentFee.class_id.in_(div_class_ids),
                    and_(StudentFee.class_id.is_(None), StudentFee.student_id.in_(enr_student_ids))
                )
            )

        rows = (
            q.group_by(
                extract("year", FeePayment.payment_date),
                extract("month", FeePayment.payment_date),
            )
            .order_by(
                extract("year", FeePayment.payment_date).asc(),
                extract("month", FeePayment.payment_date).asc(),
            )
            .all()
        )

        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        trends = []

        for r in rows:
            y = int(r[0])
            m = int(r[1])
            amt = float(r[2] or 0)
            cnt = int(r[3] or 0)
            label = f"{month_names[m - 1]} {y}"
            month_year = f"{y:04d}-{m:02d}"

            trends.append({
                "month_label": label,
                "month_year": month_year,
                "amount": round(amt, 2),
                "transaction_count": cnt,
            })

        return trends

    # =========================================================================
    # 6. STUDENT FINANCIAL LEDGER STATEMENT
    # =========================================================================

    def get_student_financial_profile(self, student_id: int, academic_year: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Retrieve complete student financial dossier (invoices, payments, statement)."""
        student = self.db.query(Student).filter(Student.id == student_id).first()
        if not student:
            return None

        ay = academic_year.strip().replace("-", "/") if academic_year else None

        inv_q = (
            self.db.query(StudentFee)
            .options(
                joinedload(StudentFee.fee_structure),
                joinedload(StudentFee.school_class),
                joinedload(StudentFee.payments),
            )
            .filter(StudentFee.student_id == student_id)
        )
        if ay:
            inv_q = inv_q.filter(StudentFee.academic_year == ay)

        invoices = inv_q.order_by(StudentFee.created_at.desc(), StudentFee.id.desc()).all()

        pay_q = (
            self.db.query(FeePayment)
            .join(StudentFee, FeePayment.student_fee_id == StudentFee.id)
            .options(joinedload(FeePayment.recorded_by))
            .filter(FeePayment.student_id == student_id)
        )
        if ay:
            pay_q = pay_q.filter(StudentFee.academic_year == ay)

        payments = pay_q.order_by(FeePayment.payment_date.desc(), FeePayment.id.desc()).all()

        billed = sum(float(inv.net_amount) for inv in invoices if inv.status != "CANCELLED")
        paid = sum(float(p.amount_paid) for p in payments if p.status == "VERIFIED")
        outstanding = max(0.0, billed - paid)

        today = date.today()
        overdue = sum(
            float(inv.balance_remaining)
            for inv in invoices
            if inv.due_date < today and inv.status != "PAID" and inv.status != "CANCELLED" and inv.balance_remaining > 0.001
        )

        class_obj = student.current_class
        class_name = class_obj.name if class_obj else "Unassigned"
        class_id = class_obj.id if class_obj else None
        education_level = class_obj.division if class_obj else "PRIMARY"

        if ay:
            enr = next((e for e in student.enrollments if (e.academic_year == ay or e.academic_year == ay.replace("/", "-")) and e.status == "ACTIVE"), None)
            if enr and enr.school_class:
                class_obj = enr.school_class
                class_name = class_obj.name
                class_id = class_obj.id
                education_level = class_obj.division

        acad_year = ay or (invoices[0].academic_year if invoices else (student.current_enrollment.academic_year if student.current_enrollment else "2026/2027"))

        return {
            "student_id": student.id,
            "admission_number": student.admission_number,
            "full_name": student.full_name,
            "student_name": student.full_name,
            "status": student.status,
            "class_id": class_id,
            "class_name": class_name,
            "current_class": class_name,
            "education_level": education_level,
            "academic_year": acad_year,
            "guardian_name": student.guardian_name,
            "guardian_phone": student.guardian_phone,
            "total_billed": round(billed, 2),
            "total_paid": round(paid, 2),
            "outstanding_balance": round(outstanding, 2),
            "overdue_balance": round(overdue, 2),
            "financial_summary": {
                "total_billed": round(billed, 2),
                "total_paid": round(paid, 2),
                "outstanding_balance": round(outstanding, 2),
                "overdue_balance": round(overdue, 2),
                "currency": "$",
            },
            "invoices": invoices,
            "payments": payments,
        }

    # =========================================================================
    # 7. CANONICAL FEES CLASS & ENROLLMENT INTEGRATION (SINGLE SOURCE OF TRUTH)
    # =========================================================================

    def get_classes_for_fees(
        self,
        academic_year: Optional[str] = None,
        division: Optional[str] = None,
        has_students_only: bool = False,
    ) -> List[SchoolClass]:
        """
        Authoritative class selector for Fees & Financial Management:
        - Only status == ACTIVE
        - Filtered by academic_year
        - Filtered by division (PRIMARY: Grade 1-8, SECONDARY: Form 1-4)
        - Excludes test, historical, and invalid classes
        - Strict educational division and level ordering
        - Option to filter only classes with active enrollments
        """
        q = self.db.query(SchoolClass).filter(SchoolClass.status == "ACTIVE")

        if academic_year and academic_year.strip():
            y_vars = _year_variants(academic_year)
            enr_class_ids = self.db.query(StudentEnrollment.class_id).filter(
                StudentEnrollment.academic_year.in_(y_vars),
                StudentEnrollment.status == "ACTIVE"
            ).distinct()
            q = q.filter(or_(SchoolClass.academic_year.in_(y_vars), SchoolClass.id.in_(enr_class_ids)))

        if division and division.strip() and division.upper() != "ALL":
            div_clean = division.upper().strip()
            q = q.filter(SchoolClass.division == div_clean)

        # Filter out test classes
        test_pattern = or_(
            SchoolClass.name.ilike("%test%"),
            SchoolClass.code.ilike("%test%"),
            SchoolClass.code.ilike("%tst%"),
            SchoolClass.name.ilike("%12subj%"),
            SchoolClass.name.ilike("%delta stream%"),
        )
        q = q.filter(~test_pattern)

        # Exclude invalid primary / secondary levels
        valid_primary = [f"Grade {i}" for i in range(1, 9)]
        valid_secondary = [f"Form {i}" for i in range(1, 5)]

        level_filter = or_(
            and_(SchoolClass.division == "PRIMARY", SchoolClass.level.in_(valid_primary)),
            and_(SchoolClass.division == "SECONDARY", SchoolClass.level.in_(valid_secondary)),
        )
        q = q.filter(level_filter)

        classes = q.all()

        # Dynamic sort: Division (PRIMARY then SECONDARY), Level (1..8, 1..4), Section
        def class_sort_key(c: SchoolClass):
            div_val = 0 if c.division == "PRIMARY" else 1
            lvl_num = 99
            if c.level:
                parts = c.level.split()
                if len(parts) == 2 and parts[1].isdigit():
                    lvl_num = int(parts[1])
            sec_val = c.section or ""
            return (div_val, lvl_num, sec_val, c.name)

        classes.sort(key=class_sort_key)

        for c in classes:
            enr_cnt_q = self.db.query(StudentEnrollment).join(Student, StudentEnrollment.student_id == Student.id).filter(
                StudentEnrollment.class_id == c.id,
                StudentEnrollment.status == "ACTIVE",
                Student.status == "ACTIVE",
            )
            if academic_year and academic_year.strip():
                enr_cnt_q = enr_cnt_q.filter(StudentEnrollment.academic_year.in_(_year_variants(academic_year)))
            c.students_count = enr_cnt_q.count()

        if has_students_only:
            classes = [c for c in classes if getattr(c, "students_count", 0) > 0]

        return classes

    def get_eligible_students(
        self,
        academic_year: Optional[str] = None,
        education_level: Optional[str] = None,
        class_id: Optional[int] = None,
        query: Optional[str] = None,
        status_filter: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """
        Authoritative single source of truth for fee-eligible students.
        Derives student population directly from active Student + StudentEnrollment + SchoolClass.
        Calculates live invoice metrics per distinct student.
        """
        ay = academic_year.strip().replace("-", "/") if academic_year else "2026/2027"
        today = date.today()

        # Base query for all active enrolled students in this academic year
        base_q = (
            self.db.query(StudentEnrollment)
            .join(Student, StudentEnrollment.student_id == Student.id)
            .join(SchoolClass, StudentEnrollment.class_id == SchoolClass.id)
            .options(
                joinedload(StudentEnrollment.student),
                joinedload(StudentEnrollment.school_class),
            )
            .filter(
                Student.status == "ACTIVE",
                StudentEnrollment.status == "ACTIVE",
                SchoolClass.status == "ACTIVE",
                StudentEnrollment.academic_year == ay,
            )
        )

        all_enrs_year = base_q.all()
        # Deduplicate by student_id to ensure exactly one record per student
        seen_year = set()
        unique_enrs_year = []
        for en in all_enrs_year:
            if en.student_id not in seen_year:
                seen_year.add(en.student_id)
                unique_enrs_year.append(en)

        primary_cnt = sum(1 for en in unique_enrs_year if en.school_class.division == "PRIMARY")
        secondary_cnt = sum(1 for en in unique_enrs_year if en.school_class.division == "SECONDARY")

        all_active_sids = set(r[0] for r in self.db.query(Student.id).filter(Student.status == "ACTIVE").all())
        without_class_cnt = len(all_active_sids - seen_year)

        # Scope filtering
        scoped_enrs = unique_enrs_year
        if class_id:
            scoped_enrs = [en for en in scoped_enrs if en.class_id == class_id]
        elif education_level and education_level.strip() and education_level.upper() != "ALL":
            div_f = education_level.upper().strip()
            scoped_enrs = [en for en in scoped_enrs if en.school_class.division == div_f]

        # Search query filter
        if query and query.strip():
            p = query.strip().lower()
            scoped_enrs = [
                en for en in scoped_enrs
                if (p in (en.student.full_name or "").lower() or p in (en.student.admission_number or "").lower())
            ]

        # Compute finances per student
        computed_items = []
        invoiced_cnt = 0
        uninvoiced_cnt = 0

        for en in scoped_enrs:
            st = en.student
            c = en.school_class

            # Fetch invoices for this student in this academic year
            invoices = (
                self.db.query(StudentFee)
                .options(joinedload(StudentFee.payments))
                .filter(
                    StudentFee.student_id == st.id,
                    StudentFee.status != "CANCELLED",
                    StudentFee.academic_year == ay,
                )
                .all()
            )

            inv_cnt = len(invoices)
            if inv_cnt > 0:
                invoiced_cnt += 1
            else:
                uninvoiced_cnt += 1

            total_billed = sum(float(inv.net_amount) for inv in invoices)
            total_paid = sum(float(inv.total_paid) for inv in invoices)
            balance = max(0.0, total_billed - total_paid)
            overdue = sum(
                float(inv.balance_remaining)
                for inv in invoices
                if inv.due_date < today and inv.status != "PAID" and inv.status != "CANCELLED" and inv.balance_remaining > 0.001
            )

            if inv_cnt == 0:
                fin_status = "UNBILLED"
            elif balance <= 0.001:
                fin_status = "PAID"
            elif total_paid > 0:
                fin_status = "PARTIAL"
            elif overdue > 0:
                fin_status = "OVERDUE"
            else:
                fin_status = "UNPAID"

            item = {
                "student_id": st.id,
                "admission_number": st.admission_number,
                "first_name": st.first_name,
                "last_name": st.last_name,
                "full_name": st.full_name,
                "gender": st.gender,
                "class_id": c.id,
                "class_name": c.name,
                "education_level": c.division,
                "academic_year": ay,
                "guardian_name": st.guardian_name,
                "guardian_phone": st.guardian_phone,
                "status": st.status,
                "invoices_count": inv_cnt,
                "total_billed": round(total_billed, 2),
                "total_paid": round(total_paid, 2),
                "outstanding_balance": round(balance, 2),
                "overdue_balance": round(overdue, 2),
                "financial_status": fin_status,
            }
            computed_items.append(item)

        # Status filtering
        if status_filter and status_filter.strip() and status_filter.upper() != "ALL":
            sf = status_filter.upper().strip()
            if sf == "INVOICED":
                computed_items = [i for i in computed_items if i["invoices_count"] > 0]
            elif sf in ("UNINVOICED", "UNBILLED"):
                computed_items = [i for i in computed_items if i["invoices_count"] == 0]
            elif sf == "PAID":
                computed_items = [i for i in computed_items if i["financial_status"] == "PAID"]
            elif sf == "UNPAID":
                computed_items = [i for i in computed_items if i["outstanding_balance"] > 0 or i["financial_status"] == "UNPAID"]
            elif sf == "PARTIAL":
                computed_items = [i for i in computed_items if i["financial_status"] == "PARTIAL"]
            elif sf == "OVERDUE":
                computed_items = [i for i in computed_items if i["financial_status"] == "OVERDUE"]

        # Sort: Division (PRIMARY first), class name, student name
        def sort_key(x):
            div_val = 0 if x["education_level"] == "PRIMARY" else 1
            return (div_val, x["class_name"], x["full_name"])

        computed_items.sort(key=sort_key)
        total_eligible = len(scoped_enrs)

        paginated_items = computed_items[skip: skip + limit]

        return {
            "total_eligible": total_eligible,
            "primary_count": primary_cnt,
            "secondary_count": secondary_cnt,
            "without_class_count": without_class_cnt,
            "invoiced_count": invoiced_cnt,
            "uninvoiced_count": uninvoiced_cnt,
            "academic_year": ay,
            "education_level": education_level,
            "class_id": class_id,
            "items": paginated_items,
        }

    def get_class_enrolled_students_with_finance(
        self,
        class_id: int,
        academic_year: str,
    ) -> Dict[str, Any]:
        """
        Loads enrolled students directly from StudentEnrollment for class_id + academic_year,
        combining live fee invoices and verified payments for full financial transparency.
        """
        cls = self.db.query(SchoolClass).filter(SchoolClass.id == class_id).first()
        if not cls:
            raise ValueError(f"Class with ID {class_id} not found.")

        ay = academic_year.strip().replace("-", "/")

        # Canonical source: StudentEnrollment
        enrollments = (
            self.db.query(StudentEnrollment)
            .options(joinedload(StudentEnrollment.student))
            .filter(
                StudentEnrollment.class_id == class_id,
                StudentEnrollment.academic_year == ay,
                StudentEnrollment.status == "ACTIVE",
            )
            .all()
        )

        today = date.today()
        student_items = []
        total_billed = Decimal("0.00")
        total_collected = Decimal("0.00")
        total_outstanding = Decimal("0.00")
        total_overdue = Decimal("0.00")

        # Sort enrollments by student name
        sorted_enrollments = sorted(
            enrollments,
            key=lambda e: (e.student.last_name if e.student else "", e.student.first_name if e.student else "")
        )

        for en in sorted_enrollments:
            st = en.student
            if not st:
                continue

            # Fetch student's invoices for this academic year and class
            invoices = (
                self.db.query(StudentFee)
                .options(joinedload(StudentFee.payments))
                .filter(
                    StudentFee.student_id == st.id,
                    StudentFee.academic_year == ay,
                    StudentFee.status != "CANCELLED",
                    or_(StudentFee.class_id == class_id, StudentFee.class_id.is_(None)),
                )
                .all()
            )

            st_billed = Decimal("0.00")
            st_paid = Decimal("0.00")
            is_overdue = False

            for inv in invoices:
                net = Decimal(str(inv.net_amount))
                st_billed += net
                paid = Decimal(str(inv.total_paid))
                st_paid += paid
                if inv.due_date < today and (net - paid) > Decimal("0.001"):
                    is_overdue = True

            st_balance = max(Decimal("0.00"), st_billed - st_paid)

            # Determine financial status
            if st_billed > Decimal("0.00") and st_balance <= Decimal("0.001"):
                calc_status = "PAID"
            elif st_paid > Decimal("0.00") and st_balance > Decimal("0.001"):
                calc_status = "PARTIAL"
            elif st_paid == Decimal("0.00") and st_billed > Decimal("0.00"):
                calc_status = "OVERDUE" if is_overdue else "UNPAID"
            else:
                calc_status = "PAID" if st_billed == Decimal("0.00") else "UNPAID"

            total_billed += st_billed
            total_collected += st_paid
            total_outstanding += st_balance
            if is_overdue:
                total_overdue += st_balance

            student_items.append({
                "student_id": st.id,
                "student_name": st.full_name,
                "admission_number": st.admission_number,
                "class_id": cls.id,
                "class_name": cls.name,
                "academic_year": ay,
                "fee_amount": float(st_billed),
                "paid_amount": float(st_paid),
                "balance": float(st_balance),
                "status": calc_status,
            })

        return {
            "class_id": cls.id,
            "class_name": cls.name,
            "academic_year": ay,
            "total_students": len(student_items),
            "total_billed": float(round(total_billed, 2)),
            "total_collected": float(round(total_collected, 2)),
            "total_outstanding": float(round(total_outstanding, 2)),
            "total_overdue": float(round(total_overdue, 2)),
            "students": student_items,
        }

    def get_outstanding_students(
        self,
        academic_year: str,
        education_level: Optional[str] = None,
        class_id: Optional[int] = None,
        status_filter: Optional[str] = None,
        query: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Returns authoritative list of outstanding/unpaid students with multi-level filtering.
        Calculates exact Decimal balances from PostgreSQL.
        """
        ay = academic_year.strip().replace("-", "/")

        # Base query for classes in scope
        class_q = self.db.query(SchoolClass).filter(
            SchoolClass.status == "ACTIVE",
            SchoolClass.academic_year == ay,
        )

        if education_level and education_level.strip() and education_level.upper() != "ALL":
            class_q = class_q.filter(SchoolClass.division == education_level.upper().strip())

        if class_id:
            class_q = class_q.filter(SchoolClass.id == class_id)

        classes_in_scope = class_q.all()
        class_ids = [c.id for c in classes_in_scope]
        class_map = {c.id: c for c in classes_in_scope}

        if not class_ids:
            return {
                "academic_year": ay,
                "education_level": education_level,
                "class_id": class_id,
                "total_students": 0,
                "paid_count": 0,
                "partial_count": 0,
                "unpaid_count": 0,
                "overdue_count": 0,
                "total_outstanding_balance": 0.0,
                "items": [],
            }

        # Active enrollments in these classes
        enr_q = (
            self.db.query(StudentEnrollment)
            .options(joinedload(StudentEnrollment.student))
            .filter(
                StudentEnrollment.class_id.in_(class_ids),
                StudentEnrollment.academic_year == ay,
                StudentEnrollment.status == "ACTIVE",
            )
        )

        enrollments = enr_q.all()
        today = date.today()

        total_scope_students = len(enrollments)
        paid_count = 0
        partial_count = 0
        unpaid_count = 0
        overdue_count = 0
        total_outstanding_balance = Decimal("0.00")

        all_computed_items = []

        for en in enrollments:
            st = en.student
            if not st:
                continue

            c = class_map.get(en.class_id)
            c_name = c.name if c else "Unknown Class"
            c_div = c.division if c else "PRIMARY"

            # Check search query
            if query and query.strip():
                p = query.strip().lower()
                full_name_l = (st.full_name or "").lower()
                adm_l = (st.admission_number or "").lower()
                if p not in full_name_l and p not in adm_l:
                    continue

            # Invoices
            invoices = (
                self.db.query(StudentFee)
                .options(joinedload(StudentFee.payments), joinedload(StudentFee.fee_structure))
                .filter(
                    StudentFee.student_id == st.id,
                    StudentFee.academic_year == ay,
                    StudentFee.status != "CANCELLED",
                )
                .all()
            )

            st_billed = Decimal("0.00")
            st_paid = Decimal("0.00")
            is_overdue = False
            primary_inv_no = None
            primary_fee_type = None
            primary_due_date = None

            for inv in invoices:
                net = Decimal(str(inv.net_amount))
                st_billed += net
                paid = Decimal(str(inv.total_paid))
                st_paid += paid
                if not primary_inv_no:
                    primary_inv_no = inv.invoice_number
                    primary_fee_type = inv.fee_type or (inv.fee_structure.name if inv.fee_structure else "Tuition")
                    primary_due_date = inv.due_date

                if inv.due_date < today and (net - paid) > Decimal("0.001"):
                    is_overdue = True

            st_balance = max(Decimal("0.00"), st_billed - st_paid)

            # Determine financial status
            if st_billed > Decimal("0.00") and st_balance <= Decimal("0.001"):
                st_status = "PAID"
                paid_count += 1
            elif st_paid > Decimal("0.00") and st_balance > Decimal("0.001"):
                st_status = "PARTIAL"
                partial_count += 1
                total_outstanding_balance += st_balance
            elif st_paid == Decimal("0.00") and st_billed > Decimal("0.00"):
                if is_overdue:
                    st_status = "OVERDUE"
                    overdue_count += 1
                else:
                    st_status = "UNPAID"
                    unpaid_count += 1
                total_outstanding_balance += st_balance
            else:
                st_status = "PAID"
                paid_count += 1

            item = {
                "student_id": st.id,
                "student_name": st.full_name,
                "admission_number": st.admission_number,
                "class_id": en.class_id,
                "class_name": c_name,
                "education_level": c_div,
                "academic_year": ay,
                "fee_type": primary_fee_type or "Tuition Fee",
                "invoice_number": primary_inv_no,
                "amount_due": float(round(st_billed, 2)),
                "paid_amount": float(round(st_paid, 2)),
                "balance": float(round(st_balance, 2)),
                "due_date": primary_due_date,
                "status": st_status,
            }
            all_computed_items.append(item)

        # Apply status filter to returned items
        filtered_items = []
        st_filter_upper = status_filter.upper().strip() if status_filter else "ALL_OUTSTANDING"

        for itm in all_computed_items:
            if st_filter_upper == "ALL_OUTSTANDING" or not status_filter or status_filter == "":
                if itm["balance"] > 0:
                    filtered_items.append(itm)
            elif st_filter_upper == "UNPAID":
                if itm["status"] == "UNPAID":
                    filtered_items.append(itm)
            elif st_filter_upper == "PARTIAL" or st_filter_upper == "PARTIALLY_PAID":
                if itm["status"] == "PARTIAL":
                    filtered_items.append(itm)
            elif st_filter_upper == "OVERDUE":
                if itm["status"] == "OVERDUE":
                    filtered_items.append(itm)
            elif st_filter_upper == "PAID":
                if itm["status"] == "PAID":
                    filtered_items.append(itm)
            elif itm["status"] == st_filter_upper:
                filtered_items.append(itm)

        # Sort: Balance desc, then student name
        filtered_items.sort(key=lambda x: (-x["balance"], x["student_name"]))

        return {
            "academic_year": ay,
            "education_level": education_level,
            "class_id": class_id,
            "total_students": total_scope_students,
            "paid_count": paid_count,
            "partial_count": partial_count,
            "unpaid_count": unpaid_count,
            "overdue_count": overdue_count,
            "total_outstanding_balance": float(round(total_outstanding_balance, 2)),
            "items": filtered_items,
        }
