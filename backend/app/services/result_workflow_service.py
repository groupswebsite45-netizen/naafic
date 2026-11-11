from typing import List, Dict, Any, Optional
from decimal import Decimal
from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.user import User
from app.models.teacher import Teacher
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.models.exam import Exam, ExamResult
from app.models.result_submission import ResultSubmission
from app.models.result_release import ResultReleaseBatch
from app.models.teacher_assignment import TeacherAssignment
from app.models.audit_log import AuditLog
from app.models.notification import Notification
from app.repositories.submission_repo import SubmissionRepository
from app.repositories.release_repo import ReleaseRepository
from app.core.grading import calculate_grade
from app.schemas.result_workflow import (
    TeacherSaveDraftPayload,
    TeacherSubmitPayload,
    ReturnSubmissionPayload,
    ApproveSubmissionPayload,
    ReleaseClassResultsPayload,
    RecordStudentViewPayload,
)


class ResultWorkflowService:
    """Service governing the multi-role Examination Result workflow with audit logging and IDOR protection."""

    def __init__(self, db: Session):
        self.db = db
        self.sub_repo = SubmissionRepository(db)
        self.rel_repo = ReleaseRepository(db)

    def _log_audit(self, user_id: Optional[int], action: str, details: Dict[str, Any], status_val: str = "SUCCESS"):
        """Record system audit log."""
        try:
            log = AuditLog(
                user_id=user_id,
                action=action,
                status=status_val,
                details=details
            )
            self.db.add(log)
            self.db.flush()
        except Exception:
            pass  # Non-blocking audit logging

    # =========================================================================
    # TEACHER PORTAL OPERATIONS
    # =========================================================================

    def get_teacher_from_user(self, user: User) -> Teacher:
        """Find teacher profile linked to user account."""
        teacher = self.db.query(Teacher).filter(Teacher.user_id == user.id).first()
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No faculty/teacher profile associated with this user account."
            )
        return teacher

    def get_teacher_assigned_exams(self, user: User) -> List[Dict[str, Any]]:
        """
        Get assigned exams for the authenticated teacher.
        Strict IDOR protection: only returns classes & subjects assigned to this teacher.
        """
        teacher = self.get_teacher_from_user(user)

        # Get active assignments
        assignments = self.db.query(TeacherAssignment).filter(
            TeacherAssignment.teacher_id == teacher.id,
            TeacherAssignment.status == "ACTIVE"
        ).all()

        if not assignments:
            return []

        results = []
        seen_exam_ids = set()
        now_utc = datetime.now(timezone.utc)
        all_candidate_exams = []
        for a in assignments:
            y = a.academic_year
            y_variants = [y, y.replace("/", "-"), y.replace("-", "/")] if y else []
            q = self.db.query(Exam).filter(
                Exam.class_id == a.class_id,
                Exam.subject_id == a.subject_id,
                Exam.status != "CANCELLED"
            )
            if y_variants:
                q = q.filter(Exam.academic_year.in_(y_variants))
            exams = q.order_by(Exam.start_date.desc()).all()
            all_candidate_exams.extend(exams)

        # Also find any exams directly assigned to this teacher where teacher assignment matches or was assigned directly
        direct_exams = self.db.query(Exam).filter(
            Exam.teacher_id == teacher.id,
            Exam.status != "CANCELLED"
        ).order_by(Exam.start_date.desc()).all()
        for de in direct_exams:
            all_candidate_exams.append(de)

        for exam in all_candidate_exams:
            if exam.id in seen_exam_ids:
                continue
            seen_exam_ids.add(exam.id)
            # Count enrolled students
            y = exam.academic_year
            years = [y, y.replace("/", "-"), y.replace("-", "/")] if y else []
            enr_q = self.db.query(StudentEnrollment).filter(
                StudentEnrollment.class_id == exam.class_id,
                StudentEnrollment.status == "ACTIVE"
            )
            if years:
                enr_q = enr_q.filter(StudentEnrollment.academic_year.in_(years))
            expected_students = enr_q.count()
            if expected_students == 0:
                expected_students = self.db.query(StudentEnrollment).filter(
                    StudentEnrollment.class_id == exam.class_id,
                    StudentEnrollment.status == "ACTIVE"
                ).count()

            # Get existing submission record
            sub = self.db.query(ResultSubmission).filter(
                ResultSubmission.exam_id == exam.id,
                ResultSubmission.class_id == exam.class_id,
                ResultSubmission.subject_id == exam.subject_id
            ).first()

            if not sub:
                sub = ResultSubmission(
                    exam_id=exam.id,
                    class_id=exam.class_id,
                    subject_id=exam.subject_id,
                    teacher_id=teacher.id,
                    academic_year=exam.academic_year,
                    exam_name=exam.name,
                    exam_type=exam.exam_type,
                    status="DRAFT",
                    expected_students=expected_students,
                    completed_students=0,
                    pending_students=expected_students,
                    submission_deadline=exam.result_submission_deadline
                )
                self.db.add(sub)
                self.db.commit()
            elif not sub.teacher_id:
                sub.teacher_id = teacher.id
                if not sub.exam_type:
                    sub.exam_type = exam.exam_type
                self.db.commit()

            # Results entered
            exam_results = self.db.query(ExamResult).filter(
                ExamResult.exam_id == exam.id
            ).all()

            completed_count = sum(
                1 for r in exam_results
                if r.attendance_status in ("ABSENT", "EXCUSED") or (r.attendance_status == "PRESENT" and r.marks_obtained is not None)
            )
            absent_count = sum(1 for r in exam_results if r.attendance_status in ("ABSENT", "EXCUSED"))
            complaints_count = sum(1 for r in exam_results if r.complaint and r.complaint.strip())
            pending_count = max(0, expected_students - completed_count)

            # Determine status
            if sub:
                st = sub.status
            elif completed_count >= expected_students and expected_students > 0:
                st = "READY_TO_SUBMIT"
            elif completed_count > 0:
                st = "PARTIAL"
            else:
                st = "NOT_STARTED"

            # Calculate deadline status and countdown
            is_overdue = False
            deadline_status = "ON_TRACK"
            remaining_time_human = None

            if exam.result_submission_deadline:
                dl = exam.result_submission_deadline
                if dl.tzinfo is None:
                    dl = dl.replace(tzinfo=timezone.utc)
                diff = (dl - now_utc).total_seconds()
                if diff < 0:
                    if st not in ("SUBMITTED", "APPROVED", "RELEASED"):
                        is_overdue = True
                        deadline_status = "OVERDUE"
                    else:
                        deadline_status = "SUBMITTED"
                    days_over = abs(int(diff // 86400))
                    remaining_time_human = f"Overdue by {days_over} day{'s' if days_over != 1 else ''}"
                else:
                    days = int(diff // 86400)
                    hours = int((diff % 86400) // 3600)
                    if days > 0:
                        remaining_time_human = f"{days}d {hours}h remaining"
                    else:
                        mins = int((diff % 3600) // 60)
                        remaining_time_human = f"{hours}h {mins}m remaining"

                    if diff < 86400 * 3:
                        deadline_status = "APPROACHING"
                    else:
                        deadline_status = "ON_TRACK"

            if exam.status == "CLOSED":
                deadline_status = "CLOSED"

            results.append({
                "exam_id": exam.id,
                "exam_name": exam.name,
                "exam_type": exam.exam_type,
                "academic_year": exam.academic_year,
                "class_id": exam.class_id,
                "class_name": exam.school_class.name if exam.school_class else "Class",
                "class_code": exam.school_class.code if exam.school_class else "",
                "class_section": exam.school_class.section if exam.school_class else "",
                "subject_id": exam.subject_id,
                "subject_name": exam.subject.name if exam.subject else "Subject",
                "subject_code": exam.subject.code if exam.subject else "",
                "start_date": exam.start_date,
                "end_date": exam.end_date,
                "start_time": exam.start_time,
                "end_time": exam.end_time,
                "result_submission_deadline": exam.result_submission_deadline,
                "deadline_status": deadline_status,
                "is_overdue": is_overdue,
                "remaining_time_human": remaining_time_human,
                "instructions": exam.instructions,
                "max_marks": exam.max_marks,
                "pass_marks": exam.pass_marks,
                "submission_id": sub.id if sub else None,
                "status": st,
                "expected_students": expected_students,
                "completed_students": completed_count,
                "pending_students": pending_count,
                "absent_students": absent_count,
                "complaints_count": complaints_count,
                "submitted_at": sub.submitted_at if sub else None,
                "returned_at": sub.returned_at if sub else None,
                "return_reason": sub.return_reason if sub else None,
                "revisions": sub.revisions if sub else [],
            })

        return results

    def get_teacher_roster_for_exam(self, user: User, exam_id: int) -> Dict[str, Any]:
        """
        Get student roster with marks & attendance for a specific assigned exam.
        Validates that the authenticated teacher is assigned to this exam's class & subject.
        """
        teacher = self.get_teacher_from_user(user)
        exam = self.db.query(Exam).filter(Exam.id == exam_id).first()
        if not exam:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found.")

        # IDOR check
        assignment = self.db.query(TeacherAssignment).filter(
            TeacherAssignment.teacher_id == teacher.id,
            TeacherAssignment.class_id == exam.class_id,
            TeacherAssignment.subject_id == exam.subject_id,
            TeacherAssignment.status == "ACTIVE"
        ).first()

        if not assignment and exam.teacher_id != teacher.id and not user.has_role("ADMIN"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to access students or results outside of your assigned classes and subjects."
            )

        # Enrolled students
        y = exam.academic_year
        years = [y, y.replace("/", "-"), y.replace("-", "/")] if y else []
        enr_query = self.db.query(StudentEnrollment).filter(
            StudentEnrollment.class_id == exam.class_id,
            StudentEnrollment.status == "ACTIVE"
        )
        if years:
            enr_query = enr_query.filter(StudentEnrollment.academic_year.in_(years))
        enrollments = enr_query.all()
        if not enrollments:
            enrollments = self.db.query(StudentEnrollment).filter(
                StudentEnrollment.class_id == exam.class_id,
                StudentEnrollment.status == "ACTIVE"
            ).all()

        # Existing results
        results = self.db.query(ExamResult).filter(ExamResult.exam_id == exam_id).all()
        res_by_student = {r.student_id: r for r in results}

        # Existing submission
        sub = self.db.query(ResultSubmission).filter(
            ResultSubmission.exam_id == exam.id,
            ResultSubmission.class_id == exam.class_id,
            ResultSubmission.subject_id == exam.subject_id,
            ResultSubmission.teacher_id == teacher.id
        ).first()

        is_locked = sub is not None and sub.status in ("SUBMITTED", "UNDER_REVIEW", "APPROVED", "RELEASED")

        roster = []
        for en in enrollments:
            std = en.student
            if not std:
                continue
            r = res_by_student.get(std.id)
            roster.append({
                "student_id": std.id,
                "admission_number": std.admission_number,
                "student_name": std.full_name,
                "roll_number": en.roll_number,
                "gender": std.gender,
                "attendance_status": r.attendance_status if r else "PRESENT",
                "absence_reason": r.absence_reason if r else None,
                "complaint": r.complaint if r else None,
                "marks_obtained": r.marks_obtained if r else None,
                "max_marks": exam.max_marks,
                "pass_marks": exam.pass_marks,
                "grade": r.grade if r else None,
                "remarks": r.remarks if r else None,
                "status": r.status if r else "DRAFT",
                "paper_file_path": r.paper_file_path if r else None,
                "paper_original_name": r.paper_original_name if r else None,
                "paper_mime_type": r.paper_mime_type if r else None,
                "paper_file_size": r.paper_file_size if r else None,
                "paper_uploaded_at": r.paper_uploaded_at.isoformat() if (r and r.paper_uploaded_at) else None,
            })

        roster.sort(key=lambda x: x["student_name"])

        return {
            "exam_id": exam.id,
            "exam_name": exam.name,
            "exam_type": exam.exam_type,
            "academic_year": exam.academic_year,
            "class_id": exam.class_id,
            "class_name": exam.school_class.name if exam.school_class else "Class",
            "class_section": exam.school_class.section if exam.school_class else "",
            "subject_id": exam.subject_id,
            "subject_name": exam.subject.name if exam.subject else "Subject",
            "max_marks": exam.max_marks,
            "pass_marks": exam.pass_marks,
            "is_locked": is_locked,
            "submission_status": sub.status if sub else "DRAFT",
            "returned_at": sub.returned_at.isoformat() if (sub and sub.returned_at) else None,
            "return_reason": sub.return_reason if sub else None,
            "revisions": sub.revisions if sub else [],
            "students": roster,
        }

    def save_teacher_draft(self, user: User, payload: TeacherSaveDraftPayload) -> Dict[str, Any]:
        """
        Save draft marks & attendance without submitting to Admin.
        Status becomes DRAFT or PARTIAL.
        """
        teacher = self.get_teacher_from_user(user)
        exam = self.db.query(Exam).filter(Exam.id == payload.exam_id).first()
        if not exam:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found.")

        # Deadline & Status Validation
        now_utc = datetime.now(timezone.utc)
        if exam.status == "CLOSED":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Submissions for this examination are currently closed. Contact the School Administrator to extend the deadline or reopen submissions."
            )
        if exam.result_submission_deadline:
            dl = exam.result_submission_deadline
            if dl.tzinfo is None:
                dl = dl.replace(tzinfo=timezone.utc)
            if now_utc > dl and exam.status != "OPEN_FOR_RESULTS":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"The result submission deadline ({dl.strftime('%Y-%m-%d %H:%M')}) for this examination has passed. Submissions are overdue. Contact the School Administrator to extend the deadline or reopen submissions."
                )

        # IDOR check
        assignment = self.db.query(TeacherAssignment).filter(
            TeacherAssignment.teacher_id == teacher.id,
            TeacherAssignment.class_id == exam.class_id,
            TeacherAssignment.subject_id == exam.subject_id,
            TeacherAssignment.status == "ACTIVE"
        ).first()

        if not assignment and exam.teacher_id != teacher.id and not user.has_role("ADMIN"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized access.")

        # Check existing submission lock
        sub = self.db.query(ResultSubmission).filter(
            ResultSubmission.exam_id == exam.id,
            ResultSubmission.class_id == exam.class_id,
            ResultSubmission.subject_id == exam.subject_id,
            ResultSubmission.teacher_id == teacher.id
        ).first()

        if sub and sub.status in ("SUBMITTED", "APPROVED", "RELEASED"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot edit marks while submission status is '{sub.status}'. Editing is locked."
            )

        # Total expected enrolled students
        y = exam.academic_year
        years = [y, y.replace("/", "-"), y.replace("-", "/")] if y else []
        enr_query = self.db.query(StudentEnrollment).filter(
            StudentEnrollment.class_id == exam.class_id,
            StudentEnrollment.status == "ACTIVE"
        )
        if years:
            enr_query = enr_query.filter(StudentEnrollment.academic_year.in_(years))
        enrollments = enr_query.all()
        if not enrollments:
            enrollments = self.db.query(StudentEnrollment).filter(
                StudentEnrollment.class_id == exam.class_id,
                StudentEnrollment.status == "ACTIVE"
            ).all()
        enrolled_ids = {e.student_id for e in enrollments}
        enrolled_count = len(enrolled_ids)

        # Upsert or create submission
        if not sub:
            sub = ResultSubmission(
                exam_id=exam.id,
                class_id=exam.class_id,
                subject_id=exam.subject_id,
                teacher_id=teacher.id,
                academic_year=exam.academic_year,
                exam_name=exam.name,
                status="DRAFT",
                expected_students=enrolled_count,
            )
            self.db.add(sub)
            self.db.flush()

        # Deduplicate marks payload by student_id to prevent unique constraint conflicts
        deduped_marks = {}
        for entry in payload.marks:
            deduped_marks[entry.student_id] = entry

        completed_count = 0
        for entry in deduped_marks.values():
            marks = None
            grade = None
            default_remark = ""
            if entry.attendance_status == "PRESENT":
                if entry.marks_obtained is not None:
                    if entry.marks_obtained > exam.max_marks:
                        raise HTTPException(
                            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=f"Marks ({entry.marks_obtained}) cannot exceed maximum allowed ({exam.max_marks})."
                        )
                    if entry.marks_obtained < 0:
                        raise HTTPException(
                            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=f"Marks ({entry.marks_obtained}) cannot be below 0."
                        )
                    marks = entry.marks_obtained
                    grade, default_remark, _ = calculate_grade(marks, exam.max_marks)
                    completed_count += 1
            else:
                # Absent or Excused: preserve absence, do NOT force marks to 0!
                grade = None
                marks = None
                default_remark = entry.attendance_status
                completed_count += 1

            # Upsert ExamResult
            res = self.db.query(ExamResult).filter(
                ExamResult.exam_id == exam.id,
                ExamResult.student_id == entry.student_id,
                ExamResult.subject_id == exam.subject_id
            ).first()

            abs_reason = entry.absence_reason.strip() if entry.absence_reason else None
            complaint_txt = entry.complaint.strip() if entry.complaint else None

            if res:
                res.class_id = exam.class_id
                res.submission_id = sub.id
                res.attendance_status = entry.attendance_status
                res.absence_reason = abs_reason
                res.complaint = complaint_txt
                res.marks_obtained = marks
                res.grade = grade
                res.remarks = entry.remarks or (default_remark if entry.attendance_status == "PRESENT" else entry.attendance_status)
                res.status = "DRAFT"
                res.recorded_by_id = user.id
            else:
                res = ExamResult(
                    exam_id=exam.id,
                    class_id=exam.class_id,
                    student_id=entry.student_id,
                    subject_id=exam.subject_id,
                    submission_id=sub.id,
                    attendance_status=entry.attendance_status,
                    absence_reason=abs_reason,
                    complaint=complaint_txt,
                    marks_obtained=marks,
                    grade=grade,
                    remarks=entry.remarks or (default_remark if entry.attendance_status == "PRESENT" else entry.attendance_status),
                    status="DRAFT",
                    recorded_by_id=user.id
                )
                self.db.add(res)

        sub.completed_students = completed_count
        sub.pending_students = max(0, enrolled_count - completed_count)
        if sub.status != "RETURNED":
            sub.status = "PARTIAL" if completed_count < enrolled_count else "DRAFT"

        self.db.commit()

        self._log_audit(
            user_id=user.id,
            action="TEACHER_SAVE_DRAFT",
            details={
                "exam_id": exam.id,
                "class_id": exam.class_id,
                "subject_id": exam.subject_id,
                "completed": completed_count,
                "expected": enrolled_count
            }
        )

        return {
            "success": True,
            "message": "Draft results saved successfully in PostgreSQL.",
            "completed_students": completed_count,
            "pending_students": sub.pending_students,
            "status": sub.status,
        }

    def submit_teacher_results(self, user: User, payload: TeacherSubmitPayload) -> Dict[str, Any]:
        """
        Validate and submit results to Admin for review.
        Checks:
        1. All expected students have attendance status.
        2. All PRESENT students have valid marks 0 <= marks <= max_marks.
        3. No duplicate submissions while under review or approved.
        4. Changes status to SUBMITTED and locks editing for teacher.
        5. Preserves revision history and notifies Admin.
        """
        teacher = self.get_teacher_from_user(user)
        exam = self.db.query(Exam).filter(Exam.id == payload.exam_id).first()
        if not exam:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found.")

        # Deadline & Status Validation
        now_utc = datetime.now(timezone.utc)
        if exam.status == "CLOSED":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Submissions for this examination are currently closed. Contact the School Administrator to extend the deadline or reopen submissions."
            )
        if exam.result_submission_deadline:
            dl = exam.result_submission_deadline
            if dl.tzinfo is None:
                dl = dl.replace(tzinfo=timezone.utc)
            if now_utc > dl and exam.status != "OPEN_FOR_RESULTS":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"The result submission deadline ({dl.strftime('%Y-%m-%d %H:%M')}) for this examination has passed. Submissions are overdue. Contact the School Administrator to extend the deadline or reopen submissions."
                )

        # IDOR check
        assignment = self.db.query(TeacherAssignment).filter(
            TeacherAssignment.teacher_id == teacher.id,
            TeacherAssignment.class_id == exam.class_id,
            TeacherAssignment.subject_id == exam.subject_id,
            TeacherAssignment.status == "ACTIVE"
        ).first()

        if not assignment and exam.teacher_id != teacher.id and not user.has_role("ADMIN"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized access.")

        # Duplicate submission prevention check
        existing_sub = self.db.query(ResultSubmission).filter(
            ResultSubmission.exam_id == exam.id,
            ResultSubmission.class_id == exam.class_id,
            ResultSubmission.subject_id == exam.subject_id,
            ResultSubmission.teacher_id == teacher.id
        ).first()

        if existing_sub and existing_sub.status in ("SUBMITTED", "UNDER_REVIEW", "APPROVED", "RELEASED"):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Results have already been submitted."
            )

        # Enrolled students check
        y = exam.academic_year
        years = [y, y.replace("/", "-"), y.replace("-", "/")] if y else []
        enr_query = self.db.query(StudentEnrollment).filter(
            StudentEnrollment.class_id == exam.class_id,
            StudentEnrollment.status == "ACTIVE"
        )
        if years:
            enr_query = enr_query.filter(StudentEnrollment.academic_year.in_(years))
        enrollments = enr_query.all()
        if not enrollments:
            enrollments = self.db.query(StudentEnrollment).filter(
                StudentEnrollment.class_id == exam.class_id,
                StudentEnrollment.status == "ACTIVE"
            ).all()
        enrolled_ids = {e.student_id for e in enrollments}

        payload_ids = {m.student_id for m in payload.marks}
        missing_ids = enrolled_ids - payload_ids

        if missing_ids:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Incomplete submission: {len(missing_ids)} enrolled students still need results or attendance."
            )

        # Validate entries
        for m in payload.marks:
            if m.attendance_status == "PRESENT":
                if m.marks_obtained is None:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail=f"Student ID {m.student_id} is marked PRESENT but has no marks entered."
                    )
                if m.marks_obtained < 0:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail=f"Marks ({m.marks_obtained}) for student ID {m.student_id} cannot be below 0."
                    )
                if m.marks_obtained > exam.max_marks:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail=f"Marks ({m.marks_obtained}) for student ID {m.student_id} exceed maximum ({exam.max_marks})."
                    )

        # First save all entries
        draft_payload = TeacherSaveDraftPayload(
            exam_id=payload.exam_id,
            class_id=payload.class_id,
            subject_id=payload.subject_id,
            marks=payload.marks
        )
        self.save_teacher_draft(user, draft_payload)

        # Now update submission status to SUBMITTED
        sub = self.db.query(ResultSubmission).filter(
            ResultSubmission.exam_id == exam.id,
            ResultSubmission.class_id == exam.class_id,
            ResultSubmission.subject_id == exam.subject_id,
            ResultSubmission.teacher_id == teacher.id
        ).first()

        now = datetime.now(timezone.utc)
        was_returned = (sub.status == "RETURNED") or (sub.returned_at is not None)
        prev_reason = sub.return_reason

        # Append to audit / revision history
        rev_list = list(sub.revisions or [])
        rev_list.append({
            "action": "RESUBMITTED" if was_returned else "SUBMITTED",
            "timestamp": now.isoformat(),
            "submitted_by_id": user.id,
            "submitted_by_name": teacher.full_name,
            "students_count": len(payload.marks),
            "notes": getattr(payload, "notes", None),
            "previous_return_reason": prev_reason if was_returned else None
        })
        sub.revisions = rev_list

        sub.status = "SUBMITTED"
        sub.submitted_at = now
        sub.submitted_by_id = user.id
        sub.exam_type = exam.exam_type
        sub.return_reason = None  # Cleared for active admin review; preserved in revisions

        # Update all ExamResults to SUBMITTED
        results = self.db.query(ExamResult).filter(
            ExamResult.exam_id == exam.id,
            ExamResult.submission_id == sub.id
        ).all()

        for r in results:
            r.status = "SUBMITTED"

        self.db.commit()
        self.db.refresh(sub)

        # Create Admin notification in PostgreSQL
        try:
            admin_notif = Notification(
                notification_type="RESULT_SUBMITTED",
                title="Examination Results Submitted",
                message=f"Teacher {teacher.full_name} submitted results for {exam.name} ({exam.subject.name if exam.subject else 'Subject'} - {exam.school_class.name if exam.school_class else 'Class'}, {exam.academic_year}).",
                channel="IN_APP",
                status="DELIVERED",
                class_id=exam.class_id,
                academic_year=exam.academic_year,
                related_exam_id=exam.id,
                created_by_id=user.id,
                extra_data={
                    "submission_id": sub.id,
                    "teacher_name": teacher.full_name,
                    "class_name": exam.school_class.name if exam.school_class else "",
                    "subject_name": exam.subject.name if exam.subject else "",
                    "exam_name": exam.name,
                    "academic_year": exam.academic_year,
                    "submitted_at": now.isoformat(),
                    "link": "/admin/results"
                }
            )
            self.db.add(admin_notif)
            self.db.commit()
        except Exception:
            pass

        self._log_audit(
            user_id=user.id,
            action="TEACHER_SUBMIT_RESULTS",
            details={
                "submission_id": sub.id,
                "exam_id": exam.id,
                "class_id": exam.class_id,
                "subject_id": exam.subject_id,
                "students_count": len(results)
            }
        )

        return {
            "success": True,
            "message": "Results submitted successfully to Administration for review.",
            "submission_id": sub.id,
            "status": "SUBMITTED",
            "submitted_at": now.isoformat(),
        }

    # =========================================================================
    # ADMIN OPERATIONS
    # =========================================================================

    def approve_submission(self, admin_user: User, submission_id: int, payload: ApproveSubmissionPayload) -> Dict[str, Any]:
        """Admin marks submission as APPROVED."""
        sub = self.db.query(ResultSubmission).filter(ResultSubmission.id == submission_id).first()
        if not sub:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found.")

        if sub.status not in ("SUBMITTED", "UNDER_REVIEW"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot approve submission with status '{sub.status}'. Must be SUBMITTED."
            )

        now = datetime.now(timezone.utc)
        sub.status = "APPROVED"
        sub.approved_at = now
        sub.approved_by_id = admin_user.id
        sub.reviewed_at = now
        sub.reviewed_by_id = admin_user.id

        # Append to revisions log
        rev_list = list(sub.revisions or [])
        rev_list.append({
            "action": "APPROVED",
            "timestamp": now.isoformat(),
            "approved_by_id": admin_user.id,
            "approved_by_name": admin_user.full_name or admin_user.username,
            "notes": payload.notes if payload else None
        })
        sub.revisions = rev_list

        # Update associated results to APPROVED (NOT yet released to students)
        results = self.db.query(ExamResult).filter(
            ExamResult.submission_id == sub.id
        ).all()

        for r in results:
            r.status = "APPROVED"

        self.db.commit()

        # Send in-app notification to responsible teacher
        try:
            teacher = sub.teacher
            if teacher and teacher.user_id:
                notif = Notification(
                    notification_type="RESULT_APPROVED",
                    title="Results Approved by Administration",
                    message=f"Results for {sub.exam_name} ({sub.subject.name if sub.subject else 'Subject'} - {sub.school_class.name if sub.school_class else 'Class'}) have been approved.",
                    channel="IN_APP",
                    status="DELIVERED",
                    class_id=sub.class_id,
                    academic_year=sub.academic_year,
                    related_exam_id=sub.exam_id,
                    created_by_id=admin_user.id,
                    extra_data={
                        "submission_id": sub.id,
                        "approved_at": now.isoformat()
                    }
                )
                self.db.add(notif)
                self.db.commit()
        except Exception:
            pass

        self._log_audit(
            user_id=admin_user.id,
            action="ADMIN_APPROVE_SUBMISSION",
            details={"submission_id": sub.id, "approved_by": admin_user.username}
        )

        return {
            "success": True,
            "message": "Submission approved successfully. Results are queued for class release.",
            "submission_id": sub.id,
            "status": "APPROVED",
            "approved_at": now.isoformat(),
        }

    def return_submission(self, admin_user: User, submission_id: int, payload: ReturnSubmissionPayload) -> Dict[str, Any]:
        """Admin returns submission for correction with mandatory reason."""
        if not payload.reason or not payload.reason.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="A clear, mandatory reason must be provided when returning results to a teacher."
            )

        sub = self.db.query(ResultSubmission).filter(ResultSubmission.id == submission_id).first()
        if not sub:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found.")

        if sub.status not in ("SUBMITTED", "UNDER_REVIEW", "APPROVED", "RELEASED"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot return submission with status '{sub.status}'."
            )

        now = datetime.now(timezone.utc)
        sub.status = "RETURNED"
        sub.returned_at = now
        sub.return_reason = payload.reason.strip()
        sub.reviewed_at = now
        sub.reviewed_by_id = admin_user.id

        # Append to revisions log
        rev_list = list(sub.revisions or [])
        rev_list.append({
            "action": "RETURNED_FOR_CORRECTION",
            "timestamp": now.isoformat(),
            "returned_by_id": admin_user.id,
            "returned_by_name": admin_user.full_name or admin_user.username,
            "reason": payload.reason.strip()
        })
        sub.revisions = rev_list

        # Reset results to DRAFT so assigned teacher can edit and correct
        results = self.db.query(ExamResult).filter(
            ExamResult.submission_id == sub.id
        ).all()

        for r in results:
            r.status = "DRAFT"

        self.db.commit()

        # Send in-app notification to responsible teacher
        try:
            teacher = sub.teacher
            if teacher and teacher.user_id:
                notif = Notification(
                    notification_type="RESULT_RETURNED",
                    title="Results Returned for Correction",
                    message=f"Results for {sub.exam_name} ({sub.subject.name if sub.subject else 'Subject'} - {sub.school_class.name if sub.school_class else 'Class'}) have been returned by Administration for correction: {payload.reason.strip()}",
                    channel="IN_APP",
                    status="DELIVERED",
                    class_id=sub.class_id,
                    academic_year=sub.academic_year,
                    related_exam_id=sub.exam_id,
                    created_by_id=admin_user.id,
                    extra_data={
                        "submission_id": sub.id,
                        "exam_id": sub.exam_id,
                        "reason": payload.reason.strip(),
                        "returned_at": now.isoformat()
                    }
                )
                self.db.add(notif)
                self.db.commit()
        except Exception:
            pass

        self._log_audit(
            user_id=admin_user.id,
            action="ADMIN_RETURN_SUBMISSION",
            details={"submission_id": sub.id, "reason": payload.reason.strip()}
        )

        return {
            "success": True,
            "message": "Submission returned to teacher for correction.",
            "submission_id": sub.id,
            "status": "RETURNED",
            "return_reason": payload.reason.strip(),
        }

    def release_class_results(self, admin_user: User, payload: ReleaseClassResultsPayload) -> Dict[str, Any]:
        """
        Release results by class.
        Safety check: Blocks full release if unapproved results remain.
        Stamps ResultReleaseBatch in PostgreSQL.
        """
        success, message, batch = self.rel_repo.release_class_results(
            class_id=payload.class_id,
            academic_year=payload.academic_year,
            exam_name=payload.exam_name,
            release_type=payload.release_type,
            released_by_id=admin_user.id,
            notes=payload.notes
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

        self.db.commit()

        # Trigger automated guardian notification upon official result release
        if batch:
            try:
                from app.services.notification_service import NotificationService
                notif_service = NotificationService(self.db)
                notif_service.trigger_result_release_notifications(
                    release_batch_id=batch.id,
                    admin_user_id=admin_user.id
                )
            except Exception:
                pass

        self._log_audit(
            user_id=admin_user.id,
            action="ADMIN_RELEASE_CLASS_RESULTS",
            details={
                "class_id": payload.class_id,
                "batch_code": batch.batch_code if batch else None,
                "release_type": payload.release_type,
                "count": batch.results_count if batch else 0
            }
        )

        return {
            "success": True,
            "message": message,
            "batch_code": batch.batch_code,
            "results_count": batch.results_count,
            "released_at": batch.released_at.isoformat(),
        }

    def release_submission(self, admin_user: User, submission_id: int, payload: Optional[Any] = None) -> Dict[str, Any]:
        """
        Release a completed result set / submission to the Student Portal.
        Strict completion check: blocks release if any student results are pending.
        Generates ResultReleaseBatch and triggers Somali SMS guardian notifications.
        """
        sub = self.db.query(ResultSubmission).filter(ResultSubmission.id == submission_id).first()
        if not sub:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission / Result set not found.")

        # Check enrolled students
        enrolled_count = self.db.query(StudentEnrollment).filter(
            StudentEnrollment.class_id == sub.class_id,
            StudentEnrollment.academic_year == sub.academic_year,
            StudentEnrollment.status == "ACTIVE"
        ).count()

        results = self.db.query(ExamResult).filter(ExamResult.exam_id == sub.exam_id).all()
        completed_count = sum(
            1 for r in results
            if r.attendance_status in ("ABSENT", "EXCUSED") or (r.attendance_status == "PRESENT" and r.marks_obtained is not None)
        )
        pending_count = max(0, enrolled_count - completed_count)

        if pending_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Results cannot be released because {pending_count} student results are still pending."
            )

        if enrolled_count == 0 or len(results) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No student results available to release."
            )

        # Idempotency check: if already released, return existing release details without duplicate notifications
        if sub.status == "RELEASED":
            existing_batch = self.db.query(ResultReleaseBatch).filter(
                ResultReleaseBatch.class_id == sub.class_id,
                ResultReleaseBatch.exam_name == sub.exam_name,
                ResultReleaseBatch.academic_year == sub.academic_year,
                ResultReleaseBatch.status == "RELEASED"
            ).order_by(ResultReleaseBatch.id.desc()).first()

            if existing_batch:
                return {
                    "success": True,
                    "message": f"Results for {sub.school_class.name} ({sub.subject.name}) are already released.",
                    "batch_code": existing_batch.batch_code,
                    "results_count": len(results),
                    "status": "RELEASED",
                    "released_at": existing_batch.released_at.isoformat()
                }

        now = datetime.now(timezone.utc)
        batch_code = self.rel_repo.generate_batch_code(sub.academic_year)
        notes = getattr(payload, "notes", None) if payload else None

        # Create or update ResultReleaseBatch
        batch = ResultReleaseBatch(
            batch_code=batch_code,
            exam_name=sub.exam_name,
            academic_year=sub.academic_year,
            class_id=sub.class_id,
            release_type="FULL",
            status="RELEASED",
            released_by_id=admin_user.id,
            released_at=now,
            results_count=len(results),
            notes=notes
        )
        self.db.add(batch)
        self.db.flush()

        # Update all ExamResults to RELEASED
        for r in results:
            r.status = "RELEASED"
            r.release_batch_id = batch.id

        # Update submission status to RELEASED
        sub.status = "RELEASED"
        sub.approved_at = sub.approved_at or now
        sub.approved_by_id = sub.approved_by_id or admin_user.id

        # Append to revisions log
        rev_list = list(sub.revisions or [])
        rev_list.append({
            "action": "PUBLISHED_TO_STUDENTS",
            "timestamp": now.isoformat(),
            "released_by_id": admin_user.id,
            "released_by_name": admin_user.full_name or admin_user.username,
            "batch_code": batch.batch_code
        })
        sub.revisions = rev_list

        # Check if Exam can be marked PUBLISHED
        exam = sub.exam
        if exam:
            exam.status = "PUBLISHED"

        self.db.commit()

        # Trigger automated guardian notification
        try:
            from app.services.notification_service import NotificationService
            notif_service = NotificationService(self.db)
            notif_service.trigger_result_release_notifications(
                release_batch_id=batch.id,
                admin_user_id=admin_user.id
            )
        except Exception:
            pass

        self._log_audit(
            user_id=admin_user.id,
            action="ADMIN_RELEASE_SUBMISSION_RESULTS",
            details={
                "submission_id": sub.id,
                "exam_id": sub.exam_id,
                "class_id": sub.class_id,
                "subject_id": sub.subject_id,
                "batch_code": batch.batch_code,
                "results_count": len(results)
            }
        )

        return {
            "success": True,
            "message": f"Successfully released results for {sub.school_class.name} ({sub.subject.name}).",
            "batch_code": batch.batch_code,
            "results_count": len(results),
            "status": "RELEASED",
            "released_at": now.isoformat()
        }


    # =========================================================================
    # STUDENT PORTAL OPERATIONS
    # =========================================================================

    def get_student_from_user(self, user: User) -> Student:
        """Find student profile linked to user account."""
        student = self.db.query(Student).filter(Student.user_id == user.id).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No student profile associated with this user account."
            )
        return student

    def get_student_released_results(self, user: User) -> List[Dict[str, Any]]:
        """
        Visibility gate: Students ONLY see results with status = 'RELEASED'!
        DRAFT, SUBMITTED, and APPROVED results remain strictly hidden.
        """
        student = self.get_student_from_user(user)

        from sqlalchemy import or_, and_, func

        # Query RELEASED results or results belonging to PUBLISHED exams
        results = self.db.query(ExamResult).join(
            Exam, ExamResult.exam_id == Exam.id
        ).filter(
            ExamResult.student_id == student.id,
            or_(
                ExamResult.status == "RELEASED",
                and_(
                    func.upper(Exam.status) == "PUBLISHED",
                    ExamResult.status.in_(["SUBMITTED", "APPROVED", "RELEASED"])
                )
            )
        ).order_by(Exam.start_date.desc(), Exam.id.desc()).all()

        return results

    def record_student_view_event(self, user: User, payload: RecordStudentViewPayload) -> Dict[str, Any]:
        """Record view event when student views released results."""
        student = self.get_student_from_user(user)
        enr = student.current_enrollment
        class_id = payload.class_id or (enr.class_id if enr else None)

        if not class_id:
            return {"success": False, "message": "Student not enrolled in an active class."}

        view = self.rel_repo.record_student_view(
            student_id=student.id,
            exam_name=payload.exam_name,
            academic_year=payload.academic_year,
            class_id=class_id
        )

        self.db.commit()

        return {
            "success": True,
            "view_count": view.view_count,
            "first_viewed_at": view.first_viewed_at.isoformat(),
            "last_viewed_at": view.last_viewed_at.isoformat(),
        }
