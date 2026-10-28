from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, and_
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.models.user import User
from app.models.fee import StudentFee
from app.models.exam import ExamResult, Exam
from app.models.subject import Subject
from app.repositories.base_repo import BaseRepository


class StudentRepository(BaseRepository[Student]):
    """Repository for Student database operations."""

    def __init__(self, db: Session):
        super().__init__(Student, db)

    def get_by_admission_number(self, adm_no: str) -> Optional[Student]:
        return self.db.query(Student).filter(Student.admission_number == adm_no.upper().strip()).first()

    def get_by_user_id(self, user_id: int) -> Optional[Student]:
        return self.db.query(Student).filter(Student.user_id == user_id).first()

    def get_summary_metrics(self, academic_year: Optional[str] = None) -> Dict[str, int]:
        """Fetch live metrics directly from PostgreSQL."""
        total = self.db.query(func.count(Student.id)).scalar() or 0
        active = self.db.query(func.count(Student.id)).filter(Student.status == "ACTIVE").scalar() or 0
        inactive = self.db.query(func.count(Student.id)).filter(Student.status != "ACTIVE").scalar() or 0

        q_enrolled = self.db.query(StudentEnrollment.student_id).filter(
            StudentEnrollment.status == "ACTIVE"
        )
        if academic_year and academic_year.strip():
            q_enrolled = q_enrolled.filter(StudentEnrollment.academic_year == academic_year.strip())

        enrolled_student_ids = q_enrolled.distinct()

        unassigned = self.db.query(func.count(Student.id)).filter(
            ~Student.id.in_(enrolled_student_ids)
        ).scalar() or 0

        return {
            "total_students": total,
            "active_students": active,
            "inactive_students": inactive,
            "unassigned_students": unassigned,
        }

    def search_students(
        self,
        query: Optional[str] = None,
        class_id: Optional[int] = None,
        academic_year: Optional[str] = None,
        gender: Optional[str] = None,
        status: Optional[str] = None,
        has_portal: Optional[bool] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[Student], int]:
        q = self.db.query(Student)

        # Class or Academic Year filters require joining StudentEnrollment
        if class_id or academic_year:
            filters = []
            if class_id:
                filters.append(StudentEnrollment.class_id == class_id)
            if academic_year:
                filters.append(StudentEnrollment.academic_year == academic_year.strip())
            filters.append(StudentEnrollment.status == "ACTIVE")

            q = q.join(StudentEnrollment).filter(and_(*filters))

        if query:
            pattern = f"%{query.strip()}%"
            q = q.filter(
                or_(
                    Student.first_name.ilike(pattern),
                    Student.middle_name.ilike(pattern),
                    Student.last_name.ilike(pattern),
                    Student.admission_number.ilike(pattern),
                    Student.guardian_name.ilike(pattern),
                    Student.phone.ilike(pattern),
                    Student.guardian_phone.ilike(pattern)
                )
            )

        if gender:
            q = q.filter(Student.gender.ilike(gender.strip()))

        if status:
            q = q.filter(Student.status == status.upper().strip())

        if has_portal is not None:
            if has_portal:
                q = q.filter(Student.user_id.isnot(None))
            else:
                q = q.filter(Student.user_id.is_(None))

        total = q.count()
        students = q.order_by(Student.id.desc()).offset(skip).limit(limit).all()
        for s in students:
            s.has_portal_access = s.user_id is not None
            if s.user:
                s.portal_username = s.user.username
        return students, total

    def enroll_student(
        self,
        student_id: int,
        class_id: int,
        academic_year: str,
        roll_number: Optional[str] = None,
        start_date=None,
        end_date=None
    ) -> StudentEnrollment:
        # Check if active enrollment exists for this year
        prev = self.db.query(StudentEnrollment).filter(
            StudentEnrollment.student_id == student_id,
            StudentEnrollment.academic_year == academic_year.strip()
        ).first()

        if prev:
            prev.class_id = class_id
            prev.roll_number = roll_number
            if start_date:
                prev.start_date = start_date
            if end_date:
                prev.end_date = end_date
            prev.status = "ACTIVE"
            self.db.commit()
            self.db.refresh(prev)
            return prev

        enrollment = StudentEnrollment(
            student_id=student_id,
            class_id=class_id,
            academic_year=academic_year.strip(),
            roll_number=roll_number,
            start_date=start_date,
            end_date=end_date,
            status="ACTIVE"
        )
        self.db.add(enrollment)
        self.db.commit()
        self.db.refresh(enrollment)
        return enrollment

    def get_student_financial_summary(self, student_id: int) -> Dict[str, Any]:
        fees = self.db.query(StudentFee).filter(StudentFee.student_id == student_id).all()
        total_billed = sum(f.total_amount for f in fees)
        total_paid = sum(f.paid_amount for f in fees)
        outstanding = sum(f.balance for f in fees)
        return {
            "total_billed": round(total_billed, 2),
            "total_paid": round(total_paid, 2),
            "outstanding_balance": round(outstanding, 2),
            "fees_count": len(fees)
        }

    def get_student_fees(self, student_id: int) -> List[Dict[str, Any]]:
        fees = self.db.query(StudentFee).filter(StudentFee.student_id == student_id).order_by(StudentFee.id.desc()).all()
        result = []
        for f in fees:
            result.append({
                "id": f.id,
                "fee_name": f.fee_structure.name if f.fee_structure else "Tuition Fee",
                "academic_year": f.academic_year,
                "total_amount": f.total_amount,
                "paid_amount": f.paid_amount,
                "balance": f.balance,
                "status": f.status,
                "due_date": f.due_date,
                "created_at": f.created_at
            })
        return result

    def get_student_exam_results(self, student_id: int) -> List[Dict[str, Any]]:
        results = self.db.query(ExamResult).filter(ExamResult.student_id == student_id).order_by(ExamResult.id.desc()).all()
        output = []
        for r in results:
            exam = r.exam
            subject = r.subject
            output.append({
                "id": r.id,
                "exam_name": exam.name if exam else "Assessment",
                "exam_type": exam.exam_type if exam else "EXAM",
                "subject_name": subject.name if subject else "General",
                "academic_year": exam.academic_year if exam else "2025-2026",
                "marks_obtained": float(r.marks_obtained) if r.marks_obtained is not None else 0.0,
                "total_marks": float(exam.total_marks) if exam and exam.total_marks else 100.0,
                "grade": r.grade,
                "remarks": r.remarks,
                "exam_date": exam.start_date if exam else None
            })
        return output

    def get_students_by_class(self, class_id: int, academic_year: Optional[str] = None) -> List[Student]:
        q = self.db.query(Student).join(StudentEnrollment).filter(
            StudentEnrollment.class_id == class_id,
            StudentEnrollment.status == "ACTIVE",
            Student.status == "ACTIVE"
        )
        if academic_year:
            q = q.filter(StudentEnrollment.academic_year == academic_year.strip())
        return q.order_by(Student.first_name.asc()).all()

    def count_active_students(self) -> int:
        return self.db.query(Student).filter(Student.status == "ACTIVE").count()
