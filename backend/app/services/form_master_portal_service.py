from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date, timedelta, timezone
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_, desc, case
from fastapi import HTTPException, status

from app.models.user import User
from app.models.teacher import Teacher
from app.models.school_class import SchoolClass
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.models.subject import Subject
from app.models.exam import Exam, ExamResult
from app.models.attendance import Attendance
from app.models.fee import StudentFee, FeePayment, FeeStructure
from app.models.form_master import FormMasterAssignment
from app.repositories.form_master_repo import FormMasterRepository
from app.repositories.teacher_repo import TeacherRepository
from app.core.grading import calculate_grade, is_passing
from app.schemas.form_master import (
    FormMasterClassSummary,
    FormMasterStudentItem,
    FormMasterDashboardData,
    FormMasterResultsData,
    FormMasterAttendanceData,
    FormMasterFeesData,
)


class FormMasterPortalService:
    """
    Dedicated Service for Form Masters to monitor academic results,
    attendance, and fees for their assigned classes with strict data isolation.
    All operations are strictly read-only regarding student marks and finance.
    """

    def __init__(self, db: Session):
        self.db = db
        self.repo = FormMasterRepository(db)
        self.teacher_repo = TeacherRepository(db)

    def get_authenticated_teacher(self, user: User) -> Teacher:
        teacher = self.teacher_repo.get_by_user_id(user.id)
        if not teacher and user.email:
            teacher = self.teacher_repo.get_by_email(user.email)
            if teacher and not teacher.user_id:
                teacher.user_id = user.id
                self.db.commit()
                self.db.refresh(teacher)
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No faculty/teacher profile associated with this user account."
            )
        return teacher

    def get_form_master_context(
        self, user: User, academic_year: Optional[str] = None
    ) -> Tuple[Teacher, List[FormMasterAssignment]]:
        teacher = self.get_authenticated_teacher(user)
        assignments = self.repo.get_active_assignments_for_teacher(teacher.id, academic_year=academic_year)
        if not assignments:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You are not an active Form Master for any class."
            )
        return teacher, assignments

    def verify_class_access(
        self, user: User, class_id: int, academic_year: Optional[str] = None
    ) -> Tuple[Teacher, FormMasterAssignment]:
        teacher, assignments = self.get_form_master_context(user, academic_year=academic_year)
        matching = next((a for a in assignments if a.class_id == class_id), None)
        if not matching:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Class ID {class_id} is not officially assigned to you as Form Master."
            )
        return teacher, matching

    def check_is_form_master(self, user: User) -> Dict[str, Any]:
        """Lightweight pre-flight check for UI to render Form Master menu item."""
        try:
            teacher = self.get_authenticated_teacher(user)
            assignments = self.repo.get_active_assignments_for_teacher(teacher.id)
            return {
                "is_form_master": len(assignments) > 0,
                "classes_count": len(assignments),
                "classes": [
                    {
                        "class_id": a.class_id,
                        "class_name": a.class_name,
                        "academic_year": a.academic_year
                    }
                    for a in assignments
                ]
            }
        except Exception:
            return {
                "is_form_master": False,
                "classes_count": 0,
                "classes": []
            }

    def get_my_form_classes(
        self, user: User, academic_year: Optional[str] = None
    ) -> List[FormMasterClassSummary]:
        teacher, assignments = self.get_form_master_context(user, academic_year=academic_year)

        results: List[FormMasterClassSummary] = []
        for a in assignments:
            sc = a.school_class
            student_count = self.db.query(StudentEnrollment).filter(
                StudentEnrollment.class_id == a.class_id,
                StudentEnrollment.academic_year == a.academic_year,
                StudentEnrollment.status == "ACTIVE"
            ).count()

            results.append(
                FormMasterClassSummary(
                    id=sc.id,
                    name=sc.name,
                    code=sc.code,
                    division=sc.division,
                    level=sc.level,
                    section=sc.section,
                    academic_year=a.academic_year,
                    capacity=sc.capacity or 40,
                    student_count=student_count,
                    assignment_id=a.id,
                    appointed_at=a.appointed_at
                )
            )

        return results

    # =========================================================================
    # 1. DASHBOARD
    # =========================================================================

    def get_class_dashboard(
        self, user: User, class_id: int, academic_year: Optional[str] = None
    ) -> FormMasterDashboardData:
        teacher, assignment = self.verify_class_access(user, class_id, academic_year=academic_year)
        year = assignment.academic_year

        # Get all assigned classes for teacher to allow quick tab switching
        all_assigned = self.get_my_form_classes(user, academic_year=year)
        selected_summary = next(c for c in all_assigned if c.id == class_id)

        # Enrolled students
        enrollments = (
            self.db.query(StudentEnrollment)
            .filter(
                StudentEnrollment.class_id == class_id,
                StudentEnrollment.academic_year == year,
                StudentEnrollment.status == "ACTIVE"
            )
            .all()
        )
        total_students = len(enrollments)
        student_ids = [e.student_id for e in enrollments]

        if not student_ids:
            return FormMasterDashboardData(
                assigned_classes=all_assigned,
                selected_class=selected_summary,
                total_students=0,
                attendance_rate=100.0,
                students_with_poor_performance_count=0,
                students_with_frequent_absences_count=0,
                students_with_outstanding_fees_count=0,
                total_outstanding_fees=0.0,
                poor_performance_students=[],
                frequent_absences_students=[],
                outstanding_fees_students=[],
                recent_activity=[],
                alerts=[]
            )

        # --- ATTENDANCE STATS ---
        attendance_records = (
            self.db.query(Attendance)
            .filter(
                Attendance.class_id == class_id,
                Attendance.academic_year == year
            )
            .all()
        )
        total_att = len(attendance_records)
        present_count = sum(1 for a in attendance_records if a.status in ("PRESENT", "LATE"))
        overall_attendance_rate = round((present_count / total_att * 100.0), 1) if total_att > 0 else 100.0

        # Absence count per student
        absent_by_student: Dict[int, int] = {}
        for a in attendance_records:
            if a.status == "ABSENT":
                absent_by_student[a.student_id] = absent_by_student.get(a.student_id, 0) + 1

        frequent_absences_students = []
        for e in enrollments:
            abs_count = absent_by_student.get(e.student_id, 0)
            if abs_count >= 3:
                s = e.student
                frequent_absences_students.append({
                    "student_id": s.id,
                    "admission_number": s.admission_number,
                    "name": s.full_name,
                    "absent_count": abs_count,
                    "phone": s.phone or s.guardian_phone,
                    "guardian_name": s.guardian_name
                })
        frequent_absences_students.sort(key=lambda x: x["absent_count"], reverse=True)

        # --- ACADEMIC RESULTS STATS ---
        # Get all exam results for students in this class
        exam_results = (
            self.db.query(ExamResult)
            .filter(
                ExamResult.student_id.in_(student_ids),
                ExamResult.class_id == class_id
            )
            .all()
        )

        student_scores: Dict[int, List[float]] = {}
        student_fails: Dict[int, int] = {}
        for r in exam_results:
            if r.marks_obtained is not None and r.attendance_status == "PRESENT":
                score = float(r.marks_obtained)
                student_scores.setdefault(r.student_id, []).append(score)
                if score < 50.0 or r.grade == "F":
                    student_fails[r.student_id] = student_fails.get(r.student_id, 0) + 1

        poor_performance_students = []
        for e in enrollments:
            s_id = e.student_id
            scores = student_scores.get(s_id, [])
            avg_score = round(sum(scores) / len(scores), 1) if scores else None
            fails = student_fails.get(s_id, 0)
            if (avg_score is not None and avg_score < 50.0) or fails > 0:
                s = e.student
                poor_performance_students.append({
                    "student_id": s.id,
                    "admission_number": s.admission_number,
                    "name": s.full_name,
                    "average_score": avg_score,
                    "failing_subjects_count": fails,
                    "exams_count": len(scores)
                })
        poor_performance_students.sort(
            key=lambda x: (x["failing_subjects_count"], -(x["average_score"] or 0)),
            reverse=True
        )

        # --- FEES STATS ---
        student_fees = (
            self.db.query(StudentFee)
            .filter(
                StudentFee.student_id.in_(student_ids),
                StudentFee.academic_year == year
            )
            .all()
        )

        total_outstanding_fees = 0.0
        outstanding_students_dict: Dict[int, Dict[str, Any]] = {}
        for sf in student_fees:
            bal = sf.balance_remaining
            if bal > 0:
                total_outstanding_fees += bal
                s = sf.student
                if s.id not in outstanding_students_dict:
                    outstanding_students_dict[s.id] = {
                        "student_id": s.id,
                        "admission_number": s.admission_number,
                        "name": s.full_name,
                        "total_due": float(sf.amount_due),
                        "total_paid": float(sf.total_paid),
                        "balance": bal,
                        "status": sf.status,
                        "due_date": str(sf.due_date) if sf.due_date else None,
                        "is_overdue": sf.due_date and sf.due_date < date.today()
                    }
                else:
                    curr = outstanding_students_dict[s.id]
                    curr["total_due"] += float(sf.amount_due)
                    curr["total_paid"] += float(sf.total_paid)
                    curr["balance"] += bal
                    if sf.due_date and sf.due_date < date.today():
                        curr["is_overdue"] = True

        outstanding_fees_students = list(outstanding_students_dict.values())
        outstanding_fees_students.sort(key=lambda x: x["balance"], reverse=True)

        # --- RECENT ACTIVITY ---
        recent_activity: List[Dict[str, Any]] = []
        # Recent exams
        recent_exams = (
            self.db.query(Exam)
            .filter(Exam.class_id == class_id, Exam.academic_year == year)
            .order_by(Exam.created_at.desc())
            .limit(5)
            .all()
        )
        for rx in recent_exams:
            recent_activity.append({
                "type": "EXAM",
                "title": f"Exam: {rx.name} ({rx.subject.name if rx.subject else ''})",
                "timestamp": rx.created_at.isoformat() if rx.created_at else None,
                "badge": rx.status,
                "details": f"Type: {rx.exam_type} | Max Marks: {float(rx.max_marks)}"
            })

        # Recent attendance dates logged
        recent_att_dates = (
            self.db.query(Attendance.date, Attendance.subject_id, func.count(Attendance.id))
            .filter(Attendance.class_id == class_id, Attendance.academic_year == year)
            .group_by(Attendance.date, Attendance.subject_id)
            .order_by(Attendance.date.desc())
            .limit(5)
            .all()
        )
        for rad in recent_att_dates:
            subj = self.db.query(Subject).filter(Subject.id == rad[1]).first()
            recent_activity.append({
                "type": "ATTENDANCE",
                "title": f"Attendance logged for {subj.name if subj else 'Subject'}",
                "timestamp": str(rad[0]),
                "badge": f"{rad[2]} records",
                "details": f"Date: {rad[0]}"
            })

        # --- CRITICAL ALERTS ---
        alerts: List[Dict[str, Any]] = []
        if frequent_absences_students:
            alerts.append({
                "level": "WARNING",
                "category": "ATTENDANCE",
                "title": f"{len(frequent_absences_students)} Student(s) with Chronic Absences",
                "description": f"{len(frequent_absences_students)} students have recorded 3 or more absences this term and require intervention."
            })

        if poor_performance_students:
            alerts.append({
                "level": "WARNING",
                "category": "ACADEMIC",
                "title": f"{len(poor_performance_students)} Student(s) Need Academic Support",
                "description": f"{len(poor_performance_students)} students are failing one or more subjects or have an average below passing grade (50%)."
            })

        overdue_count = sum(1 for s in outstanding_fees_students if s.get("is_overdue"))
        if overdue_count > 0:
            alerts.append({
                "level": "INFO",
                "category": "FEES",
                "title": f"{overdue_count} Student(s) with Overdue Fee Balances",
                "description": f"{overdue_count} students have past-due fee invoices. Form Masters can monitor balances and coordinate with guardians."
            })

        return FormMasterDashboardData(
            assigned_classes=all_assigned,
            selected_class=selected_summary,
            total_students=total_students,
            attendance_rate=overall_attendance_rate,
            students_with_poor_performance_count=len(poor_performance_students),
            students_with_frequent_absences_count=len(frequent_absences_students),
            students_with_outstanding_fees_count=len(outstanding_fees_students),
            total_outstanding_fees=round(total_outstanding_fees, 2),
            poor_performance_students=poor_performance_students[:10],
            frequent_absences_students=frequent_absences_students[:10],
            outstanding_fees_students=outstanding_fees_students[:10],
            recent_activity=recent_activity[:10],
            alerts=alerts
        )

    # =========================================================================
    # 2. STUDENTS ROSTER
    # =========================================================================

    def get_class_students(
        self, user: User, class_id: int, academic_year: Optional[str] = None
    ) -> List[FormMasterStudentItem]:
        teacher, assignment = self.verify_class_access(user, class_id, academic_year=academic_year)
        year = assignment.academic_year

        enrollments = (
            self.db.query(StudentEnrollment)
            .filter(
                StudentEnrollment.class_id == class_id,
                StudentEnrollment.academic_year == year,
                StudentEnrollment.status == "ACTIVE"
            )
            .order_by(StudentEnrollment.roll_number, StudentEnrollment.id)
            .all()
        )
        student_ids = [e.student_id for e in enrollments]
        if not student_ids:
            return []

        # Attendance map
        attendance_rows = (
            self.db.query(
                Attendance.student_id,
                func.count(Attendance.id).label("total"),
                func.sum(case((Attendance.status == "PRESENT", 1), else_=0)).label("present"),
                func.sum(case((Attendance.status == "ABSENT", 1), else_=0)).label("absent"),
                func.sum(case((Attendance.status == "LATE", 1), else_=0)).label("late"),
            )
            .filter(
                Attendance.student_id.in_(student_ids),
                Attendance.class_id == class_id,
                Attendance.academic_year == year
            )
            .group_by(Attendance.student_id)
            .all()
        )
        att_map = {
            r[0]: {
                "total": r[1] or 0,
                "present": r[2] or 0,
                "absent": r[3] or 0,
                "late": r[4] or 0,
            }
            for r in attendance_rows
        }

        # Academic results map
        results_rows = (
            self.db.query(ExamResult)
            .filter(
                ExamResult.student_id.in_(student_ids),
                ExamResult.class_id == class_id
            )
            .all()
        )
        exam_scores_map: Dict[int, List[float]] = {}
        exam_fails_map: Dict[int, int] = {}
        for r in results_rows:
            if r.marks_obtained is not None and r.attendance_status == "PRESENT":
                sc = float(r.marks_obtained)
                exam_scores_map.setdefault(r.student_id, []).append(sc)
                if sc < 50.0 or r.grade == "F":
                    exam_fails_map[r.student_id] = exam_fails_map.get(r.student_id, 0) + 1

        # Fee map
        fee_rows = (
            self.db.query(StudentFee)
            .filter(
                StudentFee.student_id.in_(student_ids),
                StudentFee.academic_year == year
            )
            .all()
        )
        fee_map: Dict[int, Dict[str, Any]] = {}
        for sf in fee_rows:
            entry = fee_map.setdefault(sf.student_id, {"invoiced": 0.0, "paid": 0.0, "balance": 0.0, "statuses": []})
            entry["invoiced"] += float(sf.amount_due)
            entry["paid"] += float(sf.total_paid)
            entry["balance"] += sf.balance_remaining
            entry["statuses"].append(sf.status)

        items: List[FormMasterStudentItem] = []
        for e in enrollments:
            s = e.student
            att = att_map.get(s.id, {"total": 0, "present": 0, "absent": 0, "late": 0})
            att_total = att["total"]
            att_rate = round(((att["present"] + att["late"]) / att_total * 100.0), 1) if att_total > 0 else 100.0

            scores = exam_scores_map.get(s.id, [])
            avg_m = round(sum(scores) / len(scores), 1) if scores else None
            fails = exam_fails_map.get(s.id, 0)

            fee_info = fee_map.get(s.id, {"invoiced": 0.0, "paid": 0.0, "balance": 0.0, "statuses": []})
            bal = round(fee_info["balance"], 2)
            if not fee_info["statuses"]:
                f_status = "NO_FEES"
            elif bal <= 0:
                f_status = "PAID"
            elif fee_info["paid"] > 0:
                f_status = "PARTIALLY_PAID"
            else:
                f_status = "UNPAID"

            items.append(
                FormMasterStudentItem(
                    student_id=s.id,
                    admission_number=s.admission_number,
                    first_name=s.first_name,
                    last_name=s.last_name,
                    full_name=s.full_name,
                    gender=s.gender,
                    phone=s.phone,
                    guardian_name=s.guardian_name,
                    guardian_phone=s.guardian_phone,
                    guardian_email=s.guardian_email,
                    guardian_relationship=s.guardian_relationship,
                    enrollment_status=e.status,
                    total_exams_taken=len(scores),
                    average_marks=avg_m,
                    failing_subjects_count=fails,
                    has_poor_academic_performance=(avg_m is not None and avg_m < 50.0) or fails > 0,
                    total_attendance_records=att_total,
                    present_count=att["present"],
                    absent_count=att["absent"],
                    late_count=att["late"],
                    attendance_rate=att_rate,
                    has_frequent_absences=att["absent"] >= 3,
                    fee_total_invoiced=round(fee_info["invoiced"], 2),
                    fee_total_paid=round(fee_info["paid"], 2),
                    fee_balance=bal,
                    fee_status=f_status,
                    has_overdue_fees=bal > 0
                )
            )

        return items

    # =========================================================================
    # 3. ACADEMIC RESULTS MONITORING (CROSS-SUBJECT READ-ONLY)
    # =========================================================================

    def get_class_results(
        self,
        user: User,
        class_id: int,
        academic_year: Optional[str] = None,
        exam_type: Optional[str] = None,
        exam_id: Optional[int] = None,
        subject_id: Optional[int] = None
    ) -> FormMasterResultsData:
        teacher, assignment = self.verify_class_access(user, class_id, academic_year=academic_year)
        year = assignment.academic_year
        sc = assignment.school_class

        # Available exams for this class
        exam_query = self.db.query(Exam).filter(
            Exam.class_id == class_id,
            Exam.academic_year == year
        )
        if exam_type:
            exam_query = exam_query.filter(Exam.exam_type == exam_type)
        if exam_id:
            exam_query = exam_query.filter(Exam.id == exam_id)
        if subject_id:
            exam_query = exam_query.filter(Exam.subject_id == subject_id)

        all_class_exams = self.db.query(Exam).filter(
            Exam.class_id == class_id,
            Exam.academic_year == year
        ).all()
        available_exam_types = sorted(list({e.exam_type for e in all_class_exams}))
        filtered_exams = exam_query.all()
        filtered_exam_ids = [e.id for e in filtered_exams]

        # All subjects associated with this class
        subjects = (
            self.db.query(Subject)
            .join(Exam, Exam.subject_id == Subject.id)
            .filter(Exam.class_id == class_id, Exam.academic_year == year)
            .distinct()
            .all()
        )
        subject_list = [{"id": s.id, "name": s.name, "code": s.code} for s in subjects]

        # Enrolled students
        enrollments = (
            self.db.query(StudentEnrollment)
            .filter(
                StudentEnrollment.class_id == class_id,
                StudentEnrollment.academic_year == year,
                StudentEnrollment.status == "ACTIVE"
            )
            .all()
        )
        student_ids = [e.student_id for e in enrollments]

        # Fetch results
        results_query = self.db.query(ExamResult).filter(
            ExamResult.class_id == class_id,
            ExamResult.student_id.in_(student_ids)
        )
        if filtered_exam_ids:
            results_query = results_query.filter(ExamResult.exam_id.in_(filtered_exam_ids))

        results = results_query.all()

        # Build student performance matrix
        # Map: student_id -> { subject_id: { score, grade, status, exam_name } }
        matrix: Dict[int, Dict[int, Dict[str, Any]]] = {}
        for r in results:
            if r.marks_obtained is not None and r.attendance_status == "PRESENT":
                matrix.setdefault(r.student_id, {})[r.subject_id] = {
                    "marks": float(r.marks_obtained),
                    "grade": r.grade,
                    "status": r.status,
                    "attendance_status": r.attendance_status
                }
            elif r.attendance_status in ("ABSENT", "EXCUSED"):
                matrix.setdefault(r.student_id, {})[r.subject_id] = {
                    "marks": None,
                    "grade": r.attendance_status,
                    "status": r.status,
                    "attendance_status": r.attendance_status
                }

        students_data = []
        all_averages = []
        for e in enrollments:
            s = e.student
            sub_scores = matrix.get(s.id, {})
            valid_scores = [v["marks"] for v in sub_scores.values() if v["marks"] is not None]
            total_marks = sum(valid_scores)
            avg_marks = round(total_marks / len(valid_scores), 2) if valid_scores else None
            failing_count = sum(1 for v in sub_scores.values() if (v["marks"] is not None and v["marks"] < 50.0) or v["grade"] == "F")

            if avg_marks is not None:
                all_averages.append(avg_marks)

            students_data.append({
                "student_id": s.id,
                "admission_number": s.admission_number,
                "name": s.full_name,
                "roll_number": e.roll_number,
                "subject_scores": {
                    str(subj_id): data for subj_id, data in sub_scores.items()
                },
                "total_marks": round(total_marks, 2),
                "average_marks": avg_marks,
                "subjects_taken": len(valid_scores),
                "failing_subjects_count": failing_count,
                "is_poor_performer": (avg_marks is not None and avg_marks < 50.0) or failing_count > 0,
                "grade": "F" if (avg_marks is not None and avg_marks < 50.0) else ("A" if (avg_marks or 0) >= 80 else ("B" if (avg_marks or 0) >= 70 else ("C" if (avg_marks or 0) >= 60 else "D")))
            })

        # Rank students by average marks
        students_data.sort(key=lambda x: (x["average_marks"] or -1), reverse=True)
        for rank, st in enumerate(students_data, 1):
            st["rank"] = rank if st["average_marks"] is not None else None

        class_average = round(sum(all_averages) / len(all_averages), 2) if all_averages else 0.0
        pass_count = sum(1 for st in students_data if st["average_marks"] is not None and st["average_marks"] >= 50.0)
        pass_rate = round((pass_count / len(all_averages) * 100.0), 1) if all_averages else 0.0
        poor_performers_count = sum(1 for st in students_data if st["is_poor_performer"])
        top_performers_count = sum(1 for st in students_data if st["average_marks"] is not None and st["average_marks"] >= 80.0)

        return FormMasterResultsData(
            class_id=sc.id,
            class_name=sc.name,
            class_code=sc.code,
            academic_year=year,
            available_exam_types=available_exam_types,
            available_exams=[
                {
                    "id": ex.id,
                    "name": ex.name,
                    "exam_type": ex.exam_type,
                    "subject_id": ex.subject_id,
                    "subject_name": ex.subject.name if ex.subject else "",
                    "max_marks": float(ex.max_marks),
                    "status": ex.status,
                    "published_at": ex.published_at.isoformat() if ex.published_at else None
                }
                for ex in filtered_exams
            ],
            subjects=subject_list,
            students=students_data,
            class_average=class_average,
            total_students=len(students_data),
            pass_rate=pass_rate,
            poor_performers_count=poor_performers_count,
            top_performers_count=top_performers_count
        )

    # =========================================================================
    # 4. ATTENDANCE MONITORING
    # =========================================================================

    def get_class_attendance(
        self,
        user: User,
        class_id: int,
        academic_year: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        subject_id: Optional[int] = None
    ) -> FormMasterAttendanceData:
        teacher, assignment = self.verify_class_access(user, class_id, academic_year=academic_year)
        year = assignment.academic_year
        sc = assignment.school_class

        query = self.db.query(Attendance).filter(
            Attendance.class_id == class_id,
            Attendance.academic_year == year
        )
        if start_date:
            query = query.filter(Attendance.date >= start_date)
        if end_date:
            query = query.filter(Attendance.date <= end_date)
        if subject_id:
            query = query.filter(Attendance.subject_id == subject_id)

        records = query.order_by(Attendance.date.desc(), Attendance.period).all()
        total_records = len(records)
        present_cnt = sum(1 for r in records if r.status == "PRESENT")
        absent_cnt = sum(1 for r in records if r.status == "ABSENT")
        late_cnt = sum(1 for r in records if r.status == "LATE")
        excused_cnt = sum(1 for r in records if r.status == "EXCUSED")
        att_rate = round(((present_cnt + late_cnt) / total_records * 100.0), 1) if total_records > 0 else 100.0

        # Enrolled students
        enrollments = (
            self.db.query(StudentEnrollment)
            .filter(
                StudentEnrollment.class_id == class_id,
                StudentEnrollment.academic_year == year,
                StudentEnrollment.status == "ACTIVE"
            )
            .all()
        )

        student_att_map: Dict[int, Dict[str, int]] = {}
        for r in records:
            stat = student_att_map.setdefault(r.student_id, {"present": 0, "absent": 0, "late": 0, "excused": 0, "total": 0})
            stat["total"] += 1
            if r.status == "PRESENT":
                stat["present"] += 1
            elif r.status == "ABSENT":
                stat["absent"] += 1
            elif r.status == "LATE":
                stat["late"] += 1
            elif r.status == "EXCUSED":
                stat["excused"] += 1

        students_summary = []
        for e in enrollments:
            s = e.student
            st = student_att_map.get(s.id, {"present": 0, "absent": 0, "late": 0, "excused": 0, "total": 0})
            s_rate = round(((st["present"] + st["late"]) / st["total"] * 100.0), 1) if st["total"] > 0 else 100.0
            students_summary.append({
                "student_id": s.id,
                "admission_number": s.admission_number,
                "name": s.full_name,
                "gender": s.gender,
                "total_records": st["total"],
                "present_count": st["present"],
                "absent_count": st["absent"],
                "late_count": st["late"],
                "excused_count": st["excused"],
                "attendance_rate": s_rate,
                "is_frequent_absentee": st["absent"] >= 3 or (st["total"] >= 5 and s_rate < 75.0)
            })

        students_summary.sort(key=lambda x: x["absent_count"], reverse=True)

        # Monthly trend
        monthly_map: Dict[str, Dict[str, int]] = {}
        for r in records:
            month_key = r.date.strftime("%Y-%m")
            m = monthly_map.setdefault(month_key, {"present": 0, "absent": 0, "late": 0, "total": 0})
            m["total"] += 1
            if r.status in ("PRESENT", "LATE"):
                m["present"] += 1
            elif r.status == "ABSENT":
                m["absent"] += 1

        monthly_trend = [
            {
                "month": m,
                "total": data["total"],
                "present": data["present"],
                "absent": data["absent"],
                "rate": round((data["present"] / data["total"] * 100.0), 1) if data["total"] > 0 else 100.0
            }
            for m, data in sorted(monthly_map.items())
        ]

        recent_logs = [
            {
                "id": r.id,
                "date": str(r.date),
                "period": r.period,
                "subject_name": r.subject.name if r.subject else "",
                "student_name": r.student.full_name if r.student else "",
                "status": r.status,
                "remarks": r.remarks
            }
            for r in records[:50]
        ]

        return FormMasterAttendanceData(
            class_id=sc.id,
            class_name=sc.name,
            class_code=sc.code,
            academic_year=year,
            overall_stats={
                "total_records": total_records,
                "present_count": present_cnt,
                "absent_count": absent_cnt,
                "late_count": late_cnt,
                "excused_count": excused_cnt,
                "attendance_rate": att_rate
            },
            students=students_summary,
            recent_records=recent_logs,
            monthly_trend=monthly_trend
        )

    # =========================================================================
    # 5. STUDENT FEES MONITORING (READ-ONLY)
    # =========================================================================

    def get_class_fees(
        self, user: User, class_id: int, academic_year: Optional[str] = None
    ) -> FormMasterFeesData:
        teacher, assignment = self.verify_class_access(user, class_id, academic_year=academic_year)
        year = assignment.academic_year
        sc = assignment.school_class

        # Enrolled students
        enrollments = (
            self.db.query(StudentEnrollment)
            .filter(
                StudentEnrollment.class_id == class_id,
                StudentEnrollment.academic_year == year,
                StudentEnrollment.status == "ACTIVE"
            )
            .all()
        )
        student_ids = [e.student_id for e in enrollments]

        student_fees = (
            self.db.query(StudentFee)
            .filter(
                StudentFee.student_id.in_(student_ids),
                StudentFee.academic_year == year
            )
            .order_by(StudentFee.due_date.asc())
            .all()
        )

        total_invoiced = sum(float(sf.amount_due) for sf in student_fees)
        total_paid = sum(float(sf.total_paid) for sf in student_fees)
        total_outstanding = max(0.0, total_invoiced - total_paid)

        paid_count = 0
        partial_count = 0
        unpaid_count = 0
        overdue_count = 0
        today = date.today()

        # Group fees by student
        fees_by_student: Dict[int, List[StudentFee]] = {}
        for sf in student_fees:
            fees_by_student.setdefault(sf.student_id, []).append(sf)

        students_fee_list = []
        for e in enrollments:
            s = e.student
            s_fees = fees_by_student.get(s.id, [])
            s_due = sum(float(f.amount_due) for f in s_fees)
            s_paid = sum(float(f.total_paid) for f in s_fees)
            s_bal = max(0.0, s_due - s_paid)

            is_overdue = False
            for f in s_fees:
                if f.due_date and f.due_date < today and f.balance_remaining > 0:
                    is_overdue = True
                    break

            if not s_fees:
                s_status = "NO_FEES"
            elif s_bal <= 0:
                s_status = "PAID"
                paid_count += 1
            elif s_paid > 0:
                s_status = "PARTIALLY_PAID"
                partial_count += 1
            else:
                s_status = "UNPAID"
                unpaid_count += 1

            if is_overdue:
                overdue_count += 1

            # Invoices detail
            invoices = [
                {
                    "invoice_number": f.invoice_number,
                    "fee_type": f.fee_type or (f.fee_structure.name if f.fee_structure else "Fee"),
                    "amount_due": float(f.amount_due),
                    "amount_paid": float(f.total_paid),
                    "balance": f.balance_remaining,
                    "status": f.status,
                    "due_date": str(f.due_date) if f.due_date else None,
                    "is_overdue": f.due_date and f.due_date < today and f.balance_remaining > 0
                }
                for f in s_fees
            ]

            # Payment history
            payments = []
            for f in s_fees:
                for p in f.payments:
                    payments.append({
                        "receipt_number": p.receipt_number,
                        "amount": float(p.amount_paid),
                        "payment_date": str(p.payment_date),
                        "payment_method": p.payment_method,
                        "status": p.status
                    })

            students_fee_list.append({
                "student_id": s.id,
                "admission_number": s.admission_number,
                "name": s.full_name,
                "gender": s.gender,
                "guardian_name": s.guardian_name,
                "guardian_phone": s.guardian_phone,
                "total_due": round(s_due, 2),
                "total_paid": round(s_paid, 2),
                "balance": round(s_bal, 2),
                "status": s_status,
                "is_overdue": is_overdue,
                "invoices": invoices,
                "payments": payments
            })

        students_fee_list.sort(key=lambda x: x["balance"], reverse=True)

        return FormMasterFeesData(
            class_id=sc.id,
            class_name=sc.name,
            class_code=sc.code,
            academic_year=year,
            summary={
                "total_invoiced": round(total_invoiced, 2),
                "total_paid": round(total_paid, 2),
                "total_outstanding": round(total_outstanding, 2),
                "paid_students_count": paid_count,
                "partially_paid_students_count": partial_count,
                "unpaid_students_count": unpaid_count,
                "overdue_students_count": overdue_count,
                "total_students": len(enrollments)
            },
            students=students_fee_list
        )
