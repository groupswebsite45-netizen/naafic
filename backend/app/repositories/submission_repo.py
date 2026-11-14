from typing import Optional, List, Dict, Any, Tuple
from decimal import Decimal
from datetime import datetime, date, timezone
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, and_
from app.models.exam import Exam, ExamResult
from app.models.result_submission import ResultSubmission
from app.models.result_release import ResultReleaseBatch
from app.models.student_result_view import StudentResultView
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.models.school_class import SchoolClass
from app.models.subject import Subject
from app.models.teacher import Teacher
from app.models.teacher_assignment import TeacherAssignment
from app.models.user import User
from app.core.grading import calculate_grade


def _build_exam_filter(exam_name: Optional[str]):
    if not exam_name or exam_name.upper().strip() in ("ALL", ""):
        return None
    e_upper = exam_name.upper().strip()
    clauses = [Exam.name == exam_name, Exam.name.ilike(exam_name)]
    if "MID" in e_upper:
        clauses.extend([Exam.exam_type == "MID_TERM", Exam.name.ilike("%Mid%")])
    elif "FINAL" in e_upper:
        clauses.extend([Exam.exam_type == "FINAL", Exam.name.ilike("%Final%")])
    elif "MONTH" in e_upper:
        clauses.extend([Exam.exam_type == "MONTHLY", Exam.name.ilike("%Month%")])
    elif "QUIZ" in e_upper:
        clauses.extend([Exam.exam_type == "QUIZ", Exam.name.ilike("%Quiz%")])
    return or_(*clauses)


def _build_submission_filter(exam_name: Optional[str]):
    if not exam_name or exam_name.upper().strip() in ("ALL", ""):
        return None
    e_upper = exam_name.upper().strip()
    clauses = [ResultSubmission.exam_name == exam_name, ResultSubmission.exam_name.ilike(exam_name)]
    if "MID" in e_upper:
        clauses.extend([ResultSubmission.exam_name.ilike("%Mid%")])
    elif "FINAL" in e_upper:
        clauses.extend([ResultSubmission.exam_name.ilike("%Final%")])
    elif "MONTH" in e_upper:
        clauses.extend([ResultSubmission.exam_name.ilike("%Month%")])
    elif "QUIZ" in e_upper:
        clauses.extend([ResultSubmission.exam_name.ilike("%Quiz%")])
    return or_(*clauses)


def _compute_grade_str(marks_val: Any, max_val: Any) -> str:
    """Helper to safely calculate letter grade string from marks and max_marks."""
    if marks_val is None or max_val is None:
        return "F"
    try:
        m = Decimal(str(marks_val))
        mx = Decimal(str(max_val))
        if mx <= 0:
            return "F"
        g, _, _ = calculate_grade(m, mx)
        return g
    except Exception:
        return "F"


