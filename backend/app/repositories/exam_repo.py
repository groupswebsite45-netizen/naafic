from typing import Optional, List, Tuple, Dict, Any
from decimal import Decimal
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, and_
from app.models.exam import Exam, ExamResult
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.models.school_class import SchoolClass
from app.models.subject import Subject
from app.repositories.base_repo import BaseRepository
from app.core.grading import calculate_grade, is_passing


class ExamRepository(BaseRepository[Exam]):
    """Repository for Exam assessments and Student Exam Results."""

    def __init__(self, db: Session):
        super().__init__(Exam, db)

    def get_summary(self, academic_year: Optional[str] = None) -> Dict[str, Any]:
        """Compute live exam statistics from PostgreSQL."""
        q = self.db.query(Exam)
        if academic_year:
            q = q.filter(Exam.academic_year == academic_year)

        total_exams = q.count()

        today = date.today()
        upcoming = q.filter(
            Exam.start_date > today,
            Exam.status.in_(["SCHEDULED", "DRAFT"])
        ).count()

        ongoing = q.filter(
            Exam.start_date <= today,
            or_(Exam.end_date.is_(None), Exam.end_date >= today),
            Exam.status.in_(["ONGOING", "SCHEDULED"])
        ).count()

        completed = q.filter(Exam.status.in_(["COMPLETED", "PUBLISHED"])).count()
        published = q.filter(Exam.status == "PUBLISHED").count()

        results_q = self.db.query(ExamResult)
        if academic_year:
            results_q = results_q.join(Exam).filter(Exam.academic_year == academic_year)
        total_students_assessed = results_q.with_entities(
            func.count(func.distinct(ExamResult.student_id))
        ).scalar() or 0

        return {
            "total_exams": total_exams,
            "upcoming_exams": upcoming,
            "ongoing_exams": ongoing,
            "completed_exams": completed,
            "published_results": published,
            "total_students_assessed": total_students_assessed,
        }

    def get_filter_options(self) -> Dict[str, Any]:
        """Get distinct filter values from real exam data."""
        academic_years = ["2026/2027"]

        exam_types = [
            r[0] for r in self.db.query(Exam.exam_type).distinct().order_by(Exam.exam_type).all()
            if r[0]
        ]
        if not exam_types:
            exam_types = ["Mid-Term", "Final", "Monthly Test", "Quiz", "Continuous Assessment"]

        statuses = [
            r[0] for r in self.db.query(Exam.status).distinct().order_by(Exam.status).all()
            if r[0]
        ]
        if not statuses:
            statuses = ["DRAFT", "SCHEDULED", "ONGOING", "COMPLETED", "PUBLISHED", "CANCELLED"]

        classes = [
            {"id": c.id, "name": c.name, "code": c.code, "academic_year": c.academic_year}
            for c in self.db.query(SchoolClass).filter(SchoolClass.status == "ACTIVE").order_by(SchoolClass.name).all()
        ]
        subjects = [
            {"id": s.id, "name": s.name, "code": s.code}
            for s in self.db.query(Subject).filter(Subject.status == "ACTIVE").order_by(Subject.name).all()
        ]

        return {
            "academic_years": academic_years,
            "exam_types": exam_types,
            "statuses": statuses,
            "classes": classes,
            "subjects": subjects,
        }

    def search_exams(
        self,
        query: Optional[str] = None,
        class_id: Optional[int] = None,
        subject_id: Optional[int] = None,
        academic_year: Optional[str] = None,
        exam_type: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Exam], int]:
        q = self.db.query(Exam)

        if query:
            q = q.filter(
                or_(
                    Exam.name.ilike(f"%{query.strip()}%"),
                    Exam.exam_type.ilike(f"%{query.strip()}%")
                )
            )
        if class_id:
            q = q.filter(Exam.class_id == class_id)
        if subject_id:
            q = q.filter(Exam.subject_id == subject_id)
        if academic_year:
            q = q.filter(Exam.academic_year == academic_year.strip())
        if exam_type:
            q = q.filter(Exam.exam_type.ilike(f"%{exam_type.strip()}%"))
        if status:
            q = q.filter(Exam.status == status.upper().strip())

        total = q.count()
        exams = q.order_by(Exam.start_date.desc(), Exam.id.desc()).offset(skip).limit(limit).all()

        for e in exams:
            self._enrich_exam(e)

        return exams, total

    def _enrich_exam(self, exam: Exam) -> None:
        """Add computed fields to an exam object."""
        results_count = self.db.query(ExamResult).filter(ExamResult.exam_id == exam.id).count()
        y = (exam.academic_year or "").strip()
        year_alt = y.replace("/", "-") if "/" in y else y.replace("-", "/")
        year_variants = list({y, year_alt, y.replace(" ", "")})

        enrolled_count = self.db.query(StudentEnrollment).filter(
            StudentEnrollment.class_id == exam.class_id,
            StudentEnrollment.academic_year.in_(year_variants),
            StudentEnrollment.status == "ACTIVE"
        ).count()
        if enrolled_count == 0:
            enrolled_count = self.db.query(StudentEnrollment).filter(
                StudentEnrollment.class_id == exam.class_id,
                StudentEnrollment.status == "ACTIVE"
            ).count()
        if enrolled_count < results_count:
            enrolled_count = results_count

        exam.results_count = results_count
        exam.enrolled_students_count = enrolled_count
        exam.completion_percentage = round((results_count / enrolled_count * 100) if enrolled_count > 0 else 0.0, 1)

        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        if exam.result_submission_deadline:
            dl = exam.result_submission_deadline
            if dl.tzinfo is None:
                dl = dl.replace(tzinfo=timezone.utc)
            if now > dl and exam.status not in ("PUBLISHED", "COMPLETED"):
                exam.is_overdue = True
                exam.deadline_status = "OVERDUE"
            elif exam.status == "CLOSED":
                exam.is_overdue = False
                exam.deadline_status = "CLOSED"
            elif (dl - now).total_seconds() < 86400 * 3:
                exam.is_overdue = False
                exam.deadline_status = "APPROACHING"
            else:
                exam.is_overdue = False
                exam.deadline_status = "ON_TRACK"
        else:
            exam.is_overdue = False
            exam.deadline_status = "ON_TRACK"

    def get_by_id_enriched(self, exam_id: int) -> Optional[Exam]:
        exam = self.get_by_id(exam_id)
        if exam:
            self._enrich_exam(exam)
        return exam

    def check_conflicts(
        self,
        class_id: int,
        start_date: date,
        end_date: Optional[date] = None,
        exclude_exam_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Check if class has conflicting exams in the requested date range."""
        target_end = end_date or start_date

        q = self.db.query(Exam).filter(
            Exam.class_id == class_id,
            Exam.status.in_(["SCHEDULED", "ONGOING", "DRAFT"])
        )

        if exclude_exam_id:
            q = q.filter(Exam.id != exclude_exam_id)

        # Date overlap check: (StartA <= EndB) and (EndA >= StartB)
        conflicts = []
        for existing in q.all():
            existing_end = existing.end_date or existing.start_date
            if existing.start_date <= target_end and existing_end >= start_date:
                conflicts.append({
                    "conflict_type": "CLASS_DATE_OVERLAP",
                    "exam_id": existing.id,
                    "exam_name": existing.name,
                    "subject_name": existing.subject.name if existing.subject else "Subject",
                    "start_date": str(existing.start_date),
                    "end_date": str(existing_end),
                    "message": f"Class already has '{existing.name}' ({existing.subject.name if existing.subject else ''}) scheduled from {existing.start_date} to {existing_end}."
                })

        return conflicts

    def get_exam_profile(self, exam_id: int) -> Optional[Dict[str, Any]]:
        """Get complete exam profile with student marks sheet."""
        exam = self.get_by_id_enriched(exam_id)
        if not exam:
            return None

        y = (exam.academic_year or "").strip()
        year_alt = y.replace("/", "-") if "/" in y else y.replace("-", "/")
        year_variants = list({y, year_alt, y.replace(" ", "")})

        # Get all enrolled students for this class + academic year (supporting year variations)
        enrollments = self.db.query(StudentEnrollment).filter(
            StudentEnrollment.class_id == exam.class_id,
            StudentEnrollment.academic_year.in_(year_variants),
            StudentEnrollment.status == "ACTIVE"
        ).all()

        if not enrollments:
            enrollments = self.db.query(StudentEnrollment).filter(
                StudentEnrollment.class_id == exam.class_id,
                StudentEnrollment.status == "ACTIVE"
            ).all()

        # Get existing results indexed by student_id
        results = self.db.query(ExamResult).filter(ExamResult.exam_id == exam_id).all()
        results_by_student = {r.student_id: r for r in results}

        student_sheet = []
        marks_list = []
        pass_count = 0
        fail_count = 0
        seen_student_ids = set()

        for enrollment in enrollments:
            student = enrollment.student
            if not student:
                continue
            seen_student_ids.add(student.id)
            existing = results_by_student.get(student.id)
            marks = float(existing.marks_obtained) if (existing and existing.marks_obtained is not None) else None
            grade = existing.grade if existing else None
            is_saved = existing is not None

            if is_saved and marks is not None:
                marks_list.append(marks)
                if is_passing(Decimal(str(marks)), exam.pass_marks):
                    pass_count += 1
                else:
                    fail_count += 1

            student_sheet.append({
                "student_id": student.id,
                "admission_number": student.admission_number,
                "student_name": student.full_name,
                "roll_number": enrollment.roll_number,
                "gender": student.gender,
                "result_id": existing.id if existing else None,
                "marks_obtained": marks,
                "grade": grade,
                "remarks": existing.remarks if existing else None,
                "is_saved": is_saved,
                "status": existing.status if existing else "PENDING",
                "updated_at": existing.updated_at.isoformat() if (existing and existing.updated_at) else None,
            })

        # Also include any student who already has a result submitted by the teacher
        for r in results:
            if r.student_id not in seen_student_ids:
                student = r.student or self.db.query(Student).filter(Student.id == r.student_id).first()
                if not student:
                    continue
                seen_student_ids.add(student.id)
                marks = float(r.marks_obtained) if r.marks_obtained is not None else None
                grade = r.grade
                is_saved = True

                if marks is not None:
                    marks_list.append(marks)
                    if is_passing(Decimal(str(marks)), exam.pass_marks):
                        pass_count += 1
                    else:
                        fail_count += 1

                student_sheet.append({
                    "student_id": student.id,
                    "admission_number": student.admission_number,
                    "student_name": student.full_name,
                    "roll_number": None,
                    "gender": student.gender,
                    "result_id": r.id,
                    "marks_obtained": marks,
                    "grade": grade,
                    "remarks": r.remarks,
                    "is_saved": True,
                    "status": r.status or "SUBMITTED",
                    "updated_at": r.updated_at.isoformat() if r.updated_at else None,
                })

        # Sort: saved students first, then by name
        student_sheet.sort(key=lambda x: (not x["is_saved"], x["student_name"] or ""))

        enrolled_count = max(len(student_sheet), len(enrollments))
        results_count = sum(1 for s in student_sheet if s["is_saved"])
        avg = round(sum(marks_list) / len(marks_list), 1) if marks_list else None
        highest = round(max(marks_list), 1) if marks_list else None
        lowest = round(min(marks_list), 1) if marks_list else None
        pass_rate = round((pass_count / results_count * 100) if results_count > 0 else 0.0, 1)
        completion_pct = round((results_count / enrolled_count * 100) if enrolled_count > 0 else 0.0, 1)

        return {
            "exam": exam,
            "enrolled_count": enrolled_count,
            "results_count": results_count,
            "completion_percentage": completion_pct,
            "average_score": avg,
            "highest_score": highest,
            "lowest_score": lowest,
            "pass_count": pass_count,
            "fail_count": fail_count,
            "pass_rate": pass_rate,
            "student_sheet": student_sheet,
        }

    def upsert_result(
        self,
        exam_id: int,
        student_id: int,
        subject_id: int,
        marks_obtained: Decimal,
        recorded_by_id: Optional[int] = None,
        custom_remarks: Optional[str] = None
    ) -> ExamResult:
        exam = self.get_by_id(exam_id)
        max_marks = exam.max_marks if exam else Decimal("100.00")
        grade, default_remark, _ = calculate_grade(marks_obtained, max_marks)
        remarks = custom_remarks if custom_remarks else default_remark

        result = self.db.query(ExamResult).filter(
            ExamResult.exam_id == exam_id,
            ExamResult.student_id == student_id,
            ExamResult.subject_id == subject_id
        ).first()

        if result:
            result.marks_obtained = marks_obtained
            result.grade = grade
            result.remarks = remarks
            result.recorded_by_id = recorded_by_id
        else:
            result = ExamResult(
                exam_id=exam_id,
                student_id=student_id,
                subject_id=subject_id,
                marks_obtained=marks_obtained,
                grade=grade,
                remarks=remarks,
                recorded_by_id=recorded_by_id
            )
            self.db.add(result)

        self.db.flush()
        return result

    def get_results_by_exam(self, exam_id: int) -> List[ExamResult]:
        results = self.db.query(ExamResult).filter(ExamResult.exam_id == exam_id).all()
        for r in results:
            if r.student:
                r.student_name = r.student.full_name
                r.student_admission_number = r.student.admission_number
        return results

    def get_results_by_student(self, student_id: int) -> List[ExamResult]:
        return self.db.query(ExamResult).filter(
            ExamResult.student_id == student_id
        ).order_by(ExamResult.created_at.desc()).all()

    def get_student_report_card(self, exam_id: int, student_id: int) -> Optional[Dict[str, Any]]:
        """Generate official Hawlwadaag School Report Card data for a student."""
        exam = self.get_by_id_enriched(exam_id)
        if not exam:
            return None

        student = self.db.query(Student).filter(Student.id == student_id).first()
        if not student:
            return None

        y = (exam.academic_year or "").strip()
        year_alt = y.replace("/", "-") if "/" in y else y.replace("-", "/")
        year_variants = list({y, year_alt, y.replace(" ", "")})

        enrollment = self.db.query(StudentEnrollment).filter(
            StudentEnrollment.student_id == student_id,
            StudentEnrollment.academic_year.in_(year_variants),
            StudentEnrollment.status == "ACTIVE"
        ).first()

        if not enrollment:
            enrollment = self.db.query(StudentEnrollment).filter(
                StudentEnrollment.student_id == student_id,
                StudentEnrollment.class_id == exam.class_id,
                StudentEnrollment.status == "ACTIVE"
            ).first()

        # Get all results for this student across all exams in the same academic year and exam type
        series_exams = self.db.query(Exam).filter(
            Exam.class_id == exam.class_id,
            Exam.academic_year.in_(year_variants),
            Exam.exam_type == exam.exam_type
        ).all()
        series_exam_ids = [e.id for e in series_exams]

        results = self.db.query(ExamResult).filter(
            ExamResult.exam_id.in_(series_exam_ids),
            ExamResult.student_id == student_id
        ).all()

        subject_entries = []
        total_obtained = Decimal("0.00")
        total_possible = Decimal("0.00")

        for r in results:
            ex = next((e for e in series_exams if e.id == r.exam_id), exam)
            max_m = ex.max_marks
            total_obtained += r.marks_obtained
            total_possible += max_m
            percentage = round((float(r.marks_obtained) / float(max_m) * 100.0), 1) if max_m > 0 else 0.0

            subject_entries.append({
                "subject_id": r.subject_id,
                "subject_name": r.subject.name if r.subject else "Subject",
                "subject_code": r.subject.code if r.subject else "",
                "marks_obtained": float(r.marks_obtained),
                "max_marks": float(max_m),
                "pass_marks": float(ex.pass_marks),
                "grade": r.grade or "N/A",
                "percentage": percentage,
                "remarks": r.remarks or "",
                "is_passed": float(r.marks_obtained) >= float(ex.pass_marks)
            })

        overall_percentage = round((float(total_obtained) / float(total_possible) * 100.0), 1) if total_possible > 0 else 0.0
        overall_grade, overall_remark, _ = calculate_grade(total_obtained, total_possible) if total_possible > 0 else ("N/A", "No records", 0.0)

        return {
            "school_name": "Education Management System",
            "school_motto": "Excellence in Education & Character Building",
            "academic_year": exam.academic_year,
            "exam_name": exam.name,
            "exam_type": exam.exam_type,
            "student": {
                "id": student.id,
                "admission_number": student.admission_number,
                "full_name": student.full_name,
                "gender": student.gender,
                "roll_number": enrollment.roll_number if enrollment else None,
                "class_name": exam.school_class.name if exam.school_class else "N/A",
                "class_section": exam.school_class.section if exam.school_class else "",
            },
            "subjects": subject_entries,
            "summary": {
                "total_subjects": len(subject_entries),
                "total_marks_obtained": float(total_obtained),
                "total_possible_marks": float(total_possible),
                "overall_percentage": overall_percentage,
                "overall_grade": overall_grade,
                "overall_remark": overall_remark,
                "publication_status": exam.status
            }
        }
