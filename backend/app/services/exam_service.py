from typing import Optional, List, Tuple, Dict, Any
from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.exam import Exam, ExamResult, ExamDeadlineExtension
from app.models.student_enrollment import StudentEnrollment
from app.models.result_submission import ResultSubmission
from app.models.notification import Notification
from app.models.teacher import Teacher
from app.models.teacher_assignment import TeacherAssignment
from app.repositories.exam_repo import ExamRepository
from app.repositories.class_repo import ClassRepository
from app.repositories.subject_repo import SubjectRepository
from app.repositories.student_repo import StudentRepository
from app.repositories.audit_repo import AuditLogRepository
from app.schemas.exam import (
    ExamCreate,
    ExamBatchCreate,
    ExamUpdate,
    BulkExamResultsCreate,
    PublishResultsPayload,
    ExamConflictCheckRequest,
    ExamConflictCheckResponse,
    ExamConflictItem,
)
from app.core.grading import calculate_grade


class ExamService:
    """Service handling Examination scheduling and Results grading."""

    VALID_STATUS_TRANSITIONS = {
        "DRAFT": ["SCHEDULED", "OPEN_FOR_RESULTS", "CANCELLED"],
        "SCHEDULED": ["OPEN_FOR_RESULTS", "ONGOING", "CLOSED", "CANCELLED", "DRAFT"],
        "OPEN_FOR_RESULTS": ["CLOSED", "COMPLETED", "SCHEDULED", "CANCELLED"],
        "ONGOING": ["OPEN_FOR_RESULTS", "COMPLETED", "CLOSED", "CANCELLED"],
        "COMPLETED": ["PUBLISHED", "OPEN_FOR_RESULTS", "CLOSED"],
        "CLOSED": ["OPEN_FOR_RESULTS", "PUBLISHED", "COMPLETED"],
        "PUBLISHED": ["COMPLETED", "CLOSED"],  # Allow unpublishing
        "CANCELLED": ["DRAFT", "SCHEDULED"],
    }

    def __init__(self, db: Session):
        self.db = db
        self.repo = ExamRepository(db)
        self.class_repo = ClassRepository(db)
        self.subject_repo = SubjectRepository(db)
        self.student_repo = StudentRepository(db)
        self.audit_repo = AuditLogRepository(db)

    def get_summary(self, academic_year: Optional[str] = None) -> Dict[str, Any]:
        return self.repo.get_summary(academic_year)

    def get_filter_options(self) -> Dict[str, Any]:
        return self.repo.get_filter_options()

    def get_exam(self, exam_id: int) -> Exam:
        e = self.repo.get_by_id_enriched(exam_id)
        if not e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found.")
        return e

    def get_exam_profile(self, exam_id: int) -> Dict[str, Any]:
        profile = self.repo.get_exam_profile(exam_id)
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found.")
        return profile

    def search_exams(
        self,
        query: Optional[str] = None,
        class_id: Optional[int] = None,
        subject_id: Optional[int] = None,
        academic_year: Optional[str] = None,
        exam_type: Optional[str] = None,
        status_filter: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Exam], int]:
        return self.repo.search_exams(
            query, class_id, subject_id, academic_year, exam_type, status_filter, skip, limit
        )

    def check_conflicts(self, req: ExamConflictCheckRequest) -> ExamConflictCheckResponse:
        """Check for scheduling conflicts for a class."""
        conflicts_data = self.repo.check_conflicts(
            class_id=req.class_id,
            start_date=req.start_date,
            end_date=req.end_date,
            exclude_exam_id=req.exclude_exam_id
        )
        items = [ExamConflictItem(**c) for c in conflicts_data]
        return ExamConflictCheckResponse(
            has_conflict=len(items) > 0,
            conflicts_count=len(items),
            conflicts=items
        )

    def _notify_teachers(self, exam: Exam, title: str, message: str, admin_user_id: Optional[int] = None):
        """Send notifications to teachers assigned to this exam's class and subject."""
        try:
            teacher_ids = set()
            if exam.teacher_id:
                teacher_ids.add(exam.teacher_id)
            year_clean = exam.academic_year.strip()
            year_alt = year_clean.replace("/", "-") if "/" in year_clean else year_clean.replace("-", "/")
            assigns = self.db.query(TeacherAssignment).filter(
                TeacherAssignment.class_id == exam.class_id,
                TeacherAssignment.subject_id == exam.subject_id,
                TeacherAssignment.academic_year.in_([year_clean, year_alt]),
                TeacherAssignment.status == "ACTIVE"
            ).all()
            if not assigns:
                assigns = self.db.query(TeacherAssignment).filter(
                    TeacherAssignment.class_id == exam.class_id,
                    TeacherAssignment.subject_id == exam.subject_id,
                    TeacherAssignment.status == "ACTIVE"
                ).all()
            for a in assigns:
                if a.teacher_id:
                    teacher_ids.add(a.teacher_id)

            for t_id in teacher_ids:
                teacher = self.db.query(Teacher).filter(Teacher.id == t_id).first()
                if teacher and teacher.user_id:
                    notif = Notification(
                        notification_type="EXAM_DEADLINE",
                        title=title,
                        message=message,
                        channel="IN_APP",
                        status="DELIVERED",
                        class_id=exam.class_id,
                        academic_year=exam.academic_year,
                        related_exam_id=exam.id,
                        created_by_id=admin_user_id,
                        extra_data={
                            "exam_id": exam.id,
                            "exam_name": exam.name,
                            "deadline": exam.result_submission_deadline.isoformat() if exam.result_submission_deadline else None
                        }
                    )
                    self.db.add(notif)
            self.db.commit()
        except Exception:
            pass

    def create_exam(self, data: ExamCreate, user_id: Optional[int] = None) -> Exam:
        if not self.class_repo.get_by_id(data.class_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class not found.")
        if not self.subject_repo.get_by_id(data.subject_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found.")

        if data.end_date and data.start_date and data.end_date < data.start_date:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="End date cannot be before start date."
            )

        if data.max_marks <= 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Maximum marks must be greater than zero."
            )
        if data.pass_marks < 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Pass marks cannot be negative."
            )
        if data.pass_marks > data.max_marks:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Pass marks cannot exceed maximum marks."
            )

        # Duplicate exam prevention: strictly ONE exam per academic_year + class + subject + exam_type
        year_clean = data.academic_year.strip()
        year_alt = year_clean.replace("/", "-") if "/" in year_clean else year_clean.replace("-", "/")
        existing = self.db.query(Exam).filter(
            Exam.academic_year.in_([year_clean, year_alt]),
            Exam.class_id == data.class_id,
            Exam.subject_id == data.subject_id,
            Exam.exam_type == data.exam_type.strip(),
            Exam.status != "CANCELLED"
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"An active examination of type '{data.exam_type}' already exists for this class and subject in academic year {data.academic_year}."
            )

        # Find assigned teacher if not explicitly passed
        assigned_teacher_id = data.teacher_id
        if not assigned_teacher_id:
            assign = self.db.query(TeacherAssignment).filter(
                TeacherAssignment.class_id == data.class_id,
                TeacherAssignment.subject_id == data.subject_id,
                TeacherAssignment.academic_year.in_([year_clean, year_alt]),
                TeacherAssignment.status == "ACTIVE"
            ).first()
            if not assign:
                assign = self.db.query(TeacherAssignment).filter(
                    TeacherAssignment.class_id == data.class_id,
                    TeacherAssignment.subject_id == data.subject_id,
                    TeacherAssignment.status == "ACTIVE"
                ).order_by(TeacherAssignment.id.desc()).first()
            if assign:
                assigned_teacher_id = assign.teacher_id

        exam = Exam(
            name=data.name.strip(),
            exam_type=data.exam_type.strip(),
            academic_year=year_clean,
            class_id=data.class_id,
            subject_id=data.subject_id,
            teacher_id=assigned_teacher_id,
            start_date=data.start_date,
            end_date=data.end_date,
            start_time=data.start_time,
            end_time=data.end_time,
            result_submission_deadline=data.result_submission_deadline,
            instructions=data.instructions,
            max_marks=data.max_marks,
            pass_marks=data.pass_marks,
            status=data.status.upper().strip(),
            created_by_id=user_id
        )
        created = self.repo.create(exam)

        # Count expected students
        enrolled_count = self.db.query(StudentEnrollment).filter(
            StudentEnrollment.class_id == data.class_id,
            StudentEnrollment.academic_year.in_([year_clean, year_alt]),
            StudentEnrollment.status == "ACTIVE"
        ).count()

        # Initialize ResultSubmission in DRAFT
        if assigned_teacher_id:
            sub = ResultSubmission(
                exam_id=created.id,
                class_id=data.class_id,
                subject_id=data.subject_id,
                teacher_id=assigned_teacher_id,
                academic_year=year_clean,
                exam_name=data.name.strip(),
                exam_type=created.exam_type,
                status="DRAFT",
                expected_students=enrolled_count,
                completed_students=0,
                pending_students=enrolled_count,
                submission_deadline=data.result_submission_deadline,
                revisions=[]
            )
            self.db.add(sub)
            self.db.commit()

        self.audit_repo.log_event(
            action="EXAM_CREATED",
            user_id=user_id,
            details={
                "exam_id": created.id,
                "name": created.name,
                "exam_type": created.exam_type,
                "class_id": created.class_id,
                "deadline": str(created.result_submission_deadline)
            }
        )

        if data.result_submission_deadline:
            self._notify_teachers(
                exam=created,
                title=f"New Examination Scheduled: {created.name}",
                message=f"Official {created.exam_type} examination has been scheduled with result submission deadline: {created.result_submission_deadline.strftime('%Y-%m-%d %H:%M')}.",
                admin_user_id=user_id
            )

        return self.repo.get_by_id_enriched(created.id)

    def create_batch_exams(self, data: ExamBatchCreate, user_id: Optional[int] = None) -> List[Exam]:
        """Create multiple exams across classes and subjects in a single atomic transaction."""
        if data.end_date and data.start_date and data.end_date < data.start_date:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="End date cannot be before start date."
            )
        if data.max_marks <= 0 or data.pass_marks < 0 or data.pass_marks > data.max_marks:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid marks configuration."
            )

        year_clean = data.academic_year.strip()
        year_alt = year_clean.replace("/", "-") if "/" in year_clean else year_clean.replace("-", "/")

        created_exams = []
        try:
            for c_id in data.class_ids:
                if not self.class_repo.get_by_id(c_id):
                    continue
                for s_id in data.subject_ids:
                    if not self.subject_repo.get_by_id(s_id):
                        continue

                    # Check duplicate
                    existing = self.db.query(Exam).filter(
                        Exam.academic_year.in_([year_clean, year_alt]),
                        Exam.class_id == c_id,
                        Exam.subject_id == s_id,
                        Exam.exam_type == data.exam_type.strip(),
                        Exam.status != "CANCELLED"
                    ).first()

                    if existing:
                        continue

                    # Find assigned teacher
                    assign = self.db.query(TeacherAssignment).filter(
                        TeacherAssignment.class_id == c_id,
                        TeacherAssignment.subject_id == s_id,
                        TeacherAssignment.academic_year.in_([year_clean, year_alt]),
                        TeacherAssignment.status == "ACTIVE"
                    ).first()
                    if not assign:
                        assign = self.db.query(TeacherAssignment).filter(
                            TeacherAssignment.class_id == c_id,
                            TeacherAssignment.subject_id == s_id,
                            TeacherAssignment.status == "ACTIVE"
                        ).order_by(TeacherAssignment.id.desc()).first()
                    teacher_id = assign.teacher_id if assign else None

                    new_exam = Exam(
                        name=data.name.strip(),
                        exam_type=data.exam_type.strip(),
                        academic_year=year_clean,
                        class_id=c_id,
                        subject_id=s_id,
                        teacher_id=teacher_id,
                        start_date=data.start_date,
                        end_date=data.end_date,
                        start_time=data.start_time,
                        end_time=data.end_time,
                        result_submission_deadline=data.result_submission_deadline,
                        instructions=data.instructions,
                        max_marks=data.max_marks,
                        pass_marks=data.pass_marks,
                        status=data.status.upper().strip(),
                        created_by_id=user_id
                    )
                    self.db.add(new_exam)
                    self.db.flush()

                    enrolled_count = self.db.query(StudentEnrollment).filter(
                        StudentEnrollment.class_id == c_id,
                        StudentEnrollment.academic_year.in_([year_clean, year_alt]),
                        StudentEnrollment.status == "ACTIVE"
                    ).count()

                    if teacher_id:
                        sub = ResultSubmission(
                            exam_id=new_exam.id,
                            class_id=c_id,
                            subject_id=s_id,
                            teacher_id=teacher_id,
                            academic_year=year_clean,
                            exam_name=data.name.strip(),
                            exam_type=new_exam.exam_type,
                            status="DRAFT",
                            expected_students=enrolled_count,
                            completed_students=0,
                            pending_students=enrolled_count,
                            submission_deadline=data.result_submission_deadline,
                            revisions=[]
                        )
                        self.db.add(sub)

                    created_exams.append(new_exam)

            self.db.commit()
            for e in created_exams:
                self.db.refresh(e)
                self.repo._enrich_exam(e)
                self._notify_teachers(
                    exam=e,
                    title=f"New Official Exam Scheduled: {e.name}",
                    message=f"Official {e.exam_type} examination has been scheduled for your subject. Result submission deadline: {e.result_submission_deadline.strftime('%Y-%m-%d %H:%M') if e.result_submission_deadline else 'Standard'}.",
                    admin_user_id=user_id
                )

            self.audit_repo.log_event(
                action="EXAM_BATCH_CREATED",
                user_id=user_id,
                details={"name": data.name, "created_count": len(created_exams)}
            )
            return created_exams
        except HTTPException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to batch create exams: {str(e)}"
            )

    def dispatch_to_teachers(self, exam_id: int, user_id: Optional[int] = None) -> dict:
        """Manually release/route an exam to assigned teachers and notify them."""
        exam = self.repo.get_by_id(exam_id)
        if not exam:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found.")

        year_clean = exam.academic_year.strip()
        year_alt = year_clean.replace("/", "-") if "/" in year_clean else year_clean.replace("-", "/")

        assign = self.db.query(TeacherAssignment).filter(
            TeacherAssignment.class_id == exam.class_id,
            TeacherAssignment.subject_id == exam.subject_id,
            TeacherAssignment.academic_year.in_([year_clean, year_alt]),
            TeacherAssignment.status == "ACTIVE"
        ).first()
        if not assign:
            assign = self.db.query(TeacherAssignment).filter(
                TeacherAssignment.class_id == exam.class_id,
                TeacherAssignment.subject_id == exam.subject_id,
                TeacherAssignment.status == "ACTIVE"
            ).order_by(TeacherAssignment.id.desc()).first()

        assigned_teacher_id = assign.teacher_id if assign else exam.teacher_id
        if assigned_teacher_id and exam.teacher_id != assigned_teacher_id:
            exam.teacher_id = assigned_teacher_id
            self.db.commit()

        # Count expected students
        enrolled_count = self.db.query(StudentEnrollment).filter(
            StudentEnrollment.class_id == exam.class_id,
            StudentEnrollment.academic_year.in_([year_clean, year_alt]),
            StudentEnrollment.status == "ACTIVE"
        ).count()
        if enrolled_count == 0:
            enrolled_count = self.db.query(StudentEnrollment).filter(
                StudentEnrollment.class_id == exam.class_id,
                StudentEnrollment.status == "ACTIVE"
            ).count()

        # Ensure ResultSubmission exists
        sub = self.db.query(ResultSubmission).filter(
            ResultSubmission.exam_id == exam.id,
            ResultSubmission.class_id == exam.class_id,
            ResultSubmission.subject_id == exam.subject_id
        ).first()

        if not sub and assigned_teacher_id:
            sub = ResultSubmission(
                exam_id=exam.id,
                class_id=exam.class_id,
                subject_id=exam.subject_id,
                teacher_id=assigned_teacher_id,
                academic_year=year_clean,
                exam_name=exam.name,
                status="DRAFT",
                expected_students=enrolled_count,
                completed_students=0,
                pending_students=enrolled_count,
                submission_deadline=exam.result_submission_deadline
            )
            self.db.add(sub)
            self.db.commit()
        elif sub:
            if assigned_teacher_id and sub.teacher_id != assigned_teacher_id:
                sub.teacher_id = assigned_teacher_id
            if exam.result_submission_deadline:
                sub.submission_deadline = exam.result_submission_deadline
            if sub.expected_students == 0 and enrolled_count > 0:
                sub.expected_students = enrolled_count
                sub.pending_students = enrolled_count
            self.db.commit()

        # Send in-app notification
        teacher_name = assign.teacher.full_name if (assign and assign.teacher) else "Faculty Teacher"
        self._notify_teachers(
            exam=exam,
            title=f"Examination Released: {exam.name}",
            message=f"Administrator has released the {exam.exam_type} examination for {exam.subject.name if exam.subject else 'your subject'} in {exam.school_class.name if exam.school_class else 'your class'}. You may now record student attendance and enter examination marks.",
            admin_user_id=user_id
        )

        return {
            "success": True,
            "message": f"Examination successfully released to {teacher_name}. Teacher can now enter marks in Teacher Portal.",
            "teacher_id": assigned_teacher_id,
            "teacher_name": teacher_name
        }

    def update_exam(self, exam_id: int, data: ExamUpdate, user_id: Optional[int] = None) -> Exam:
        e = self.get_exam(exam_id)

        if data.class_id is not None:
            if not self.class_repo.get_by_id(data.class_id):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class not found.")
            e.class_id = data.class_id
        if data.subject_id is not None:
            if not self.subject_repo.get_by_id(data.subject_id):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found.")
            e.subject_id = data.subject_id
        if data.name is not None:
            e.name = data.name.strip()
        if data.exam_type is not None:
            e.exam_type = data.exam_type.strip()
        if data.academic_year is not None:
            e.academic_year = data.academic_year.strip()
        if data.start_date is not None:
            e.start_date = data.start_date
        if data.end_date is not None:
            e.end_date = data.end_date
        if data.start_time is not None:
            e.start_time = data.start_time
        if data.end_time is not None:
            e.end_time = data.end_time
        if data.result_submission_deadline is not None:
            e.result_submission_deadline = data.result_submission_deadline
            # update submissions
            subs = self.db.query(ResultSubmission).filter(ResultSubmission.exam_id == e.id).all()
            for s in subs:
                s.submission_deadline = data.result_submission_deadline
        if data.instructions is not None:
            e.instructions = data.instructions
        if data.max_marks is not None:
            if data.max_marks <= 0:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Max marks must be > 0.")
            e.max_marks = data.max_marks
        if data.pass_marks is not None:
            if data.pass_marks < 0 or data.pass_marks > e.max_marks:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid pass marks.")
            e.pass_marks = data.pass_marks
        if data.status is not None:
            new_status = data.status.upper().strip()
            valid_next = self.VALID_STATUS_TRANSITIONS.get(e.status, [])
            if new_status != e.status and new_status not in valid_next:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Invalid status transition: {e.status} -> {new_status}"
                )
            e.status = new_status

        # Validate dates
        if e.end_date and e.start_date and e.end_date < e.start_date:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="End date cannot be before start date."
            )

        updated = self.repo.update(e)
        self.audit_repo.log_event(
            action="EXAM_UPDATED",
            user_id=user_id,
            details={"exam_id": updated.id, "name": updated.name, "status": updated.status}
        )
        return self.repo.get_by_id_enriched(updated.id)

    def extend_deadline(
        self,
        exam_id: int,
        new_deadline: datetime,
        reason: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Exam:
        """Extend the result submission deadline with audit logging and teacher notification."""
        exam = self.get_exam(exam_id)
        prev_deadline = exam.result_submission_deadline

        # Create extension audit record
        ext = ExamDeadlineExtension(
            exam_id=exam.id,
            previous_deadline=prev_deadline,
            new_deadline=new_deadline,
            reason=reason,
            extended_by_id=user_id
        )
        self.db.add(ext)

        exam.result_submission_deadline = new_deadline
        now = datetime.now(timezone.utc)
        dl_utc = new_deadline if new_deadline.tzinfo else new_deadline.replace(tzinfo=timezone.utc)

        # If exam was closed and new deadline is in future, reopen to OPEN_FOR_RESULTS
        if exam.status in ("CLOSED", "SCHEDULED") and dl_utc > now:
            exam.status = "OPEN_FOR_RESULTS"

        # Update submissions deadline
        subs = self.db.query(ResultSubmission).filter(ResultSubmission.exam_id == exam.id).all()
        for s in subs:
            s.submission_deadline = new_deadline

        self.db.commit()
        self.db.refresh(exam)

        self.audit_repo.log_event(
            action="EXAM_DEADLINE_EXTENDED",
            user_id=user_id,
            details={
                "exam_id": exam.id,
                "exam_name": exam.name,
                "previous_deadline": prev_deadline.isoformat() if prev_deadline else None,
                "new_deadline": new_deadline.isoformat(),
                "reason": reason
            }
        )

        self._notify_teachers(
            exam=exam,
            title=f"Submission Deadline Extended: {exam.name}",
            message=f"The result submission deadline for {exam.name} has been extended to {new_deadline.strftime('%Y-%m-%d %H:%M')}. Reason: {reason or 'Administrative extension'}.",
            admin_user_id=user_id
        )

        return self.repo.get_by_id_enriched(exam.id)

    def reopen_submissions(
        self,
        exam_id: int,
        new_deadline: Optional[datetime] = None,
        reason: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Exam:
        """Reopen a closed or passed-deadline examination for mark submission/corrections."""
        exam = self.get_exam(exam_id)
        now = datetime.now(timezone.utc)

        exam.reopened_at = now
        exam.reopened_by_id = user_id
        exam.reopen_reason = reason
        exam.status = "OPEN_FOR_RESULTS"

        if new_deadline:
            prev_dl = exam.result_submission_deadline
            exam.result_submission_deadline = new_deadline
            ext = ExamDeadlineExtension(
                exam_id=exam.id,
                previous_deadline=prev_dl,
                new_deadline=new_deadline,
                reason=f"Reopened examination submissions: {reason or 'General reopening'}",
                extended_by_id=user_id
            )
            self.db.add(ext)

            subs = self.db.query(ResultSubmission).filter(ResultSubmission.exam_id == exam.id).all()
            for s in subs:
                s.submission_deadline = new_deadline

        self.db.commit()
        self.db.refresh(exam)

        self.audit_repo.log_event(
            action="EXAM_SUBMISSIONS_REOPENED",
            user_id=user_id,
            details={
                "exam_id": exam.id,
                "exam_name": exam.name,
                "reopened_at": now.isoformat(),
                "new_deadline": new_deadline.isoformat() if new_deadline else None,
                "reason": reason
            }
        )

        self._notify_teachers(
            exam=exam,
            title=f"Submissions Reopened: {exam.name}",
            message=f"Results submission for {exam.name} has been officially reopened by Administration. Reason: {reason or 'Submissions open for updates'}.",
            admin_user_id=user_id
        )

        return self.repo.get_by_id_enriched(exam.id)

    def update_status(self, exam_id: int, new_status: str, user_id: Optional[int] = None) -> Exam:
        """Admin updates examination status directly."""
        exam = self.get_exam(exam_id)
        st_norm = new_status.upper().strip()
        exam.status = st_norm
        self.db.commit()
        self.db.refresh(exam)

        self.audit_repo.log_event(
            action="EXAM_STATUS_UPDATED",
            user_id=user_id,
            details={"exam_id": exam.id, "new_status": st_norm}
        )
        return self.repo.get_by_id_enriched(exam.id)

    def delete_exam(self, exam_id: int, user_id: Optional[int] = None) -> bool:
        e = self.get_exam(exam_id)
        if e.status == "PUBLISHED":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Cannot delete a published exam. Unpublish first."
            )
        self.audit_repo.log_event(
            action="EXAM_DELETED",
            user_id=user_id,
            details={"exam_id": exam_id, "name": e.name}
        )
        self.repo.delete(e)
        return True

    def save_bulk_results(self, data: BulkExamResultsCreate, recorded_by_user_id: Optional[int] = None) -> List[ExamResult]:
        exam = self.get_exam(data.exam_id)
        subject_id = data.subject_id or exam.subject_id
        saved_results = []
        errors = []

        for entry in data.results:
            if entry.marks_obtained < 0:
                errors.append(f"Student ID {entry.student_id}: Marks cannot be negative ({entry.marks_obtained}).")
                continue
            if entry.marks_obtained > exam.max_marks:
                errors.append(
                    f"Student ID {entry.student_id}: Marks ({entry.marks_obtained}) exceed maximum allowed ({exam.max_marks})."
                )
                continue

            # Verify student enrollment in the exam's class
            enrollment = self.db.query(StudentEnrollment).filter(
                StudentEnrollment.student_id == entry.student_id,
                StudentEnrollment.class_id == exam.class_id,
                StudentEnrollment.academic_year == exam.academic_year,
                StudentEnrollment.status == "ACTIVE"
            ).first()

            if not enrollment:
                errors.append(f"Student ID {entry.student_id} is not actively enrolled in class {exam.class_id} for year {exam.academic_year}.")
                continue

            res = self.repo.upsert_result(
                exam_id=exam.id,
                student_id=entry.student_id,
                subject_id=subject_id,
                marks_obtained=entry.marks_obtained,
                recorded_by_id=recorded_by_user_id,
                custom_remarks=entry.remarks
            )
            saved_results.append(res)

        if errors:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"message": "Validation errors in mark entry. No changes were committed.", "errors": errors}
            )

        self.db.commit()
        # Refresh results with student details
        for r in saved_results:
            self.db.refresh(r)
            if r.student:
                r.student_name = r.student.full_name
                r.student_admission_number = r.student.admission_number

        self.audit_repo.log_event(
            action="EXAM_RESULTS_ENTERED",
            user_id=recorded_by_user_id,
            details={"exam_id": exam.id, "count": len(saved_results)}
        )
        return saved_results

    def publish_results(self, exam_id: int, payload: PublishResultsPayload, user_id: Optional[int] = None) -> Exam:
        e = self.get_exam(exam_id)
        target_status = "PUBLISHED" if payload.publish else "COMPLETED"

        if payload.publish and e.status not in ("COMPLETED", "PUBLISHED"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Cannot publish exam with status '{e.status}'. Exam must be COMPLETED first."
            )
        if not payload.publish and e.status != "PUBLISHED":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Exam is not currently published."
            )

        e.status = target_status
        updated = self.repo.update(e)
        action = "EXAM_RESULTS_PUBLISHED" if payload.publish else "EXAM_RESULTS_UNPUBLISHED"
        self.audit_repo.log_event(
            action=action,
            user_id=user_id,
            details={"exam_id": exam_id, "name": e.name}
        )
        return self.repo.get_by_id_enriched(updated.id)

    def get_exam_results(self, exam_id: int) -> List[ExamResult]:
        return self.repo.get_results_by_exam(exam_id)

    def get_student_report_card(self, exam_id: int, student_id: int) -> Dict[str, Any]:
        report = self.repo.get_student_report_card(exam_id, student_id)
        if not report:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report card not found.")
        return report