class SubmissionRepository:
    """Repository handling examination mark submissions, teacher progress, and admin verification."""

    def __init__(self, db: Session):
        self.db = db

    def get_filter_academic_years(self) -> List[str]:
        """Fetch unified authoritative academic year."""
        return ["2026/2027"]

    def get_exam_series_for_year(self, academic_year: str) -> List[str]:
        """Fetch distinct exam series names for a specific academic year."""
        y = academic_year.strip()
        y_variants = [y, y.replace("/", "-"), y.replace("-", "/")]
        names = [
            r[0] for r in self.db.query(Exam.name).filter(
                Exam.academic_year.in_(y_variants)
            ).distinct().order_by(Exam.name).all()
            if r[0]
        ]
        sub_names = [
            r[0] for r in self.db.query(ResultSubmission.exam_name).filter(
                ResultSubmission.academic_year.in_(y_variants)
            ).distinct().order_by(ResultSubmission.exam_name).all()
            if r[0]
        ]
        combined = []
        for n in names + sub_names:
            if n and n not in combined:
                combined.append(n)
        defaults = ["Mid-Term Examination", "Final Examination", "Monthly Examination", "Quiz Examination"]
        for d in defaults:
            if d not in combined:
                combined.append(d)
        return combined

    def get_overview_stats(self, academic_year: str, exam_name: str) -> Dict[str, Any]:
        """
        Compute top-level dashboard statistics directly from PostgreSQL:
        - CLASSES count
        - SUBMISSIONS (completed / total)
        - PENDING submissions count
        - APPROVED submissions count
        - RELEASED submissions count
        """
        y = academic_year.strip()
        y_variants = [y, y.replace("/", "-"), y.replace("-", "/")]

        exam_filter = _build_exam_filter(exam_name)
        sub_filter = _build_submission_filter(exam_name)

        exam_q = self.db.query(Exam).filter(Exam.academic_year.in_(y_variants))
        if exam_filter is not None:
            exam_q = exam_q.filter(exam_filter)
        exams = exam_q.all()

        class_ids = list(set(e.class_id for e in exams))
        classes_count = len(class_ids)
        total_assignments = len(exams)

        sub_q = self.db.query(ResultSubmission).filter(ResultSubmission.academic_year.in_(y_variants))
        if sub_filter is not None:
            sub_q = sub_q.filter(sub_filter)
        submissions = sub_q.all()

        sub_by_exam = {s.exam_id: s for s in submissions}

        submitted_count = 0
        pending_count = 0
        approved_count = 0
        released_count = 0

        for exam in exams:
            sub = sub_by_exam.get(exam.id)
            if not sub:
                pending_count += 1
            elif sub.status == "RELEASED":
                released_count += 1
                approved_count += 1
                submitted_count += 1
            elif sub.status == "APPROVED":
                approved_count += 1
                submitted_count += 1
            elif sub.status in ("SUBMITTED", "UNDER_REVIEW"):
                submitted_count += 1
            else:  # DRAFT, PARTIAL, RETURNED
                pending_count += 1

        return {
            "academic_year": academic_year,
            "exam_name": exam_name,
            "classes_count": classes_count,
            "submissions_completed": submitted_count,
            "submissions_total": total_assignments,
            "pending_count": pending_count,
            "approved_count": approved_count,
            "released_count": released_count,
        }

    def get_classes_summary(self, academic_year: str, exam_name: str) -> List[Dict[str, Any]]:
        """
        Get result completion summary for classes with real assignments/exams in the selected academic year.
        Deduplicates classes by class_id and only includes classes that have assigned curriculum or exams.
        """
        y = academic_year.strip()
        y_variants = [y, y.replace("/", "-"), y.replace("-", "/")]

        exam_filter = _build_exam_filter(exam_name)
        sub_filter = _build_submission_filter(exam_name)

        # 1. Fetch exams for this academic year & exam series
        exam_q = self.db.query(Exam).filter(Exam.academic_year.in_(y_variants))
        if exam_filter is not None:
            exam_q = exam_q.filter(exam_filter)
        exams = exam_q.all()

        exams_by_class = {}
        for e in exams:
            exams_by_class.setdefault(e.class_id, []).append(e)

        # 2. Fetch active teacher assignments for this academic year
        assignments = self.db.query(TeacherAssignment).filter(
            TeacherAssignment.academic_year.in_(y_variants),
            TeacherAssignment.status == "ACTIVE"
        ).all()
        assigns_by_class = {}
        for a in assignments:
            assigns_by_class.setdefault(a.class_id, []).append(a)

        # 3. Fetch submissions for this academic year & exam series
        sub_q = self.db.query(ResultSubmission).filter(ResultSubmission.academic_year.in_(y_variants))
        if sub_filter is not None:
            sub_q = sub_q.filter(sub_filter)
        submissions = sub_q.all()
        subs_by_class_subj = {(s.class_id, s.subject_id): s for s in submissions}

        # 4. Relevant class IDs: all classes with active assignments or exams for this year
        relevant_class_ids = sorted(list(set(assigns_by_class.keys()) | set(exams_by_class.keys()) | set(s.class_id for s in submissions)))

        if not relevant_class_ids:
            return []

        classes = self.db.query(SchoolClass).filter(
            SchoolClass.id.in_(relevant_class_ids),
            SchoolClass.status == "ACTIVE"
        ).order_by(SchoolClass.name).all()

        # 5. Fetch all exam results for these exams
        exam_ids = [e.id for e in exams]
        results = self.db.query(ExamResult).filter(
            ExamResult.exam_id.in_(exam_ids)
        ).all() if exam_ids else []
        res_by_exam = {}
        for r in results:
            res_by_exam.setdefault(r.exam_id, []).append(r)

        summaries = []
        for c in classes:
            c_exams = exams_by_class.get(c.id, [])
            c_assigns = assigns_by_class.get(c.id, [])

            assigned_subj_ids = {a.subject_id for a in c_assigns if a.subject and a.subject.status == "ACTIVE"}
            all_subj_ids = sorted(list(assigned_subj_ids))
            subjects_count = len(all_subj_ids)

            if subjects_count == 0:
                continue

            # Enrolled student count
            student_count = self.db.query(StudentEnrollment).filter(
                StudentEnrollment.class_id == c.id,
                StudentEnrollment.academic_year.in_(y_variants),
                StudentEnrollment.status == "ACTIVE"
            ).count()

            expected_results = student_count * subjects_count

            # Evaluate each expected subject
            c_exam_by_subj = {e.subject_id: e for e in c_exams}
            complete_subjects = 0
            released_subjects = 0
            submitted_subjects = 0
            pending_subjects = 0
            tot_submitted_results = 0
            tot_approved_results = 0
            tot_released_results = 0

            for s_id in all_subj_ids:
                ex = c_exam_by_subj.get(s_id)
                sub = subs_by_class_subj.get((c.id, s_id))
                ex_results = res_by_exam.get(ex.id, []) if ex else []

                completed_in_subj = sum(
                    1 for r in ex_results
                    if r.attendance_status in ("ABSENT", "EXCUSED") or (r.attendance_status == "PRESENT" and r.marks_obtained is not None)
                )
                submitted_in_subj = sum(1 for r in ex_results if r.status in ("SUBMITTED", "APPROVED", "RELEASED"))
                approved_in_subj = sum(1 for r in ex_results if r.status in ("APPROVED", "RELEASED"))
                released_in_subj = sum(1 for r in ex_results if r.status == "RELEASED")

                tot_submitted_results += submitted_in_subj
                tot_approved_results += approved_in_subj
                tot_released_results += released_in_subj

                is_subj_complete = (completed_in_subj >= student_count and student_count > 0)
                is_subj_released = (released_in_subj >= student_count and student_count > 0) or (sub and sub.status == "RELEASED")
                is_subj_submitted = (sub and sub.status in ("SUBMITTED", "APPROVED", "RELEASED"))

                if is_subj_released:
                    released_subjects += 1
                if is_subj_complete:
                    complete_subjects += 1
                if is_subj_submitted:
                    submitted_subjects += 1
                if not is_subj_complete and not is_subj_released:
                    pending_subjects += 1

            viewed_count = self.db.query(StudentResultView).filter(
                StudentResultView.class_id == c.id,
                StudentResultView.academic_year.in_(y_variants),
                StudentResultView.exam_name == exam_name
            ).count()

            progress_pct = round((complete_subjects / subjects_count) * 100) if subjects_count > 0 else 0

            if released_subjects >= subjects_count and subjects_count > 0:
                class_status = "RELEASED"
            elif complete_subjects >= subjects_count and subjects_count > 0:
                class_status = "COMPLETE"
            elif complete_subjects > 0 or submitted_subjects > 0:
                class_status = "PARTIAL"
            else:
                class_status = "PENDING"

            summaries.append({
                "class_id": c.id,
                "class_name": c.name,
                "class_code": c.code,
                "academic_year": academic_year,
                "students_count": student_count,
                "subjects_count": subjects_count,
                "complete_subjects_count": complete_subjects,
                "pending_subjects_count": pending_subjects,
                "released_subjects_count": released_subjects,
                "submitted_subjects_count": submitted_subjects,
                "progress_percent": progress_pct,
                "expected_results": expected_results,
                "submitted_results": tot_submitted_results,
                "pending_results": max(0, expected_results - tot_submitted_results),
                "approved_results": tot_approved_results,
                "released_results": tot_released_results,
                "viewed_results": viewed_count,
                "status": class_status,
            })

        return summaries

    def get_class_dashboard(self, class_id: int, academic_year: str, exam_name: str) -> Optional[Dict[str, Any]]:
        """
        Build the comprehensive Class Result Dashboard and Subject Matrix.
        Shows exact counts and status for expected subjects in the class curriculum,
        strictly without creating synthetic database records during read.
        """
        school_class = self.db.query(SchoolClass).filter(SchoolClass.id == class_id).first()
        if not school_class:
            return None

        y = academic_year.strip()
        y_variants = [y, y.replace("/", "-"), y.replace("-", "/")]

        # 1. Fetch enrolled students
        enrollments = self.db.query(StudentEnrollment).filter(
            StudentEnrollment.class_id == class_id,
            StudentEnrollment.academic_year.in_(y_variants),
            StudentEnrollment.status == "ACTIVE"
        ).all()
        students_count = len(enrollments)

        # 2. Fetch teacher assignments for curriculum subjects
        assignments = self.db.query(TeacherAssignment).filter(
            TeacherAssignment.class_id == class_id,
            TeacherAssignment.academic_year.in_(y_variants),
            TeacherAssignment.status == "ACTIVE"
        ).all()
        tch_by_subject = {a.subject_id: a.teacher for a in assignments if a.teacher}
        assigned_subj_ids = {a.subject_id for a in assignments if a.subject and a.subject.status == "ACTIVE"}

        # 3. Fetch exams for this class in this exam series
        exam_filter = _build_exam_filter(exam_name)
        sub_filter = _build_submission_filter(exam_name)

        exam_q = self.db.query(Exam).filter(
            Exam.class_id == class_id,
            Exam.academic_year.in_(y_variants)
        )
        if exam_filter is not None:
            exam_q = exam_q.filter(exam_filter)
        class_exams = exam_q.order_by(Exam.subject_id).all()
        exam_by_subject = {e.subject_id: e for e in class_exams}

        # 4. Discover required subjects (strictly active assignments)
        all_subj_ids = sorted(list(assigned_subj_ids))
        subjects_count = len(all_subj_ids)
        expected_results = students_count * subjects_count

        # 5. Fetch submissions
        sub_q = self.db.query(ResultSubmission).filter(
            ResultSubmission.class_id == class_id,
            ResultSubmission.academic_year.in_(y_variants)
        )
        if sub_filter is not None:
            sub_q = sub_q.filter(sub_filter)
        submissions = sub_q.all()
        sub_by_subject = {s.subject_id: s for s in submissions}

        # 6. Check existing release batch
        release_batch = self.db.query(ResultReleaseBatch).filter(
            ResultReleaseBatch.class_id == class_id,
            ResultReleaseBatch.academic_year.in_(y_variants),
            ResultReleaseBatch.exam_name == exam_name,
            ResultReleaseBatch.status == "RELEASED"
        ).order_by(ResultReleaseBatch.id.desc()).first()

        # 7. Pre-fetch all results for existing exams
        exam_ids = [ex.id for ex in class_exams]
        all_results = self.db.query(ExamResult).filter(ExamResult.exam_id.in_(exam_ids)).all() if exam_ids else []
        res_lookup = {(r.exam_id, r.student_id): r for r in all_results}

        subjects_matrix = []
        tot_submitted = 0
        tot_approved = 0
        tot_released = 0
        complete_subjects_count = 0
        released_subjects_count = 0

        all_subjects = self.db.query(Subject).filter(Subject.id.in_(all_subj_ids)).all() if all_subj_ids else []
        subject_entity_by_id = {s.id: s for s in all_subjects}

        for s_id in all_subj_ids:
            subj = subject_entity_by_id.get(s_id)
            ex = exam_by_subject.get(s_id)
            sub = sub_by_subject.get(s_id)
            teacher = (sub.teacher if sub and sub.teacher else None) or (ex.teacher if ex and ex.teacher else None) or tch_by_subject.get(s_id)

            if ex:
                results = [r for r in all_results if r.exam_id == ex.id]
                marks_entered = len(results)
                attended_count = sum(1 for r in results if r.attendance_status == "PRESENT")
                absent_count = sum(1 for r in results if r.attendance_status in ("ABSENT", "EXCUSED"))
                present_with_marks = sum(1 for r in results if r.attendance_status == "PRESENT" and r.marks_obtained is not None)
                completed_count = present_with_marks + absent_count
                pending = max(0, students_count - completed_count)

                marks_submitted = sum(1 for r in results if r.status in ("SUBMITTED", "APPROVED", "RELEASED"))
                marks_approved = sum(1 for r in results if r.status in ("APPROVED", "RELEASED"))
                marks_released = sum(1 for r in results if r.status == "RELEASED")
            else:
                marks_entered = 0
                attended_count = 0
                absent_count = 0
                completed_count = 0
                pending = students_count
                marks_submitted = 0
                marks_approved = 0
                marks_released = 0

            tot_submitted += marks_submitted
            tot_approved += marks_approved
            tot_released += marks_released

            is_complete = (pending == 0 and students_count > 0 and ex is not None)
            is_released = (marks_released >= students_count and students_count > 0) or (sub and sub.status == "RELEASED")
            release_status = "RELEASED" if is_released else "NOT RELEASED"

            if is_complete:
                complete_subjects_count += 1
            if is_released:
                released_subjects_count += 1

            if is_released:
                subj_status = "RELEASED"
            elif sub and sub.status == "RETURNED":
                subj_status = "RETURNED"
            elif is_complete:
                subj_status = "COMPLETE"
            elif sub and sub.status in ("SUBMITTED", "APPROVED"):
                subj_status = "SUBMITTED"
            elif marks_entered > 0:
                subj_status = "INCOMPLETE"
            else:
                subj_status = "PENDING"

            subjects_matrix.append({
                "subject_id": subj.id if subj else s_id,
                "subject_name": subj.name if subj else f"Subject #{s_id}",
                "subject_code": subj.code if subj else "",
                "teacher_id": teacher.id if teacher else (sub.teacher_id if sub else None),
                "teacher_name": teacher.full_name if teacher else "Unassigned",
                "teacher_email": teacher.email if teacher else None,
                "exam_id": ex.id if ex else None,
                "submission_id": sub.id if sub else None,
                "status": subj_status,
                "release_status": release_status,
                "is_complete": is_complete,
                "expected_students": students_count,
                "attended_students": attended_count,
                "marks_entered": marks_entered,
                "marks_submitted": marks_submitted,
                "marks_approved": marks_approved,
                "marks_released": marks_released,
                "pending_students": pending,
                "absent_students": absent_count,
                "submitted_at": sub.submitted_at if sub else None,
                "approved_at": sub.approved_at if sub else None,
                "return_reason": sub.return_reason if sub else None,
            })

        # Build Multi-Subject Student Matrix
        student_matrix = []
        for en in enrollments:
            std = en.student
            if not std:
                continue
            scores = {}
            tot_obtained = Decimal("0.00")
            tot_max = Decimal("0.00")
            has_failed = False
            has_any_score = False

            for s_id in all_subj_ids:
                ex = exam_by_subject.get(s_id)
                subj = subject_entity_by_id.get(s_id)
                res = res_lookup.get((ex.id, std.id)) if ex else None
                att_status = res.attendance_status if res else "PRESENT"
                marks = res.marks_obtained if res else None
                grade = res.grade if res else None
                st = res.status if res else "DRAFT"
                pass_m = ex.pass_marks if ex else Decimal("50.00")
                max_m = ex.max_marks if ex else Decimal("100.00")

                if (att_status == "PRESENT" and marks is not None and marks < pass_m) or att_status in ("ABSENT", "EXCUSED"):
                    has_failed = True

                if marks is not None:
                    tot_obtained += Decimal(str(marks))
                    tot_max += Decimal(str(max_m))
                    has_any_score = True

                scores[str(s_id)] = {
                    "subject_id": s_id,
                    "subject_name": subj.name if subj else f"Subject #{s_id}",
                    "subject_code": subj.code if subj else "",
                    "attendance_status": att_status,
                    "marks_obtained": marks,
                    "max_marks": max_m,
                    "pass_marks": pass_m,
                    "grade": grade,
                    "remarks": res.remarks if res else None,
                    "status": st,
                }

            avg_marks = round(tot_obtained / len(all_subj_ids), 1) if all_subj_ids and has_any_score else None

            student_matrix.append({
                "student_id": std.id,
                "admission_number": std.admission_number,
                "student_name": std.full_name,
                "roll_number": en.roll_number,
                "gender": std.gender,
                "scores": scores,
                "total_marks": tot_obtained if has_any_score else None,
                "average_marks": avg_marks,
                "passed_all": not has_failed,
            })

        student_matrix.sort(key=lambda x: x["student_name"])

        # Overall class status
        pending_subjects_count = max(0, subjects_count - complete_subjects_count)
        not_released_subjects_count = max(0, subjects_count - released_subjects_count)

        if released_subjects_count >= subjects_count and subjects_count > 0:
            overall_status = "RELEASED"
        elif complete_subjects_count >= subjects_count and subjects_count > 0:
            overall_status = "COMPLETE"
        elif complete_subjects_count > 0:
            overall_status = "PARTIAL"
        else:
            overall_status = "PENDING"

        # Viewed results count
        viewed_count = self.db.query(StudentResultView).filter(
            StudentResultView.class_id == class_id,
            StudentResultView.academic_year.in_(y_variants),
            StudentResultView.exam_name == exam_name
        ).count()

        can_release_full = (complete_subjects_count >= subjects_count) and (subjects_count > 0)
        can_release_partial = (complete_subjects_count > 0) and (complete_subjects_count < subjects_count)

        return {
            "class_id": class_id,
            "class_name": school_class.name,
            "academic_year": academic_year,
            "exam_name": exam_name,
            "students_count": students_count,
            "subjects_count": subjects_count,
            "complete_subjects_count": complete_subjects_count,
            "pending_subjects_count": pending_subjects_count,
            "released_subjects_count": released_subjects_count,
            "not_released_subjects_count": not_released_subjects_count,
            "expected_results": expected_results,
            "submitted_results": tot_submitted,
            "pending_results": max(0, expected_results - tot_submitted),
            "approved_results": tot_approved,
            "released_results": tot_released,
            "viewed_results": viewed_count,
            "status": overall_status,
            "subjects_matrix": subjects_matrix,
            "student_matrix": student_matrix,
            "can_release_full": can_release_full,
            "can_release_partial": can_release_partial,
            "release_batch_code": release_batch.batch_code if release_batch else None,
            "released_at": release_batch.released_at if release_batch else None,
        }

    def get_teacher_submissions(
        self,
        academic_year: Optional[str] = None,
        exam_name: Optional[str] = None,
        teacher_id: Optional[int] = None,
        class_id: Optional[int] = None,
        subject_id: Optional[int] = None,
        status: Optional[str] = None,
        exam_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Admin Teacher Submissions / Results Management query.
        Lists actual submissions with relational data from PostgreSQL, without creating synthetic records.
        """
        exam_q = self.db.query(Exam)
        if academic_year and academic_year.strip() and academic_year.upper() != "ALL":
            y = academic_year.strip()
            exam_q = exam_q.filter(Exam.academic_year.in_([y, y.replace("/", "-"), y.replace("-", "/")]))
        if exam_name and exam_name.strip() and exam_name.upper() != "ALL":
            exam_q = exam_q.filter(Exam.name == exam_name)
        if exam_type and exam_type.strip() and exam_type.upper() != "ALL":
            exam_q = exam_q.filter(Exam.exam_type.ilike(exam_type.strip()))
        if class_id:
            exam_q = exam_q.filter(Exam.class_id == class_id)
        if subject_id:
            exam_q = exam_q.filter(Exam.subject_id == subject_id)

        exams = exam_q.order_by(Exam.start_date.desc(), Exam.id.desc()).all()

        items = []
        for ex in exams:
            sub = self.db.query(ResultSubmission).filter(
                ResultSubmission.exam_id == ex.id,
                ResultSubmission.class_id == ex.class_id,
                ResultSubmission.subject_id == ex.subject_id
            ).first()

            teacher = None
            if sub and sub.teacher:
                teacher = sub.teacher
            elif ex.teacher:
                teacher = ex.teacher
            else:
                y = ex.academic_year
                assign = self.db.query(TeacherAssignment).filter(
                    TeacherAssignment.class_id == ex.class_id,
                    TeacherAssignment.subject_id == ex.subject_id,
                    TeacherAssignment.academic_year.in_([y, y.replace("/", "-"), y.replace("-", "/")]),
                    TeacherAssignment.status == "ACTIVE"
                ).first()
                if assign and assign.teacher:
                    teacher = assign.teacher

            if teacher_id and (not teacher or teacher.id != teacher_id):
                continue

            y = ex.academic_year
            enrolled_count = self.db.query(StudentEnrollment).filter(
                StudentEnrollment.class_id == ex.class_id,
                StudentEnrollment.academic_year.in_([y, y.replace("/", "-"), y.replace("-", "/")]),
                StudentEnrollment.status == "ACTIVE"
            ).count()

            results = self.db.query(ExamResult).filter(ExamResult.exam_id == ex.id).all()
            completed_count = sum(
                1 for r in results
                if r.attendance_status in ("ABSENT", "EXCUSED") or (r.attendance_status == "PRESENT" and r.marks_obtained is not None)
            )
            pending_count = max(0, enrolled_count - completed_count)

            st = sub.status if sub else ("DRAFT" if completed_count > 0 else "PENDING")

            s_class = ex.school_class
            subject = ex.subject
            effective_deadline = (sub.submission_deadline if sub and sub.submission_deadline else ex.result_submission_deadline)

            now_utc = datetime.now(timezone.utc)
            is_overdue = False
            deadline_status = "ON_TRACK"

            if effective_deadline:
                dl = effective_deadline
                if dl.tzinfo is None:
                    dl = dl.replace(tzinfo=timezone.utc)
                if dl < now_utc and st not in ("SUBMITTED", "APPROVED", "RELEASED"):
                    is_overdue = True
                    deadline_status = "OVERDUE"
                elif ex.status == "CLOSED":
                    deadline_status = "CLOSED"
                elif (dl - now_utc).total_seconds() < 86400 * 3:
                    deadline_status = "APPROACHING"
                else:
                    deadline_status = "ON_TRACK"
            elif ex.status == "CLOSED":
                deadline_status = "CLOSED"

            present_in_sub = sum(1 for r in results if r.attendance_status == "PRESENT")
            absent_in_sub = sum(1 for r in results if r.attendance_status in ("ABSENT", "EXCUSED"))
            complaints_in_sub = sum(1 for r in results if r.complaint and r.complaint.strip())

            if status and status.strip() and status.upper() != "ALL":
                st_filter = status.upper().strip()
                if st_filter in ("AWAITING", "AWAITING TEACHER SUBMISSION", "DRAFT"):
                    if st not in ("DRAFT", "PARTIAL", "NOT_STARTED", "PENDING"):
                        continue
                elif st_filter in ("SUBMITTED", "SUBMITTED TO ADMIN"):
                    if st not in ("SUBMITTED", "UNDER_REVIEW"):
                        continue
                elif st_filter in ("UNDER REVIEW", "UNDER_REVIEW"):
                    if st != "UNDER_REVIEW":
                        continue
                elif st_filter in ("RETURNED", "RETURNED FOR CORRECTION"):
                    if st != "RETURNED":
                        continue
                elif st_filter == "APPROVED":
                    if st != "APPROVED":
                        continue
                elif st_filter in ("PUBLISHED", "RELEASED"):
                    if st != "RELEASED" and ex.status != "PUBLISHED":
                        continue
                elif st_filter == "OVERDUE" and not is_overdue:
                    continue
                elif st_filter == "INCOMPLETE" and (pending_count == 0 or st in ("RELEASED", "RETURNED")):
                    continue
                elif st_filter == "COMPLETE" and (pending_count > 0 or st == "RELEASED"):
                    continue

            comp_pct = round((completed_count / enrolled_count * 100) if enrolled_count > 0 else 0.0, 1)

            items.append({
                "id": sub.id if sub else ex.id,
                "teacher_id": teacher.id if teacher else (sub.teacher_id if sub else None),
                "teacher_name": teacher.full_name if teacher else "Unassigned Teacher",
                "teacher_number": teacher.teacher_number if teacher else None,
                "subject_id": ex.subject_id,
                "subject_name": subject.name if subject else "Subject",
                "subject_code": subject.code if subject else None,
                "class_id": ex.class_id,
                "class_name": s_class.name if s_class else "Class",
                "class_section": s_class.section if s_class else None,
                "exam_id": ex.id,
                "exam_name": ex.name,
                "exam_type": ex.exam_type,
                "exam_status": ex.status,
                "academic_year": ex.academic_year,
                "expected_students": enrolled_count,
                "completed_students": completed_count,
                "pending_students": pending_count,
                "absent_students": absent_in_sub,
                "present_students": present_in_sub,
                "complaints_count": complaints_in_sub,
                "completion_percentage": comp_pct,
                "status": st,
                "submitted_at": sub.submitted_at if sub else None,
                "reviewed_at": sub.reviewed_at if sub else None,
                "approved_at": sub.approved_at if sub else None,
                "returned_at": sub.returned_at if sub else None,
                "return_reason": sub.return_reason if sub else None,
                "submission_deadline": effective_deadline,
                "is_overdue": is_overdue,
                "deadline_status": deadline_status,
                "start_time": ex.start_time,
                "end_time": ex.end_time,
                "instructions": ex.instructions,
                "revisions": sub.revisions if sub else [],
            })

        return items

    def get_teacher_accountability(self, teacher_id: int, academic_year: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculate teacher accountability metrics from PostgreSQL.
        Tracks each assignment separately.
        """
        teacher = self.db.query(Teacher).filter(Teacher.id == teacher_id).first()
        if not teacher:
            return {}

        assign_q = self.db.query(TeacherAssignment).filter(
            TeacherAssignment.teacher_id == teacher_id,
            TeacherAssignment.status == "ACTIVE"
        )
        if academic_year:
            assign_q = assign_q.filter(TeacherAssignment.academic_year == academic_year)
        total_assigned = assign_q.count()

        sub_q = self.db.query(ResultSubmission).filter(
            ResultSubmission.teacher_id == teacher_id
        )
        if academic_year:
            sub_q = sub_q.filter(ResultSubmission.academic_year == academic_year)
        subs = sub_q.all()

        submitted = sum(1 for s in subs if s.status in ("SUBMITTED", "APPROVED", "RELEASED"))
        partial = sum(1 for s in subs if s.status == "PARTIAL")
        pending = max(0, total_assigned - submitted)
        approved = sum(1 for s in subs if s.status in ("APPROVED", "RELEASED"))
        returned = sum(1 for s in subs if s.status == "RETURNED")
        released = sum(1 for s in subs if s.status == "RELEASED")

        return {
            "teacher_id": teacher.id,
            "teacher_name": teacher.full_name,
            "teacher_number": teacher.teacher_number,
            "total_assigned": total_assigned,
            "submitted": submitted,
            "partial": partial,
            "pending": pending,
            "approved": approved,
            "returned": returned,
            "released": released,
        }

    def get_submission_detail(self, submission_id: int) -> Optional[Dict[str, Any]]:
        """Get complete submission detail for Admin review screen."""
        sub = self.db.query(ResultSubmission).filter(ResultSubmission.id == submission_id).first()
        if not sub:
            return None

        exam = sub.exam
        school_class = sub.school_class
        subject = sub.subject
        teacher = sub.teacher

        # Fetch enrolled students
        y = sub.academic_year
        y_variants = [y, y.replace("/", "-"), y.replace("-", "/")] if y else []
        enrollments = self.db.query(StudentEnrollment).filter(
            StudentEnrollment.class_id == sub.class_id,
            StudentEnrollment.academic_year.in_(y_variants),
            StudentEnrollment.status == "ACTIVE"
        ).all()
        if not enrollments:
            enrollments = self.db.query(StudentEnrollment).filter(
                StudentEnrollment.class_id == sub.class_id,
                StudentEnrollment.status == "ACTIVE"
            ).all()

        # Fetch results
        results = self.db.query(ExamResult).filter(ExamResult.exam_id == sub.exam_id).all()
        res_by_student = {r.student_id: r for r in results}

        students_list = []
        present_count = 0
        sat_exam_count = 0
        absent_count = 0
        missing_marks_count = 0
        recorded_absence_reasons_count = 0
        complaints_count = 0

        for en in enrollments:
            std = en.student
            if not std:
                continue
            res = res_by_student.get(std.id)
            att_status = res.attendance_status if res else "PRESENT"
            marks = res.marks_obtained if res else None
            absence_reason = (res.absence_reason if res and res.absence_reason else None)
            complaint_text = (res.complaint if res and res.complaint else None)

            if att_status in ("ABSENT", "EXCUSED"):
                absent_count += 1
                if absence_reason and absence_reason.strip():
                    recorded_absence_reasons_count += 1
            elif att_status == "PRESENT":
                present_count += 1
                if marks is not None:
                    sat_exam_count += 1
                else:
                    missing_marks_count += 1
            else:
                missing_marks_count += 1

            if complaint_text and complaint_text.strip():
                complaints_count += 1

            students_list.append({
                "student_id": std.id,
                "admission_number": std.admission_number,
                "student_name": std.full_name,
                "roll_number": en.roll_number,
                "gender": std.gender,
                "attendance_status": att_status,
                "absence_reason": absence_reason,
                "complaint": complaint_text,
                "marks_obtained": marks,
                "max_marks": exam.max_marks if exam else Decimal("100.00"),
                "pass_marks": exam.pass_marks if exam else Decimal("50.00"),
                "grade": res.grade if res else None,
                "remarks": res.remarks if res else None,
                "status": res.status if res else "DRAFT",
                "paper_file_path": res.paper_file_path if res else None,
                "paper_original_name": res.paper_original_name if res else None,
            })

        students_list.sort(key=lambda x: x["student_name"])

        total_expected = len(enrollments)
        completed_count = sat_exam_count + absent_count
        pending_count = max(0, total_expected - completed_count)
        is_complete = (missing_marks_count == 0 and total_expected > 0)

        return {
            "id": sub.id,
            "exam_id": sub.exam_id,
            "exam_name": sub.exam_name,
            "exam_type": sub.exam_type or (exam.exam_type if exam else None),
            "academic_year": sub.academic_year,
            "class_id": sub.class_id,
            "class_name": school_class.name if school_class else "Class",
            "class_section": school_class.section if school_class else None,
            "subject_id": sub.subject_id,
            "subject_name": subject.name if subject else "Subject",
            "teacher_id": sub.teacher_id,
            "teacher_name": teacher.full_name if teacher else "Teacher",
            "status": sub.status,
            "expected_students": total_expected,
            "completed_students": completed_count,
            "pending_students": pending_count,
            "absent_students": absent_count,
            "present_students": present_count,
            "sat_exam_students": sat_exam_count,
            "missing_marks_students": missing_marks_count,
            "recorded_absence_reasons_count": recorded_absence_reasons_count,
            "complaints_count": complaints_count,
            "pass_marks": exam.pass_marks if exam else Decimal("50.00"),
            "max_marks": exam.max_marks if exam else Decimal("100.00"),
            "is_complete": is_complete,
            "submitted_at": sub.submitted_at,
            "returned_at": sub.returned_at,
            "return_reason": sub.return_reason,
            "revisions": sub.revisions or [],
            "students": students_list,
        }

    def get_school_branding(self) -> Dict[str, Any]:
        """Fetch school branding details for reports and documents."""
        from app.models.institution import Institution
        from app.models.system_setting import SystemSetting
        import os

        settings = {s.key: s.value for s in self.db.query(SystemSetting).all()}
        institution = self.db.query(Institution).filter(Institution.status == "ACTIVE").first()

        name = settings.get("school_name") or (institution.name if institution else "Hawlwadaag Secondary School")
        motto = settings.get("school_motto", "Excellence in Education and Character")
        address = settings.get("school_address", "Hawlwadaag District, Mogadishu, Somalia")
        phone = settings.get("school_phone", "+252 61 0000000")
        email = settings.get("school_email", "info@ems.edu.so")

        logo_path = None
        possible_paths = [
            r"d:\desktop\SMS\frontend\public\somroyal-official-logo.png",
            r"d:\desktop\SMS\frontend\public\somroyal-logo-cropped.png",
            r"d:\desktop\SMS\frontend\public\somroyal-logo-transparent.png",
        ]
        for p in possible_paths:
            if os.path.exists(p):
                logo_path = p
                break

        return {
            "name": name,
            "motto": motto,
            "address": address,
            "phone": phone,
            "email": email,
            "logo_path": logo_path,
            "primary_color": "#0f172a",
            "secondary_color": "#ea580c",
        }

    def get_dashboard_statistics(
        self, academic_year: str, exam_name: str, division: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate the 10 real-time KPIs specified for the Results Management Dashboard.
        Strictly computes from live database records without any hardcoded values.
        """
        y = academic_year.strip()
        y_variants = [y, y.replace("/", "-"), y.replace("-", "/")]

        class_q = self.db.query(SchoolClass).filter(
            SchoolClass.status == "ACTIVE",
            SchoolClass.academic_year.in_(y_variants)
        )
        if division and division != "ALL":
            class_q = class_q.filter(SchoolClass.division == division)
        classes = class_q.all()
        class_ids = [c.id for c in classes]

        enrolled_classes_count = self.db.query(StudentEnrollment.class_id).filter(
            StudentEnrollment.class_id.in_(class_ids),
            StudentEnrollment.academic_year.in_(y_variants),
            StudentEnrollment.status == "ACTIVE"
        ).distinct().count()

        total_eligible_students = self.db.query(StudentEnrollment.student_id).filter(
            StudentEnrollment.class_id.in_(class_ids),
            StudentEnrollment.academic_year.in_(y_variants),
            StudentEnrollment.status == "ACTIVE"
        ).distinct().count()

        sub_filter = _build_submission_filter(exam_name)
        sub_q = self.db.query(ResultSubmission).filter(
            ResultSubmission.class_id.in_(class_ids),
            ResultSubmission.academic_year.in_(y_variants)
        )
        if sub_filter is not None:
            sub_q = sub_q.filter(sub_filter)
        all_submissions = sub_q.all()

        total_submitted_sheets = sum(
            1 for s in all_submissions
            if s.status in ("SUBMITTED", "UNDER_REVIEW", "APPROVED", "RELEASED")
        )

        completed_subjects = sum(
            1 for s in all_submissions
            if s.status in ("APPROVED", "RELEASED")
        )

        awaiting_admin_review = sum(
            1 for s in all_submissions
            if s.status in ("SUBMITTED", "UNDER_REVIEW")
        )

        approved_results = sum(
            1 for s in all_submissions
            if s.status == "APPROVED"
        )

        published_results = sum(
            1 for s in all_submissions
            if s.status == "RELEASED"
        )

        exam_filter = _build_exam_filter(exam_name)
        exam_q = self.db.query(Exam).filter(
            Exam.class_id.in_(class_ids),
            Exam.academic_year.in_(y_variants)
        )
        if exam_filter is not None:
            exam_q = exam_q.filter(exam_filter)
        exams = exam_q.all()
        exam_ids = [e.id for e in exams]

        total_expected_submissions = max(len(exams), len(all_submissions))
        pending_teacher_submissions = max(0, total_expected_submissions - total_submitted_sheets)

        results_q = self.db.query(ExamResult).filter(
            ExamResult.exam_id.in_(exam_ids)
        ) if exam_ids else []
        all_results = results_q.all() if exam_ids else []

        sat_student_ids = {
            r.student_id for r in all_results
            if r.attendance_status == "PRESENT" and r.marks_obtained is not None
        }
        students_sat_exam = len(sat_student_ids)

        absent_student_instances = sum(
            1 for r in all_results
            if r.attendance_status in ("ABSENT", "EXCUSED")
        )

        return {
            "academic_year": academic_year,
            "exam_name": exam_name,
            "division": division or "ALL",
            "total_classes_with_students": enrolled_classes_count,
            "total_eligible_students": total_eligible_students,
            "total_submitted_sheets": total_submitted_sheets,
            "completed_subjects": completed_subjects,
            "pending_teacher_submissions": pending_teacher_submissions,
            "students_sat_exam": students_sat_exam,
            "absent_students": absent_student_instances,
            "awaiting_admin_review": awaiting_admin_review,
            "approved_results": approved_results,
            "published_results": published_results,
        }

    def get_class_result_sheet(
        self, class_id: int, academic_year: str, exam_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Build the full class result sheet for an examination and class.
        Includes student scores across all subjects, totals, percentages,
        competition rankings (1, 2, 2, 4), grades, pass/fail status,
        and comprehensive class & subject performance summaries.
        """
        school_class = self.db.query(SchoolClass).filter(SchoolClass.id == class_id).first()
        if not school_class:
            return None

        y = academic_year.strip()
        y_variants = [y, y.replace("/", "-"), y.replace("-", "/")]

        enrollments = self.db.query(StudentEnrollment).filter(
            StudentEnrollment.class_id == class_id,
            StudentEnrollment.academic_year.in_(y_variants),
            StudentEnrollment.status == "ACTIVE"
        ).all()
        if not enrollments:
            enrollments = self.db.query(StudentEnrollment).filter(
                StudentEnrollment.class_id == class_id,
                StudentEnrollment.status == "ACTIVE"
            ).all()

        assignments = self.db.query(TeacherAssignment).filter(
            TeacherAssignment.class_id == class_id,
            TeacherAssignment.academic_year.in_(y_variants),
            TeacherAssignment.status == "ACTIVE"
        ).all()
        assigned_subj_ids = {a.subject_id for a in assignments if a.subject and a.subject.status == "ACTIVE"}
        tch_by_subj = {a.subject_id: a.teacher for a in assignments if a.teacher}

        exam_filter = _build_exam_filter(exam_name)
        exam_q = self.db.query(Exam).filter(
            Exam.class_id == class_id,
            Exam.academic_year.in_(y_variants)
        )
        if exam_filter is not None:
            exam_q = exam_q.filter(exam_filter)
        exams = exam_q.order_by(Exam.subject_id).all()
        exam_by_subj = {}
        for e in exams:
            prev_e = exam_by_subj.get(e.subject_id)
            if not prev_e:
                exam_by_subj[e.subject_id] = e
            else:
                has_res = self.db.query(ExamResult.id).filter(ExamResult.exam_id == e.id, ExamResult.marks_obtained.isnot(None)).first()
                prev_has_res = self.db.query(ExamResult.id).filter(ExamResult.exam_id == prev_e.id, ExamResult.marks_obtained.isnot(None)).first()
                if has_res and not prev_has_res:
                    exam_by_subj[e.subject_id] = e

        all_subj_ids = sorted(list(assigned_subj_ids.union(set(exam_by_subj.keys()))))
        all_subjects = self.db.query(Subject).filter(Subject.id.in_(all_subj_ids)).order_by(Subject.name).all() if all_subj_ids else []
        subj_obj_by_id = {s.id: s for s in all_subjects}

        exam_ids = [e.id for e in exams]
        results = self.db.query(ExamResult).filter(ExamResult.exam_id.in_(exam_ids)).all() if exam_ids else []
        res_lookup = {(r.exam_id, r.student_id): r for r in results}

        subjects_meta = []
        for s_id in all_subj_ids:
            s_obj = subj_obj_by_id.get(s_id)
            ex = exam_by_subj.get(s_id)
            tch = tch_by_subj.get(s_id) or (ex.teacher if ex else None)
            subjects_meta.append({
                "id": s_id,
                "name": s_obj.name if s_obj else f"Subject #{s_id}",
                "code": s_obj.code if s_obj else "",
                "teacher_id": tch.id if tch else None,
                "teacher_name": tch.full_name if tch else "Assigned Teacher",
                "max_marks": float(ex.max_marks) if ex else 100.0,
                "pass_marks": float(ex.pass_marks) if ex else 50.0,
            })

        students_list = []
        for en in enrollments:
            std = en.student
            if not std:
                continue

            scores = {}
            tot_obtained = 0.0
            tot_max = 0.0
            completed_count = 0
            absent_count = 0
            has_failed_subject = False
            has_any_score = False

            for s_id in all_subj_ids:
                ex = exam_by_subj.get(s_id)
                s_obj = subj_obj_by_id.get(s_id)
                res = res_lookup.get((ex.id, std.id)) if ex else None

                att_status = res.attendance_status if res else "PRESENT"
                marks = float(res.marks_obtained) if res and res.marks_obtained is not None else None
                grade = res.grade if res else None
                remarks = res.remarks if res else None
                absence_reason = res.absence_reason if res else None
                complaint = res.complaint if res else None
                max_m = float(ex.max_marks) if ex else 100.0
                pass_m = float(ex.pass_marks) if ex else 50.0

                if att_status in ("ABSENT", "EXCUSED"):
                    absent_count += 1
                    has_failed_subject = True
                    is_absent = True
                else:
                    is_absent = False
                    if marks is not None:
                        completed_count += 1
                        tot_obtained += marks
                        tot_max += max_m
                        has_any_score = True
                        if marks < pass_m:
                            has_failed_subject = True

                scores[str(s_id)] = {
                    "subject_id": s_id,
                    "subject_name": s_obj.name if s_obj else f"Subject #{s_id}",
                    "subject_code": s_obj.code if s_obj else "",
                    "marks_obtained": marks,
                    "max_marks": max_m,
                    "pass_marks": pass_m,
                    "grade": grade,
                    "attendance_status": att_status,
                    "absence_reason": absence_reason,
                    "complaint": complaint,
                    "is_absent": is_absent,
                    "remarks": remarks,
                    "status": res.status if res else "DRAFT",
                }

            pct = round((tot_obtained / tot_max) * 100, 1) if tot_max > 0 else 0.0
            overall_grade = _compute_grade_str(tot_obtained, tot_max) if has_any_score else None
            if has_any_score:
                pass_status = "PASS" if (pct >= 50.0 and not has_failed_subject) else ("PASS" if pct >= 50.0 else "FAIL")
            elif absent_count > 0:
                pass_status = "ABSENT"
            else:
                pass_status = "PENDING"

            students_list.append({
                "student_id": std.id,
                "admission_number": std.admission_number,
                "student_name": std.full_name,
                "gender": std.gender,
                "roll_number": en.roll_number,
                "subject_marks": scores,
                "total_obtained": round(tot_obtained, 1) if has_any_score else None,
                "total_max": round(tot_max, 1) if tot_max > 0 else (len(all_subj_ids) * 100.0),
                "percentage": pct if has_any_score else None,
                "grade": overall_grade,
                "pass_status": pass_status,
                "completed_subjects": completed_count,
                "absent_subjects": absent_count,
                "is_absent_all": (absent_count == len(all_subj_ids) and len(all_subj_ids) > 0),
                "remarks": ("Excellent" if pct >= 80 else ("Good" if pct >= 60 else ("Needs Improvement" if pct >= 50 else "Poor"))) if has_any_score else "—",
            })

        # Calculate Competition Rankings (1, 2, 2, 4)
        students_list.sort(
            key=lambda x: (x["total_obtained"] is not None, x["total_obtained"] or 0.0),
            reverse=True
        )
        for i, s in enumerate(students_list):
            if s["total_obtained"] is None:
                s["rank"] = len(students_list)
            elif i == 0:
                s["rank"] = 1
            else:
                prev = students_list[i - 1]
                if s["total_obtained"] == prev["total_obtained"]:
                    s["rank"] = prev["rank"]
                else:
                    s["rank"] = i + 1

        total_registered = len(students_list)
        sat_exam = sum(1 for s in students_list if s["completed_subjects"] > 0)
        absent_all = sum(1 for s in students_list if s["is_absent_all"])
        passed = sum(1 for s in students_list if s["pass_status"] == "PASS")
        failed = total_registered - passed
        pass_pct = round((passed / total_registered) * 100, 1) if total_registered > 0 else 0.0

        scored_pcts = [s["percentage"] for s in students_list if s["percentage"] is not None]
        avg_pct = round(sum(scored_pcts) / len(scored_pcts), 1) if scored_pcts else 0.0

        totals = [s["total_obtained"] for s in students_list if s["total_obtained"] is not None]
        highest_total = max(totals) if totals else 0.0
        lowest_total = min(totals) if totals else 0.0

        subj_stats = []
        for s_meta in subjects_meta:
            s_id_str = str(s_meta["id"])
            subj_scores = []
            s_sat = 0
            s_absent = 0
            s_missing = 0
            s_pass = 0
            s_fail = 0
            dist = {"A+": 0, "A": 0, "B": 0, "C": 0, "D": 0, "F": 0, "ABSENT": 0}

            for std in students_list:
                s_res = std["subject_marks"].get(s_id_str)
                if not s_res:
                    s_missing += 1
                elif s_res.get("is_absent"):
                    s_absent += 1
                    dist["ABSENT"] += 1
                elif s_res.get("marks_obtained") is not None:
                    m = s_res["marks_obtained"]
                    subj_scores.append(m)
                    s_sat += 1
                    if m >= s_meta["pass_marks"]:
                        s_pass += 1
                    else:
                        s_fail += 1
                    g = s_res.get("grade") or _compute_grade_str(m, s_meta["max_marks"])
                    if g in dist:
                        dist[g] += 1
                else:
                    s_missing += 1

            s_avg = round(sum(subj_scores) / len(subj_scores), 1) if subj_scores else 0.0
            s_high = max(subj_scores) if subj_scores else 0.0
            s_low = min(subj_scores) if subj_scores else 0.0
            s_pass_rate = round((s_pass / s_sat) * 100, 1) if s_sat > 0 else 0.0

            subj_stats.append({
                "subject_id": s_meta["id"],
                "subject_name": s_meta["name"],
                "subject_code": s_meta["code"],
                "teacher_name": s_meta["teacher_name"],
                "registered": total_registered,
                "sat": s_sat,
                "absent": s_absent,
                "missing": s_missing,
                "average_marks": s_avg,
                "highest_marks": s_high,
                "lowest_marks": s_low,
                "pass_count": s_pass,
                "fail_count": s_fail,
                "pass_rate": s_pass_rate,
                "grade_distribution": dist,
            })

        branding = self.get_school_branding()
        first_exam = exams[0] if exams else None

        return {
            "school": branding,
            "class_info": {
                "id": school_class.id,
                "name": school_class.name,
                "code": school_class.code,
                "division": school_class.division,
                "level": school_class.level,
                "section": school_class.section,
                "academic_year": academic_year,
            },
            "exam_info": {
                "name": exam_name,
                "exam_type": first_exam.exam_type if first_exam else None,
                "academic_year": academic_year,
                "start_date": str(first_exam.start_date) if first_exam and first_exam.start_date else None,
                "end_date": str(first_exam.end_date) if first_exam and first_exam.end_date else None,
            },
            "subjects": subjects_meta,
            "students": students_list,
            "class_summary": {
                "registered_students": total_registered,
                "sat_exam_students": sat_exam,
                "absent_students": absent_all,
                "passed_students": passed,
                "failed_students": failed,
                "pass_percentage": pass_pct,
                "class_average_percentage": avg_pct,
                "highest_total": highest_total,
                "lowest_total": lowest_total,
                "subject_performance": subj_stats,
            }
        }

    def get_class_rankings(
        self,
        class_id: Optional[int],
        academic_year: str,
        exam_name: str,
        division: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Build class ranking and merit list with competition ranking (1, 2, 2, 4)
        for a specific class or school-wide by academic year and exam.
        """
        y = academic_year.strip()
        y_variants = [y, y.replace("/", "-"), y.replace("-", "/")]

        class_q = self.db.query(SchoolClass).filter(
            SchoolClass.status == "ACTIVE",
            SchoolClass.academic_year.in_(y_variants)
        )
        if class_id:
            class_q = class_q.filter(SchoolClass.id == class_id)
        if division and division != "ALL":
            class_q = class_q.filter(SchoolClass.division == division)
        target_classes = class_q.all()
        target_class_ids = [c.id for c in target_classes]

        enrollments = self.db.query(StudentEnrollment).filter(
            StudentEnrollment.class_id.in_(target_class_ids),
            StudentEnrollment.academic_year.in_(y_variants),
            StudentEnrollment.status == "ACTIVE"
        ).all()
        if not enrollments:
            enrollments = self.db.query(StudentEnrollment).filter(
                StudentEnrollment.class_id.in_(target_class_ids),
                StudentEnrollment.status == "ACTIVE"
            ).all()

        cls_by_id = {c.id: c for c in target_classes}

        exam_filter = _build_exam_filter(exam_name)
        exam_q = self.db.query(Exam).filter(
            Exam.class_id.in_(target_class_ids),
            Exam.academic_year.in_(y_variants)
        )
        if exam_filter is not None:
            exam_q = exam_q.filter(exam_filter)
        exams = exam_q.all()
        exam_ids = [e.id for e in exams]

        results = self.db.query(ExamResult).filter(ExamResult.exam_id.in_(exam_ids)).all() if exam_ids else []
        res_by_student = {}
        for r in results:
            res_by_student.setdefault(r.student_id, []).append(r)

        ranked_list = []
        for en in enrollments:
            std = en.student
            if not std:
                continue

            c = cls_by_id.get(en.class_id)
            std_results = res_by_student.get(std.id, [])

            tot_obtained = 0.0
            tot_max = 0.0
            completed_subjects = 0
            absent_subjects = 0
            has_scores = False

            for r in std_results:
                if r.attendance_status in ("ABSENT", "EXCUSED"):
                    absent_subjects += 1
                elif r.marks_obtained is not None:
                    marks = float(r.marks_obtained)
                    tot_obtained += marks
                    tot_max += float(r.exam.max_marks) if r.exam else 100.0
                    completed_subjects += 1
                    has_scores = True

            pct = round((tot_obtained / tot_max) * 100, 1) if tot_max > 0 else 0.0
            grade = _compute_grade_str(tot_obtained, tot_max) if has_scores else None
            if has_scores:
                pass_fail = "PASS" if pct >= 50.0 else "FAIL"
            elif absent_subjects > 0:
                pass_fail = "ABSENT"
            else:
                pass_fail = "PENDING"

            ranked_list.append({
                "student_id": std.id,
                "admission_number": std.admission_number,
                "student_name": std.full_name,
                "gender": std.gender,
                "roll_number": en.roll_number,
                "class_id": en.class_id,
                "class_name": c.name if c else "Class",
                "division": c.division if c else "",
                "completed_subjects": completed_subjects,
                "absent_subjects": absent_subjects,
                "total_marks": round(tot_obtained, 1) if has_scores else None,
                "max_possible_marks": round(tot_max, 1) if tot_max > 0 else None,
                "percentage": pct if has_scores else None,
                "grade": grade,
                "pass_fail": pass_fail,
                "is_complete": (completed_subjects > 0 and absent_subjects == 0),
            })

        ranked_list.sort(
            key=lambda x: (x["total_marks"] is not None, x["total_marks"] or 0.0),
            reverse=True
        )
        for i, s in enumerate(ranked_list):
            if s["total_marks"] is None:
                s["position"] = None
            elif i == 0:
                s["position"] = 1
            else:
                prev = ranked_list[i - 1]
                if prev["total_marks"] is not None and s["total_marks"] == prev["total_marks"]:
                    s["position"] = prev["position"]
                else:
                    s["position"] = i + 1

        selected_class = target_classes[0] if (class_id and target_classes) else None
        first_exam = exams[0] if exams else None

        return {
            "school": self.get_school_branding(),
            "class_info": {
                "id": selected_class.id if selected_class else None,
                "name": selected_class.name if selected_class else "School-Wide",
                "division": selected_class.division if selected_class else (division or "ALL"),
                "academic_year": academic_year,
            },
            "exam_info": {
                "name": exam_name,
                "exam_type": first_exam.exam_type if first_exam else None,
                "academic_year": academic_year,
            },
            "rankings": ranked_list,
        }

    def get_student_result_report(
        self,
        student_id: int,
        academic_year: str,
        exam_name: Optional[str] = None,
        only_published: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Generate individual student result transcript/report card for an exam or academic year.
        Respects publication status if only_published=True (for student/guardian portal).
        """
        std = self.db.query(Student).filter(Student.id == student_id).first()
        if not std:
            return None

        y = academic_year.strip()
        y_variants = [y, y.replace("/", "-"), y.replace("-", "/")]

        enrollment = self.db.query(StudentEnrollment).filter(
            StudentEnrollment.student_id == student_id,
            StudentEnrollment.academic_year.in_(y_variants),
            StudentEnrollment.status == "ACTIVE"
        ).first()
        if not enrollment:
            enrollment = self.db.query(StudentEnrollment).filter(
                StudentEnrollment.student_id == student_id,
                StudentEnrollment.status == "ACTIVE"
            ).first()

        school_class = enrollment.school_class if enrollment else None

        res_q = self.db.query(ExamResult).join(Exam).filter(
            ExamResult.student_id == student_id,
            Exam.academic_year.in_(y_variants)
        )
        if exam_name and exam_name != "ALL":
            exam_filter = _build_exam_filter(exam_name)
            if exam_filter is not None:
                res_q = res_q.filter(exam_filter)
        if only_published:
            res_q = res_q.filter(ExamResult.status == "RELEASED")

        results = res_q.all()

        subjects_list = []
        tot_obtained = 0.0
        tot_max = 0.0
        has_scores = False
        absent_count = 0

        for r in results:
            ex = r.exam
            subj = ex.subject if ex else None
            tch = ex.teacher if ex else None

            max_m = float(ex.max_marks) if ex else 100.0
            pass_m = float(ex.pass_marks) if ex else 50.0

            if r.attendance_status in ("ABSENT", "EXCUSED"):
                marks = None
                absent_count += 1
                pct = 0.0
                pass_status = "FAIL"
            elif r.marks_obtained is not None:
                marks = float(r.marks_obtained)
                tot_obtained += marks
                tot_max += max_m
                has_scores = True
                pct = round((marks / max_m) * 100, 1) if max_m > 0 else 0.0
                pass_status = "PASS" if marks >= pass_m else "FAIL"
            else:
                marks = None
                pct = 0.0
                pass_status = "FAIL"

            grade = r.grade or (_compute_grade_str(marks, max_m) if marks is not None else "ABSENT")

            subjects_list.append({
                "subject_id": subj.id if subj else None,
                "subject_name": subj.name if subj else "Subject",
                "subject_code": subj.code if subj else "",
                "teacher_name": tch.full_name if tch else "Assigned Teacher",
                "marks_obtained": marks,
                "max_marks": max_m,
                "pass_marks": pass_m,
                "percentage": pct if marks is not None else None,
                "grade": grade,
                "attendance_status": r.attendance_status,
                "absence_reason": r.absence_reason,
                "pass_status": pass_status,
                "remarks": r.remarks or ("Good" if pct >= 60 else "Keep working hard"),
                "status": r.status,
            })

        overall_pct = round((tot_obtained / tot_max) * 100, 1) if tot_max > 0 else 0.0
        overall_grade = _compute_grade_str(tot_obtained, tot_max) if has_scores else None
        if has_scores:
            overall_pass = "PASS" if overall_pct >= 50.0 else "FAIL"
        elif any(r.get("attendance_status") in ("ABSENT", "EXCUSED") for r in subjects_results):
            overall_pass = "ABSENT"
        else:
            overall_pass = "PENDING"

        rank_in_class = "-"
        class_size = 0
        if school_class and exam_name:
            rankings = self.get_class_rankings(school_class.id, academic_year, exam_name)
            for r in rankings.get("rankings", []):
                if r["student_id"] == student_id:
                    rank_in_class = r.get("position", "-")
                    break
            class_size = len(rankings.get("rankings", []))

        return {
            "school": self.get_school_branding(),
            "student": {
                "id": std.id,
                "student_name": std.full_name,
                "admission_number": std.admission_number,
                "gender": std.gender,
                "roll_number": enrollment.roll_number if enrollment else None,
            },
            "class_info": {
                "id": school_class.id if school_class else None,
                "name": school_class.name if school_class else "Unassigned",
                "division": school_class.division if school_class else "",
                "academic_year": academic_year,
            },
            "exam_info": {
                "name": exam_name or "Official Examination",
                "academic_year": academic_year,
            },
            "subjects": subjects_list,
            "overall": {
                "total_obtained": round(tot_obtained, 1) if has_scores else 0.0,
                "total_max": round(tot_max, 1) if tot_max > 0 else 0.0,
                "overall_percentage": overall_pct,
                "overall_grade": overall_grade,
                "pass_status": overall_pass,
                "rank_in_class": rank_in_class,
                "class_size": class_size,
                "absent_subjects_count": absent_count,
                "teacher_remarks": "Demonstrated commendable dedication. Keep up the high standard." if overall_pct >= 75 else "Consistent effort noted. Encouraged to focus on areas needing improvement.",
            }
        }

    def get_subject_performance_list(
        self,
        academic_year: str,
        exam_name: str,
        class_id: Optional[int] = None,
        subject_id: Optional[int] = None,
        division: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve performance metrics for each subject separately across classes.
        Shows registered, sat, absent, missing, average, highest/lowest,
        pass/fail counts, and grade distributions.
        """
        y = academic_year.strip()
        y_variants = [y, y.replace("/", "-"), y.replace("-", "/")]

        class_q = self.db.query(SchoolClass).filter(
            SchoolClass.status == "ACTIVE",
            SchoolClass.academic_year.in_(y_variants)
        )
        if class_id:
            class_q = class_q.filter(SchoolClass.id == class_id)
        if division and division != "ALL":
            class_q = class_q.filter(SchoolClass.division == division)
        target_classes = class_q.all()
        target_class_ids = [c.id for c in target_classes]
        cls_by_id = {c.id: c for c in target_classes}

        exam_filter = _build_exam_filter(exam_name)
        exam_q = self.db.query(Exam).filter(
            Exam.class_id.in_(target_class_ids),
            Exam.academic_year.in_(y_variants)
        )
        if exam_filter is not None:
            exam_q = exam_q.filter(exam_filter)
        if subject_id:
            exam_q = exam_q.filter(Exam.subject_id == subject_id)
        exams = exam_q.all()

        sub_filter = _build_submission_filter(exam_name)
        sub_q = self.db.query(ResultSubmission).filter(
            ResultSubmission.class_id.in_(target_class_ids),
            ResultSubmission.academic_year.in_(y_variants)
        )
        if sub_filter is not None:
            sub_q = sub_q.filter(sub_filter)
        if subject_id:
            sub_q = sub_q.filter(ResultSubmission.subject_id == subject_id)
        submissions = sub_q.all()
        sub_map = {(s.class_id, s.subject_id): s for s in submissions}

        enrollments = self.db.query(StudentEnrollment).filter(
            StudentEnrollment.class_id.in_(target_class_ids),
            StudentEnrollment.academic_year.in_(y_variants),
            StudentEnrollment.status == "ACTIVE"
        ).all()
        enrolled_by_class = {}
        for en in enrollments:
            enrolled_by_class.setdefault(en.class_id, []).append(en)

        exam_ids = [e.id for e in exams]
        results = self.db.query(ExamResult).filter(ExamResult.exam_id.in_(exam_ids)).all() if exam_ids else []
        res_by_exam = {}
        for r in results:
            res_by_exam.setdefault(r.exam_id, []).append(r)

        performance_items = []
        for ex in exams:
            c = cls_by_id.get(ex.class_id)
            subj = ex.subject
            sub = sub_map.get((ex.class_id, ex.subject_id))
            tch = (sub.teacher if sub and sub.teacher else None) or ex.teacher
            c_enrollments = enrolled_by_class.get(ex.class_id, [])
            total_reg = len(c_enrollments)

            ex_results = res_by_exam.get(ex.id, [])
            scores = []
            absent_count = 0
            pass_count = 0
            fail_count = 0
            dist = {"A+": 0, "A": 0, "B": 0, "C": 0, "D": 0, "F": 0, "ABSENT": 0}

            for r in ex_results:
                if r.attendance_status in ("ABSENT", "EXCUSED"):
                    absent_count += 1
                    dist["ABSENT"] += 1
                elif r.marks_obtained is not None:
                    m = float(r.marks_obtained)
                    scores.append(m)
                    if m >= float(ex.pass_marks):
                        pass_count += 1
                    else:
                        fail_count += 1
                    g = r.grade or _compute_grade_str(m, float(ex.max_marks))
                    if g in dist:
                        dist[g] += 1

            sat_count = len(scores)
            missing_count = max(0, total_reg - (sat_count + absent_count))
            avg_m = round(sum(scores) / sat_count, 1) if sat_count > 0 else 0.0
            high_m = max(scores) if scores else 0.0
            low_m = min(scores) if scores else 0.0
            pass_rate = round((pass_count / sat_count) * 100, 1) if sat_count > 0 else 0.0

            sub_status = sub.status if sub else ("RELEASED" if ex.status == "PUBLISHED" else "PENDING")

            performance_items.append({
                "exam_id": ex.id,
                "class_id": ex.class_id,
                "class_name": c.name if c else "Class",
                "division": c.division if c else "",
                "subject_id": ex.subject_id,
                "subject_name": subj.name if subj else "Subject",
                "subject_code": subj.code if subj else "",
                "teacher_id": tch.id if tch else None,
                "teacher_name": tch.full_name if tch else "Unassigned",
                "max_marks": float(ex.max_marks),
                "pass_marks": float(ex.pass_marks),
                "total_registered": total_reg,
                "sat_exam": sat_count,
                "absent_count": absent_count,
                "missing_marks_count": missing_count,
                "highest_marks": high_m,
                "lowest_marks": low_m,
                "average_marks": avg_m,
                "pass_count": pass_count,
                "fail_count": fail_count,
                "pass_rate": pass_rate,
                "grade_distribution": dist,
                "submission_status": sub_status,
            })

        performance_items.sort(key=lambda x: (x["class_name"], x["subject_name"]))
        return performance_items

    def get_absent_students_list(
        self,
        academic_year: str,
        exam_name: str,
        class_id: Optional[int] = None,
        subject_id: Optional[int] = None,
        division: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve list of students marked ABSENT or EXCUSED with documented reasons and complaints.
        """
        y = academic_year.strip()
        y_variants = [y, y.replace("/", "-"), y.replace("-", "/")]

        class_q = self.db.query(SchoolClass).filter(
            SchoolClass.status == "ACTIVE",
            SchoolClass.academic_year.in_(y_variants)
        )
        if class_id:
            class_q = class_q.filter(SchoolClass.id == class_id)
        if division and division != "ALL":
            class_q = class_q.filter(SchoolClass.division == division)
        target_classes = class_q.all()
        target_class_ids = [c.id for c in target_classes]
        cls_by_id = {c.id: c for c in target_classes}

        exam_filter = _build_exam_filter(exam_name)
        exam_q = self.db.query(Exam).filter(
            Exam.class_id.in_(target_class_ids),
            Exam.academic_year.in_(y_variants)
        )
        if exam_filter is not None:
            exam_q = exam_q.filter(exam_filter)
        if subject_id:
            exam_q = exam_q.filter(Exam.subject_id == subject_id)
        exams = exam_q.all()
        exam_ids = [e.id for e in exams]
        exam_by_id = {e.id: e for e in exams}

        results = self.db.query(ExamResult).filter(
            ExamResult.exam_id.in_(exam_ids),
            ExamResult.attendance_status.in_(("ABSENT", "EXCUSED"))
        ).all() if exam_ids else []

        absent_records = []
        for r in results:
            std = r.student
            ex = exam_by_id.get(r.exam_id)
            c = cls_by_id.get(ex.class_id) if ex else None
            subj = ex.subject if ex else None
            tch = ex.teacher if ex else None

            absent_records.append({
                "result_id": r.id,
                "student_id": std.id if std else r.student_id,
                "admission_number": std.admission_number if std else "-",
                "student_name": std.full_name if std else "Student",
                "gender": std.gender if std else "-",
                "class_id": c.id if c else None,
                "class_name": c.name if c else "Class",
                "division": c.division if c else "",
                "section": c.section if c else "",
                "subject_id": subj.id if subj else None,
                "subject_name": subj.name if subj else "Subject",
                "subject_code": subj.code if subj else "",
                "exam_id": ex.id if ex else None,
                "exam_name": ex.name if ex else exam_name,
                "attendance_status": r.attendance_status,
                "absence_reason": r.absence_reason or "No specific reason recorded by teacher",
                "complaint": r.complaint,
                "teacher_name": tch.full_name if tch else "Assigned Teacher",
            })

        absent_records.sort(key=lambda x: (x["class_name"], x["student_name"]))
        return absent_records

