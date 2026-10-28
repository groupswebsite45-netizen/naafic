from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from app.models.exam import Exam, ExamResult
from app.models.result_submission import ResultSubmission
from app.models.result_release import ResultReleaseBatch
from app.models.student_result_view import StudentResultView
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.models.school_class import SchoolClass


def _build_exam_filter(exam_name: Optional[str]):
    if not exam_name or exam_name == "ALL":
        return None
    e_upper = exam_name.upper().strip()
    clauses = [Exam.name == exam_name]
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
    if not exam_name or exam_name == "ALL":
        return None
    e_upper = exam_name.upper().strip()
    clauses = [ResultSubmission.exam_name == exam_name]
    if "MID" in e_upper:
        clauses.extend([ResultSubmission.exam_name.ilike("%Mid%")])
    elif "FINAL" in e_upper:
        clauses.extend([ResultSubmission.exam_name.ilike("%Final%")])
    elif "MONTH" in e_upper:
        clauses.extend([ResultSubmission.exam_name.ilike("%Month%")])
    elif "QUIZ" in e_upper:
        clauses.extend([ResultSubmission.exam_name.ilike("%Quiz%")])
    return or_(*clauses)


class ReleaseRepository:
    """Repository handling examination result publication, batch tracking, and student receipt verification."""

    def __init__(self, db: Session):
        self.db = db

    def generate_batch_code(self, academic_year: str) -> str:
        """Generate formatted release batch code, e.g. RB-2026-0001, guaranteed unique."""
        prefix_year = academic_year.split("-")[0] if "-" in academic_year else academic_year
        prefix = f"RB-{prefix_year}-"
        batches = self.db.query(ResultReleaseBatch.batch_code).filter(
            ResultReleaseBatch.batch_code.like(f"{prefix}%")
        ).all()
        existing_nums = set()
        for (code,) in batches:
            if code and code.startswith(prefix):
                suffix = code[len(prefix):]
                if suffix.isdigit():
                    existing_nums.add(int(suffix))

        next_num = 1
        while next_num in existing_nums:
            next_num += 1

        return f"{prefix}{next_num:04d}"

    def release_class_results(
        self,
        class_id: int,
        academic_year: str,
        exam_name: str,
        release_type: str,
        released_by_id: int,
        notes: Optional[str] = None
    ) -> Tuple[bool, str, Optional[ResultReleaseBatch]]:
        """
        Execute class result release in a transaction.
        Enforces that all assigned curriculum subjects for this class in this academic year
        are submitted and completed before release.
        """
        school_class = self.db.query(SchoolClass).filter(SchoolClass.id == class_id).first()
        if not school_class:
            return False, f"Class ID {class_id} does not exist in PostgreSQL.", None

        # Fetch enrolled students
        enrollments = self.db.query(StudentEnrollment).filter(
            StudentEnrollment.class_id == class_id,
            StudentEnrollment.academic_year == academic_year,
            StudentEnrollment.status == "ACTIVE"
        ).all()
        students_count = len(enrollments)

        # Fetch active assigned subjects for this class in this academic year
        from app.models.teacher_assignment import TeacherAssignment
        assignments = self.db.query(TeacherAssignment).filter(
            TeacherAssignment.class_id == class_id,
            TeacherAssignment.academic_year.in_([academic_year, academic_year.replace("/", "-"), academic_year.replace("-", "/")]),
            TeacherAssignment.status == "ACTIVE"
        ).all()
        required_assignments = [a for a in assignments if a.subject and a.subject.status == "ACTIVE"]
        required_subject_ids = list(set(a.subject_id for a in required_assignments))

        if not required_subject_ids:
            return False, f"No active curriculum subjects assigned for {school_class.name}.", None

        # Fetch class exams for this exam series
        exam_filter = _build_exam_filter(exam_name)
        sub_filter = _build_submission_filter(exam_name)

        exam_q = self.db.query(Exam).filter(
            Exam.class_id == class_id,
            Exam.academic_year.in_([academic_year, academic_year.replace("/", "-"), academic_year.replace("-", "/")])
        )
        if exam_filter is not None:
            exam_q = exam_q.filter(exam_filter)
        class_exams = exam_q.all()
        exam_by_subj = {e.subject_id: e for e in class_exams}

        # Check completeness per required subject
        sub_q = self.db.query(ResultSubmission).filter(
            ResultSubmission.class_id == class_id,
            ResultSubmission.academic_year.in_([academic_year, academic_year.replace("/", "-"), academic_year.replace("-", "/")])
        )
        if sub_filter is not None:
            sub_q = sub_q.filter(sub_filter)
        submissions = sub_q.all()
        sub_by_subj = {s.subject_id: s for s in submissions}

        pending_subject_names = []
        for a in required_assignments:
            s_id = a.subject_id
            s_name = a.subject.name if a.subject else f"Subject {s_id}"
            ex = exam_by_subj.get(s_id)
            sub = sub_by_subj.get(s_id)

            if not ex or not sub or sub.status not in ("SUBMITTED", "APPROVED", "RELEASED"):
                if s_name not in pending_subject_names:
                    pending_subject_names.append(s_name)

        if pending_subject_names:
            return (
                False,
                f"Cannot release {school_class.name}. {len(pending_subject_names)} subject(s) are still pending: {', '.join(pending_subject_names)}.",
                None
            )

        expected_results = students_count * len(required_subject_ids)
        exam_ids = [e.id for e in class_exams if e.subject_id in required_subject_ids]

        # Query existing results
        results = self.db.query(ExamResult).filter(
            ExamResult.exam_id.in_(exam_ids)
        ).all()

        completed_results = [
            r for r in results
            if r.attendance_status in ("ABSENT", "EXCUSED") or (r.attendance_status == "PRESENT" and r.marks_obtained is not None)
        ]
        pending_count = max(0, expected_results - len(completed_results))

        if pending_count > 0:
            return (
                False,
                f"Class results cannot be released yet. {pending_count} student result(s) across subjects are still pending.",
                None
            )

        if not completed_results:
            return False, "No completed results available to release for this class.", None

        # Generate batch code
        batch_code = self.generate_batch_code(academic_year)
        now = datetime.now(timezone.utc)

        batch = ResultReleaseBatch(
            batch_code=batch_code,
            exam_name=exam_name,
            academic_year=academic_year,
            class_id=class_id,
            release_type=release_type,
            status="RELEASED",
            released_by_id=released_by_id,
            released_at=now,
            results_count=len(completed_results),
            notes=notes
        )
        self.db.add(batch)
        self.db.flush()

        # Update completed results to RELEASED
        for r in completed_results:
            r.status = "RELEASED"
            r.release_batch_id = batch.id

        # Update submissions to RELEASED
        sub_update_q = self.db.query(ResultSubmission).filter(
            ResultSubmission.class_id == class_id,
            ResultSubmission.academic_year.in_([academic_year, academic_year.replace("/", "-"), academic_year.replace("-", "/")])
        )
        if sub_filter is not None:
            sub_update_q = sub_update_q.filter(sub_filter)
        submissions = sub_update_q.all()

        for s in submissions:
            s.status = "RELEASED"

        # Update Exam objects status to PUBLISHED if all subjects released
        for ex in class_exams:
            ex.status = "PUBLISHED"

        self.db.flush()
        return True, f"Successfully published {len(completed_results)} results for {school_class.name}.", batch

    def get_class_receipt_status(
        self,
        class_id: int,
        academic_year: str,
        exam_name: str
    ) -> Dict[str, Any]:
        """
        Verify whether students have actually received and viewed their released results.
        Tracks: Released vs Viewed vs Not Viewed.
        """
        school_class = self.db.query(SchoolClass).filter(SchoolClass.id == class_id).first()
        class_name = school_class.name if school_class else "Class"

        enrollments = self.db.query(StudentEnrollment).filter(
            StudentEnrollment.class_id == class_id,
            StudentEnrollment.academic_year == academic_year,
            StudentEnrollment.status == "ACTIVE"
        ).all()

        # Check if class results are released
        batch = self.db.query(ResultReleaseBatch).filter(
            ResultReleaseBatch.class_id == class_id,
            ResultReleaseBatch.academic_year == academic_year,
            ResultReleaseBatch.exam_name == exam_name,
            ResultReleaseBatch.status == "RELEASED"
        ).order_by(ResultReleaseBatch.id.desc()).first()

        # Fetch student result views
        views = self.db.query(StudentResultView).filter(
            StudentResultView.class_id == class_id,
            StudentResultView.academic_year == academic_year,
            StudentResultView.exam_name == exam_name
        ).all()
        views_by_student = {v.student_id: v for v in views}

        receipts = []
        released_count = 0
        viewed_count = 0

        for en in enrollments:
            std = en.student
            if not std:
                continue

            view = views_by_student.get(std.id)
            if not batch:
                st = "NOT_RELEASED"
            elif view:
                st = "VIEWED"
                viewed_count += 1
                released_count += 1
            else:
                st = "RELEASED"
                released_count += 1

            receipts.append({
                "student_id": std.id,
                "admission_number": std.admission_number,
                "student_name": std.full_name,
                "class_name": class_name,
                "status": st,
                "release_batch_code": batch.batch_code if batch else None,
                "released_at": batch.released_at if batch else None,
                "first_viewed_at": view.first_viewed_at if view else None,
                "last_viewed_at": view.last_viewed_at if view else None,
                "view_count": view.view_count if view else 0,
            })

        receipts.sort(key=lambda x: (x["status"] != "VIEWED", x["student_name"]))

        return {
            "class_id": class_id,
            "class_name": class_name,
            "exam_name": exam_name,
            "academic_year": academic_year,
            "total_students": len(receipts),
            "released_students": released_count,
            "viewed_students": viewed_count,
            "not_viewed_students": max(0, released_count - viewed_count),
            "receipts": receipts,
        }

    def record_student_view(
        self,
        student_id: int,
        exam_name: str,
        academic_year: str,
        class_id: int
    ) -> StudentResultView:
        """
        Record a view event when student views published results.
        Upserts single record per student/exam/class to avoid excessive duplicates.
        """
        now = datetime.now(timezone.utc)
        view = self.db.query(StudentResultView).filter(
            StudentResultView.student_id == student_id,
            StudentResultView.exam_name == exam_name,
            StudentResultView.class_id == class_id,
            StudentResultView.academic_year == academic_year
        ).first()

        if view:
            view.last_viewed_at = now
            view.view_count += 1
        else:
            # Find matching batch
            batch = self.db.query(ResultReleaseBatch).filter(
                ResultReleaseBatch.class_id == class_id,
                ResultReleaseBatch.academic_year == academic_year,
                ResultReleaseBatch.exam_name == exam_name,
                ResultReleaseBatch.status == "RELEASED"
            ).order_by(ResultReleaseBatch.id.desc()).first()

            view = StudentResultView(
                student_id=student_id,
                exam_name=exam_name,
                class_id=class_id,
                academic_year=academic_year,
                release_batch_id=batch.id if batch else None,
                first_viewed_at=now,
                last_viewed_at=now,
                view_count=1
            )
            self.db.add(view)

        self.db.flush()
        return view
