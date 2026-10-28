import os
import uuid
import mimetypes
from decimal import Decimal
from datetime import datetime, date, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status, UploadFile

from app.models.user import User
from app.models.teacher import Teacher
from app.models.teacher_assignment import TeacherAssignment
from app.models.school_class import SchoolClass
from app.models.subject import Subject
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.models.timetable import Timetable
from app.models.exam import Exam, ExamResult
from app.models.attendance import Attendance
from app.models.result_submission import ResultSubmission
from app.models.notification import Notification
from app.models.audit_log import AuditLog
from app.models.system_setting import SystemSetting
from app.core.grading import calculate_grade
from app.repositories.teacher_repo import TeacherRepository
from app.repositories.exam_repo import ExamRepository
from app.schemas.teacher import TeacherAssignmentResponse
from app.schemas.teacher_portal import (
    TeacherDashboardResponse,
    TeacherClassStudentsResponse,
    TeacherTodayAttendanceItem,
    TeacherPendingSubmissionWidget,
    TeacherClassDetailResponse,
    TeacherClassDetailSubject,
    TeacherExamItemResponse,
    TeacherExamRosterResponse,
    TeacherRosterStudentItem,
    TeacherIdentityResponse,
    TeacherPortalProfileResponse,
)
from app.schemas.exam import BulkExamResultsCreate, ExamResponse, ExamCreate
from app.schemas.timetable import TimetableResponse
from app.schemas.student import StudentResponse

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "uploads", "exam_papers")
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/jpg", "application/pdf"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


class TeacherPortalService:
    """Service handling isolated operations for authenticated teachers."""

    def __init__(self, db: Session):
        self.db = db
        self.teacher_repo = TeacherRepository(db)
        self.exam_repo = ExamRepository(db)
        os.makedirs(UPLOAD_DIR, exist_ok=True)

    def get_authenticated_teacher(self, user: User) -> Teacher:
        teacher = self.teacher_repo.get_by_user_id(user.id)
        if not teacher and user.email:
            # Safe fallback: match by email and establish link
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

    def get_teacher_me(self, user: User) -> TeacherIdentityResponse:
        teacher = self.get_authenticated_teacher(user)
        return TeacherIdentityResponse(
            user_id=user.id,
            teacher_id=teacher.id,
            teacher_number=teacher.teacher_number,
            name=teacher.full_name,
            email=teacher.email,
            role="TEACHER",
            status=teacher.status
        )

    def get_profile(self, user: User) -> TeacherPortalProfileResponse:
        teacher = self.get_authenticated_teacher(user)
        assignments = self.get_my_classes(user)
        return TeacherPortalProfileResponse(
            id=teacher.id,
            teacher_number=teacher.teacher_number,
            first_name=teacher.first_name,
            middle_name=teacher.middle_name,
            last_name=teacher.last_name,
            gender=teacher.gender,
            email=teacher.email,
            phone=teacher.phone,
            address=teacher.address,
            qualification=teacher.qualification,
            hire_date=teacher.hire_date,
            status=teacher.status,
            full_name=teacher.full_name,
            user_id=teacher.user_id,
            assignments=assignments
        )

    def get_teacher_subjects(self, user: User, academic_year: Optional[str] = None) -> List[Dict[str, Any]]:
        teacher = self.get_authenticated_teacher(user)
        q = self.db.query(TeacherAssignment).filter(
            TeacherAssignment.teacher_id == teacher.id,
            TeacherAssignment.status == "ACTIVE"
        )
        if academic_year and academic_year.upper() != "ALL":
            y = academic_year.strip()
            q = q.filter(TeacherAssignment.academic_year.in_([y, y.replace("/", "-"), y.replace("-", "/")]))
        assignments = q.all()

        seen = set()
        subjects = []
        for a in assignments:
            if a.subject_id not in seen and a.subject and a.subject.status == "ACTIVE":
                seen.add(a.subject_id)
                subjects.append({
                    "id": a.subject.id,
                    "name": a.subject.name,
                    "code": a.subject.code,
                    "department": a.subject.department,
                    "division": a.subject.division,
                    "status": a.subject.status
                })
        subjects.sort(key=lambda s: s["name"])
        return subjects

    def get_dashboard(self, user: User) -> TeacherDashboardResponse:
        teacher = self.get_authenticated_teacher(user)
        assignments = self.teacher_repo.get_teacher_assignments(teacher.id)

        class_ids = list(set(a.class_id for a in assignments))
        subject_ids = list(set(a.subject_id for a in assignments))

        # Total distinct students in assigned classes
        total_students = self.db.query(StudentEnrollment).filter(
            StudentEnrollment.class_id.in_(class_ids) if class_ids else False,
            StudentEnrollment.status == "ACTIVE"
        ).distinct(StudentEnrollment.student_id).count() if class_ids else 0

        # Today's timetable
        today_name = datetime.now().strftime("%A")
        timetables = self.db.query(Timetable).filter(
            Timetable.teacher_id == teacher.id,
            Timetable.status == "ACTIVE"
        ).order_by(Timetable.start_time.asc()).all()

        today_classes = [t for t in timetables if t.day_of_week.lower() == today_name.lower()]

        # Active exams in assigned classes
        exams = self.db.query(Exam).filter(
            Exam.class_id.in_(class_ids) if class_ids else False,
            Exam.subject_id.in_(subject_ids) if subject_ids else False,
            Exam.status.in_(["SCHEDULED", "ONGOING"])
        ).all() if (class_ids and subject_ids) else []

        # Today's Attendance Tracking
        today = date.today()
        today_attendance_summary: List[TeacherTodayAttendanceItem] = []
        for a in assignments:
            tot_enrolled = self.db.query(StudentEnrollment).filter(
                StudentEnrollment.class_id == a.class_id,
                StudentEnrollment.status == "ACTIVE"
            ).count()

            att_records = self.db.query(Attendance).filter(
                Attendance.class_id == a.class_id,
                Attendance.subject_id == a.subject_id,
                Attendance.date == today
            ).all()

            is_rec = len(att_records) > 0
            pres = sum(1 for r in att_records if r.status in ["PRESENT", "LATE"])
            absc = sum(1 for r in att_records if r.status in ["ABSENT", "EXCUSED"])

            today_attendance_summary.append(
                TeacherTodayAttendanceItem(
                    class_id=a.class_id,
                    class_name=a.school_class.name,
                    subject_id=a.subject_id,
                    subject_name=a.subject.name,
                    period=None,
                    is_recorded=is_rec,
                    total_students=tot_enrolled,
                    present_count=pres,
                    absent_count=absc
                )
            )

        # Pending Result Submissions Widget
        pending_submissions: List[TeacherPendingSubmissionWidget] = []
        if class_ids and subject_ids:
            all_exams = self.db.query(Exam).filter(
                Exam.class_id.in_(class_ids),
                Exam.subject_id.in_(subject_ids)
            ).all()

            for ex in all_exams:
                sub = self.db.query(ResultSubmission).filter(
                    ResultSubmission.exam_id == ex.id,
                    ResultSubmission.class_id == ex.class_id,
                    ResultSubmission.subject_id == ex.subject_id,
                    ResultSubmission.teacher_id == teacher.id
                ).first()

                tot_enr = self.db.query(StudentEnrollment).filter(
                    StudentEnrollment.class_id == ex.class_id,
                    StudentEnrollment.status == "ACTIVE"
                ).count()

                completed_results = self.db.query(ExamResult).filter(
                    ExamResult.exam_id == ex.id,
                    ExamResult.class_id == ex.class_id,
                    ExamResult.subject_id == ex.subject_id
                ).filter(
                    (ExamResult.marks_obtained.isnot(None)) | (ExamResult.attendance_status.in_(["ABSENT", "EXCUSED"]))
                ).count()

                sub_status = sub.status if sub else ("DRAFT" if completed_results > 0 else "PENDING")
                pending_count = max(0, tot_enr - completed_results)

                pending_submissions.append(
                    TeacherPendingSubmissionWidget(
                        exam_id=ex.id,
                        exam_name=ex.name,
                        class_id=ex.class_id,
                        class_name=ex.school_class.name if ex.school_class else "",
                        subject_id=ex.subject_id,
                        subject_name=ex.subject.name if ex.subject else "",
                        academic_year=ex.academic_year,
                        status=sub_status,
                        total_students=tot_enr,
                        completed_students=completed_results,
                        pending_students=pending_count
                    )
                )

        pending_results_count = sum(1 for p in pending_submissions if p.status in ["DRAFT", "PENDING", "PARTIAL", "RETURNED"])

        teacher.has_portal_access = True

        return TeacherDashboardResponse(
            teacher=teacher,
            total_classes=len(class_ids),
            total_subjects=len(subject_ids),
            total_students=total_students,
            today_classes_count=len(today_classes),
            pending_results_count=pending_results_count,
            today_attendance_summary=today_attendance_summary,
            pending_submissions=pending_submissions,
            assigned_classes=assignments,
            upcoming_timetables=timetables,
            active_exams=exams
        )

    def get_my_classes(self, user: User, academic_year: Optional[str] = None) -> List[TeacherAssignmentResponse]:
        teacher = self.get_authenticated_teacher(user)

        # Retrieve current active academic year from system settings
        setting = self.db.query(SystemSetting).filter(SystemSetting.key == "academic_year_current").first()
        current_year = setting.value.strip() if setting else "2025-2026"

        query = self.db.query(TeacherAssignment).filter(
            TeacherAssignment.teacher_id == teacher.id,
            TeacherAssignment.status == "ACTIVE"
        )

        if academic_year and academic_year.upper() != "ALL":
            norm_year = academic_year.strip()
            query = query.filter(
                (TeacherAssignment.academic_year == norm_year) |
                (TeacherAssignment.academic_year == norm_year.replace("-", "/")) |
                (TeacherAssignment.academic_year == norm_year.replace("/", "-"))
            )

        assignments = query.order_by(
            TeacherAssignment.academic_year.desc(),
            TeacherAssignment.class_id.asc(),
            TeacherAssignment.subject_id.asc()
        ).all()

        results: List[TeacherAssignmentResponse] = []
        seen_keys = set()

        for a in assignments:
            if not a.school_class or a.school_class.status != "ACTIVE":
                continue
            if not a.subject or a.subject.status != "ACTIVE":
                continue
            # Prevent duplicate assignment cards for the exact same unique stream
            key = (a.teacher_id, a.class_id, a.subject_id, a.academic_year)
            if key in seen_keys:
                continue
            seen_keys.add(key)

            # Count enrolled students strictly in this assigned class for this academic year
            student_count = self.db.query(StudentEnrollment).filter(
                StudentEnrollment.class_id == a.class_id,
                StudentEnrollment.status == "ACTIVE"
            ).filter(
                (StudentEnrollment.academic_year == a.academic_year) |
                (StudentEnrollment.academic_year == a.academic_year.replace("-", "/")) |
                (StudentEnrollment.academic_year == a.academic_year.replace("/", "-"))
            ).count()

            # Fallback to total active students in class if academic year string format differs
            if student_count == 0:
                student_count = self.db.query(StudentEnrollment).filter(
                    StudentEnrollment.class_id == a.class_id,
                    StudentEnrollment.status == "ACTIVE"
                ).count()

            # Determine assignment status (ACTIVE vs HISTORICAL vs INACTIVE)
            if a.status != "ACTIVE":
                display_status = "INACTIVE"
                is_current = False
            elif (
                a.academic_year == current_year or
                a.academic_year.replace("/", "-") == current_year.replace("/", "-") or
                a.academic_year.replace("-", "/") == current_year.replace("-", "/")
            ):
                display_status = "ACTIVE"
                is_current = True
            else:
                display_status = "HISTORICAL"
                is_current = False

            class_name = a.school_class.name if a.school_class else f"Class {a.class_id}"
            class_code = a.school_class.code if a.school_class else ""
            section = a.school_class.section if a.school_class else None
            subject_name = a.subject.name if a.subject else f"Subject {a.subject_id}"
            subject_code = a.subject.code if (a.subject and a.subject.code) else None
            department = a.subject.department if a.subject else None

            results.append(
                TeacherAssignmentResponse(
                    id=a.id,
                    teacher_id=a.teacher_id,
                    class_id=a.class_id,
                    subject_id=a.subject_id,
                    academic_year=a.academic_year,
                    status=a.status,
                    teacher_name=teacher.full_name,
                    teacher_number=teacher.teacher_number,
                    class_name=class_name,
                    class_code=class_code,
                    section=section,
                    subject_name=subject_name,
                    subject_code=subject_code,
                    department=department,
                    student_count=student_count,
                    is_current_academic_year=is_current,
                    display_status=display_status,
                    school_class=a.school_class,
                    subject=a.subject,
                    created_at=a.created_at
                )
            )

        return results

    def get_class_detail(
        self,
        user: User,
        class_id: int,
        subject_id: Optional[int] = None
    ) -> TeacherClassDetailResponse:
        teacher = self.get_authenticated_teacher(user)

        query = self.db.query(TeacherAssignment).filter(
            TeacherAssignment.teacher_id == teacher.id,
            TeacherAssignment.class_id == class_id
        )
        if subject_id:
            query = query.filter(TeacherAssignment.subject_id == subject_id)

        assignments = query.all()

        if not assignments:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to view details for this class."
            )

        school_class = assignments[0].school_class
        if not school_class:
            school_class = self.db.query(SchoolClass).filter(SchoolClass.id == class_id).first()

        academic_years = list(set(a.academic_year for a in assignments))

        # Enrolled active students strictly in this class and academic year
        stmt = self.db.query(Student).join(
            StudentEnrollment,
            StudentEnrollment.student_id == Student.id
        ).filter(
            StudentEnrollment.class_id == class_id,
            StudentEnrollment.status == "ACTIVE",
            Student.status == "ACTIVE"
        )

        if academic_years:
            year_patterns = []
            for y in academic_years:
                year_patterns.extend([y, y.replace("-", "/"), y.replace("/", "-")])
            stmt = stmt.filter(StudentEnrollment.academic_year.in_(set(year_patterns)))

        students = stmt.order_by(Student.first_name.asc(), Student.last_name.asc()).distinct().all()

        if not students:
            students = self.db.query(Student).join(
                StudentEnrollment,
                StudentEnrollment.student_id == Student.id
            ).filter(
                StudentEnrollment.class_id == class_id,
                StudentEnrollment.status == "ACTIVE",
                Student.status == "ACTIVE"
            ).order_by(Student.first_name.asc(), Student.last_name.asc()).distinct().all()

        for s in students:
            s.has_portal_access = s.user_id is not None

        # Subjects taught by teacher in this class
        my_subjects = [
            TeacherClassDetailSubject(
                id=a.subject_id,
                name=a.subject.name if a.subject else f"Subject {a.subject_id}",
                code=a.subject.code if (a.subject and a.subject.code) else "Not assigned"
            )
            for a in assignments if a.subject
        ]

        # Teacher's timetable for this class
        timetables = self.db.query(Timetable).filter(
            Timetable.teacher_id == teacher.id,
            Timetable.class_id == class_id,
            Timetable.status == "ACTIVE"
        ).order_by(Timetable.day_of_week.asc(), Timetable.start_time.asc()).all()

        # Exams for teacher's subjects in this class
        subject_ids = [a.subject_id for a in assignments]
        exams = self.db.query(Exam).filter(
            Exam.class_id == class_id,
            Exam.subject_id.in_(subject_ids)
        ).order_by(Exam.start_date.desc()).all() if subject_ids else []

        # Overall class attendance rate
        total_att = self.db.query(Attendance).filter(
            Attendance.class_id == class_id,
            Attendance.subject_id.in_(subject_ids)
        ).count() if subject_ids else 0

        present_att = self.db.query(Attendance).filter(
            Attendance.class_id == class_id,
            Attendance.subject_id.in_(subject_ids),
            Attendance.status.in_(["PRESENT", "LATE"])
        ).count() if subject_ids else 0

        att_rate = round((present_att / total_att * 100), 1) if total_att > 0 else 100.0

        return TeacherClassDetailResponse(
            class_id=class_id,
            name=school_class.name if school_class else f"Class {class_id}",
            code=school_class.code if school_class else "",
            section=school_class.section if school_class else None,
            academic_year=assignments[0].academic_year,
            capacity=school_class.capacity if school_class else 40,
            enrolled_students_count=len(students),
            my_subjects=my_subjects,
            students=students,
            timetables=timetables,
            exams=exams,
            attendance_rate=att_rate
        )

    def get_my_timetable(self, user: User) -> List[TimetableResponse]:
        teacher = self.get_authenticated_teacher(user)
        day_order = {
            "Saturday": 1, "Sunday": 2, "Monday": 3, "Tuesday": 4,
            "Wednesday": 5, "Thursday": 6, "Friday": 7
        }
        slots = self.db.query(Timetable).filter(
            Timetable.teacher_id == teacher.id,
            Timetable.status.in_(["ACTIVE", "PUBLISHED"])
        ).all()
        sorted_slots = sorted(slots, key=lambda s: (day_order.get(s.day_of_week, 8), s.start_time))
        
        results = []
        for s in sorted_slots:
            results.append(TimetableResponse(
                id=s.id,
                class_id=s.class_id,
                subject_id=s.subject_id,
                teacher_id=s.teacher_id,
                academic_year=s.academic_year,
                day_of_week=s.day_of_week,
                start_time=s.start_time,
                end_time=s.end_time,
                room=s.room,
                period_number=s.period_number,
                is_break=s.is_break if s.is_break is not None else False,
                status=s.status,
                published_at=s.published_at,
                published_by_id=s.published_by_id,
                class_name=s.school_class.name if s.school_class else f"Class {s.class_id}",
                class_code=s.school_class.code if s.school_class else "",
                subject_name=s.subject.name if s.subject else f"Subject {s.subject_id}",
                subject_code=s.subject.code if s.subject else "",
                teacher_name=teacher.full_name,
                room_number=s.room,
                created_at=s.created_at,
                updated_at=s.updated_at
            ))
        return results

    def get_students_in_class(self, user: User, class_id: int) -> TeacherClassStudentsResponse:
        teacher = self.get_authenticated_teacher(user)

        # Enforce that teacher is assigned to this class
        is_assigned = self.db.query(TeacherAssignment).filter(
            TeacherAssignment.teacher_id == teacher.id,
            TeacherAssignment.class_id == class_id,
            TeacherAssignment.status == "ACTIVE"
        ).first()

        if not is_assigned:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to view students in a class you are not assigned to."
            )

        students = self.db.query(Student).join(StudentEnrollment).filter(
            StudentEnrollment.class_id == class_id,
            StudentEnrollment.status == "ACTIVE",
            Student.status == "ACTIVE"
        ).order_by(Student.first_name.asc()).all()

        for s in students:
            s.has_portal_access = s.user_id is not None

        c = is_assigned.school_class
        return TeacherClassStudentsResponse(
            class_id=c.id,
            class_name=c.name,
            class_code=c.code,
            academic_year=c.academic_year,
            students=students
        )

    def create_exam(self, user: User, data: ExamCreate) -> Exam:
        teacher = self.get_authenticated_teacher(user)

        # Verify active TeacherAssignment for class_id, subject_id, academic_year
        year_clean = data.academic_year.strip()
        year_alt = year_clean.replace("/", "-") if "/" in year_clean else year_clean.replace("-", "/")

        assignment = self.db.query(TeacherAssignment).filter(
            TeacherAssignment.teacher_id == teacher.id,
            TeacherAssignment.class_id == data.class_id,
            TeacherAssignment.subject_id == data.subject_id,
            TeacherAssignment.academic_year.in_([year_clean, year_alt]),
            TeacherAssignment.status == "ACTIVE"
        ).first()

        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Teacher is not assigned to this subject and class for the selected academic year."
            )

        if data.pass_marks > data.max_marks:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Pass marks cannot be greater than maximum marks."
            )

        # Validate and normalize exam type
        norm_type = data.exam_type.upper().strip()
        from app.schemas.exam import EXAM_TYPE_NORMALIZATION, ALLOWED_EXAM_TYPES
        canonical_type = EXAM_TYPE_NORMALIZATION.get(norm_type)
        if not canonical_type or canonical_type not in ALLOWED_EXAM_TYPES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid exam type '{data.exam_type}'. Allowed exam types are strictly: Mid-Term (MID_TERM), Final (FINAL), Monthly (MONTHLY), Quiz (QUIZ)."
            )

        # Requirement 1 & 7: Official exams (Final, Midterm, Monthly) are created ONLY by School Administrators
        if canonical_type != "QUIZ":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Teachers are only permitted to create Quiz examinations. Final, Midterm, and Monthly examinations are official examinations scheduled exclusively by School Administrators."
            )

        # Check duplicate exam prevention: strictly ONE exam per academic_year + class + subject + exam_type
        existing = self.db.query(Exam).filter(
            Exam.academic_year.in_([year_clean, year_alt]),
            Exam.class_id == data.class_id,
            Exam.subject_id == data.subject_id,
            Exam.exam_type == canonical_type
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"An active examination of type '{canonical_type}' already exists for this class and subject in academic year {data.academic_year}."
            )

        # Create Exam
        new_exam = Exam(
            name=data.name.strip(),
            exam_type=canonical_type,
            academic_year=data.academic_year.strip(),
            class_id=data.class_id,
            subject_id=data.subject_id,
            teacher_id=teacher.id,
            start_date=data.start_date,
            end_date=data.end_date,
            max_marks=data.max_marks,
            pass_marks=data.pass_marks,
            instructions=data.instructions,
            status="SCHEDULED"
        )
        self.db.add(new_exam)
        self.db.flush()

        # Count expected enrolled students in this class and academic year
        enrolled_count = self.db.query(StudentEnrollment).filter(
            StudentEnrollment.class_id == data.class_id,
            StudentEnrollment.academic_year.in_([year_clean, year_alt]),
            StudentEnrollment.status == "ACTIVE"
        ).count()

        # Initialize ResultSubmission in DRAFT status
        sub = ResultSubmission(
            exam_id=new_exam.id,
            class_id=data.class_id,
            subject_id=data.subject_id,
            teacher_id=teacher.id,
            academic_year=data.academic_year.strip(),
            exam_name=data.name.strip(),
            status="DRAFT",
            expected_students=enrolled_count,
            completed_students=0,
            pending_students=enrolled_count
        )
        self.db.add(sub)
        self.db.commit()
        self.db.refresh(new_exam)

        # Log audit event
        try:
            log = AuditLog(
                user_id=user.id,
                action="TEACHER_CREATED_EXAM",
                status="SUCCESS",
                details={
                    "exam_id": new_exam.id,
                    "exam_name": new_exam.name,
                    "class_id": new_exam.class_id,
                    "subject_id": new_exam.subject_id,
                    "teacher_id": teacher.id,
                    "academic_year": new_exam.academic_year
                }
            )
            self.db.add(log)
            self.db.commit()
        except Exception:
            pass

        return new_exam

    def get_my_exams(
        self,
        user: User,
        academic_year: Optional[str] = None,
        class_id: Optional[int] = None,
        subject_id: Optional[int] = None,
        exam_type: Optional[str] = None,
        status_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        teacher = self.get_authenticated_teacher(user)

        # Teacher sees exams created by them OR official exams for classes/subjects they are assigned to
        assignments = self.db.query(TeacherAssignment).filter(
            TeacherAssignment.teacher_id == teacher.id,
            TeacherAssignment.status == "ACTIVE"
        ).all()

        assigned_pairs = set((a.class_id, a.subject_id) for a in assignments)

        from sqlalchemy import or_, and_
        clauses = [Exam.teacher_id == teacher.id]
        for (cid, sid) in assigned_pairs:
            clauses.append(and_(Exam.class_id == cid, Exam.subject_id == sid))

        q = self.db.query(Exam).filter(or_(*clauses))

        if academic_year and academic_year.strip():
            y = academic_year.strip()
            q = q.filter(Exam.academic_year.in_([y, y.replace("/", "-"), y.replace("-", "/")]))

        if class_id:
            q = q.filter(Exam.class_id == class_id)

        if subject_id:
            q = q.filter(Exam.subject_id == subject_id)

        if exam_type and exam_type.strip():
            q = q.filter(Exam.exam_type.ilike(f"%{exam_type.strip()}%"))

        exams = q.order_by(Exam.start_date.desc(), Exam.id.desc()).all()

        now_utc = datetime.now(timezone.utc)
        results = []
        for e in exams:
            # Expected enrolled students
            y = e.academic_year
            enrolled = self.db.query(StudentEnrollment).filter(
                StudentEnrollment.class_id == e.class_id,
                StudentEnrollment.academic_year.in_([y, y.replace("/", "-"), y.replace("-", "/")]),
                StudentEnrollment.status == "ACTIVE"
            ).count()

            # Result count
            results_entered = self.db.query(ExamResult).filter(ExamResult.exam_id == e.id).all()
            completed_count = len(results_entered)
            pending_count = max(0, enrolled - completed_count)

            # Check submission
            sub = self.db.query(ResultSubmission).filter(
                ResultSubmission.exam_id == e.id,
                ResultSubmission.class_id == e.class_id,
                ResultSubmission.subject_id == e.subject_id
            ).first()

            if sub:
                sub_status = sub.status
                return_reason = sub.return_reason
                is_locked = sub.status in ("SUBMITTED", "UNDER_REVIEW", "APPROVED", "RELEASED")
                submitted_at_str = sub.submitted_at.isoformat() if sub.submitted_at else None
                sub_id = sub.id
            else:
                if completed_count >= enrolled and enrolled > 0:
                    sub_status = "RESULTS_IN_PROGRESS"
                elif completed_count > 0:
                    sub_status = "RESULTS_IN_PROGRESS"
                else:
                    sub_status = "DRAFT"
                return_reason = None
                is_locked = False
                submitted_at_str = None
                sub_id = None

            # Calculate deadline status and countdown
            is_overdue = False
            deadline_status = "ON_TRACK"
            remaining_time_human = None

            if e.result_submission_deadline:
                dl = e.result_submission_deadline
                if dl.tzinfo is None:
                    dl = dl.replace(tzinfo=timezone.utc)
                diff = (dl - now_utc).total_seconds()
                if diff < 0:
                    if sub_status not in ("SUBMITTED", "APPROVED", "RELEASED"):
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

            if e.status == "CLOSED":
                deadline_status = "CLOSED"

            if status_filter and status_filter.strip():
                sf = status_filter.upper().strip()
                if sf == "DRAFT" and sub_status not in ("DRAFT", "RESULTS_IN_PROGRESS"):
                    continue
                elif sf == "SUBMITTED" and sub_status != "SUBMITTED":
                    continue
                elif sf == "RELEASED" and sub_status != "RELEASED":
                    continue
                elif sf == "RETURNED" and "RETURN" not in sub_status:
                    continue
                elif sf == "OVERDUE" and not is_overdue:
                    continue

            results.append({
                "id": e.id,
                "name": e.name,
                "exam_type": e.exam_type,
                "academic_year": e.academic_year,
                "class_id": e.class_id,
                "class_name": e.school_class.name if e.school_class else f"Class {e.class_id}",
                "class_code": e.school_class.code if e.school_class else "",
                "subject_id": e.subject_id,
                "subject_name": e.subject.name if e.subject else f"Subject {e.subject_id}",
                "subject_code": e.subject.code if e.subject else "",
                "start_date": e.start_date,
                "end_date": e.end_date,
                "start_time": e.start_time,
                "end_time": e.end_time,
                "result_submission_deadline": e.result_submission_deadline,
                "deadline_status": deadline_status,
                "is_overdue": is_overdue,
                "remaining_time_human": remaining_time_human,
                "max_marks": float(e.max_marks),
                "pass_marks": float(e.pass_marks),
                "instructions": e.instructions,
                "status": e.status,
                "submission_id": sub_id,
                "submission_status": sub_status,
                "expected_students": enrolled,
                "completed_students": completed_count,
                "pending_students": pending_count,
                "return_reason": return_reason,
                "is_locked": is_locked,
                "submitted_at": submitted_at_str
            })

        return results

    def get_exam_roster(self, user: User, exam_id: int) -> Dict[str, Any]:
        teacher = self.get_authenticated_teacher(user)
        exam = self.db.query(Exam).filter(Exam.id == exam_id).first()
        if not exam:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found.")

        # Verify teacher assignment
        y = exam.academic_year
        assignment = self.db.query(TeacherAssignment).filter(
            TeacherAssignment.teacher_id == teacher.id,
            TeacherAssignment.class_id == exam.class_id,
            TeacherAssignment.subject_id == exam.subject_id,
            TeacherAssignment.academic_year.in_([y, y.replace("/", "-"), y.replace("-", "/")]),
            TeacherAssignment.status == "ACTIVE"
        ).first()

        if not assignment and not user.has_role("ADMIN"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to view results for an exam outside your assigned classes."
            )

        # Enrolled students
        enrollments = self.db.query(StudentEnrollment).filter(
            StudentEnrollment.class_id == exam.class_id,
            StudentEnrollment.academic_year.in_([y, y.replace("/", "-"), y.replace("-", "/")]),
            StudentEnrollment.status == "ACTIVE"
        ).all()

        if not enrollments:
            enrollments = self.db.query(StudentEnrollment).filter(
                StudentEnrollment.class_id == exam.class_id,
                StudentEnrollment.status == "ACTIVE"
            ).all()

        # Existing results
        existing_results = self.db.query(ExamResult).filter(ExamResult.exam_id == exam_id).all()
        res_by_student = {r.student_id: r for r in existing_results}

        # Submission status
        sub = self.db.query(ResultSubmission).filter(
            ResultSubmission.exam_id == exam.id,
            ResultSubmission.class_id == exam.class_id,
            ResultSubmission.subject_id == exam.subject_id,
            ResultSubmission.teacher_id == teacher.id
        ).first()

        sub_status = sub.status if sub else "DRAFT"
        is_locked = sub is not None and sub.status in ("SUBMITTED", "UNDER_REVIEW", "APPROVED", "RELEASED")
        return_reason = sub.return_reason if sub else None

        students_data = []
        for en in enrollments:
            s = en.student
            if not s:
                continue
            res = res_by_student.get(s.id)
            students_data.append({
                "student_id": s.id,
                "admission_number": s.admission_number,
                "student_name": f"{s.first_name} {s.last_name}".strip(),
                "gender": s.gender,
                "attendance_status": res.attendance_status if res else "PRESENT",
                "marks_obtained": float(res.marks_obtained) if (res and res.marks_obtained is not None) else None,
                "grade": res.grade if res else None,
                "remarks": res.remarks if res else None,
                "paper_file_path": res.paper_file_path if res else None,
                "paper_original_name": res.paper_original_name if res else None,
                "paper_mime_type": res.paper_mime_type if res else None,
                "paper_uploaded_at": res.paper_uploaded_at.isoformat() if (res and res.paper_uploaded_at) else None
            })

        # Calculate deadline status and countdown
        now_utc = datetime.now(timezone.utc)
        is_overdue = False
        deadline_status = "ON_TRACK"
        remaining_time_human = None

        if exam.result_submission_deadline:
            dl = exam.result_submission_deadline
            if dl.tzinfo is None:
                dl = dl.replace(tzinfo=timezone.utc)
            diff = (dl - now_utc).total_seconds()
            if diff < 0:
                if sub_status not in ("SUBMITTED", "APPROVED", "RELEASED"):
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

        return {
            "exam_id": exam.id,
            "exam_name": exam.name,
            "exam_type": exam.exam_type,
            "academic_year": exam.academic_year,
            "class_id": exam.class_id,
            "class_name": exam.school_class.name if exam.school_class else f"Class {exam.class_id}",
            "subject_id": exam.subject_id,
            "subject_name": exam.subject.name if exam.subject else f"Subject {exam.subject_id}",
            "start_date": exam.start_date,
            "end_date": exam.end_date,
            "start_time": exam.start_time,
            "end_time": exam.end_time,
            "result_submission_deadline": exam.result_submission_deadline,
            "deadline_status": deadline_status,
            "is_overdue": is_overdue,
            "remaining_time_human": remaining_time_human,
            "instructions": exam.instructions,
            "max_marks": float(exam.max_marks),
            "pass_marks": float(exam.pass_marks),
            "submission_id": sub.id if sub else None,
            "submission_status": sub_status,
            "is_locked": is_locked,
            "return_reason": return_reason,
            "students": students_data
        }

    def save_draft_results(self, user: User, exam_id: int, results_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        teacher = self.get_authenticated_teacher(user)
        exam = self.db.query(Exam).filter(Exam.id == exam_id).first()
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
        y = exam.academic_year
        assignment = self.db.query(TeacherAssignment).filter(
            TeacherAssignment.teacher_id == teacher.id,
            TeacherAssignment.class_id == exam.class_id,
            TeacherAssignment.subject_id == exam.subject_id,
            TeacherAssignment.academic_year.in_([y, y.replace("/", "-"), y.replace("-", "/")]),
            TeacherAssignment.status == "ACTIVE"
        ).first()

        if not assignment and not user.has_role("ADMIN"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to edit results for an exam outside your assigned class and subject."
            )

        sub = self.db.query(ResultSubmission).filter(
            ResultSubmission.exam_id == exam.id,
            ResultSubmission.class_id == exam.class_id,
            ResultSubmission.subject_id == exam.subject_id,
            ResultSubmission.teacher_id == teacher.id
        ).first()

        if sub and sub.status in ("SUBMITTED", "UNDER_REVIEW", "APPROVED", "RELEASED"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot save draft. Results are currently locked with status '{sub.status}'."
            )

        for item in results_list:
            s_id = item.get("student_id")
            att = (item.get("attendance_status") or "PRESENT").upper().strip()
            raw_marks = item.get("marks_obtained")
            rem = item.get("remarks")

            marks = None
            grade_val = None

            if att == "PRESENT":
                if raw_marks is not None and raw_marks != "":
                    try:
                        m_dec = Decimal(str(raw_marks))
                    except Exception:
                        raise HTTPException(
                            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=f"Invalid mark value '{raw_marks}' for student #{s_id}."
                        )
                    if m_dec < 0 or m_dec > exam.max_marks:
                        raise HTTPException(
                            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=f"Marks ({m_dec}) for student #{s_id} must be between 0 and {exam.max_marks}."
                        )
                    marks = m_dec
                    grade_val, auto_remark, _ = calculate_grade(marks, exam.max_marks)
                    if not rem:
                        rem = auto_remark
            elif att in ("ABSENT", "EXCUSED"):
                marks = None
                grade_val = att
                if not rem:
                    rem = f"Student was {att.lower()}"

            # Upsert ExamResult
            existing_res = self.db.query(ExamResult).filter(
                ExamResult.exam_id == exam_id,
                ExamResult.student_id == s_id,
                ExamResult.subject_id == exam.subject_id
            ).first()

            if not existing_res:
                existing_res = ExamResult(
                    exam_id=exam_id,
                    class_id=exam.class_id,
                    student_id=s_id,
                    subject_id=exam.subject_id,
                    attendance_status=att,
                    marks_obtained=marks,
                    grade=grade_val,
                    remarks=rem,
                    status="DRAFT",
                    recorded_by_id=user.id
                )
                self.db.add(existing_res)
            else:
                existing_res.attendance_status = att
                existing_res.marks_obtained = marks
                existing_res.grade = grade_val
                existing_res.remarks = rem
                existing_res.status = "DRAFT"
                existing_res.recorded_by_id = user.id

        # Update or create submission status
        enrolled_count = self.db.query(StudentEnrollment).filter(
            StudentEnrollment.class_id == exam.class_id,
            StudentEnrollment.academic_year.in_([y, y.replace("/", "-"), y.replace("-", "/")]),
            StudentEnrollment.status == "ACTIVE"
        ).count()

        completed_count = self.db.query(ExamResult).filter(ExamResult.exam_id == exam_id).count()

        if not sub:
            sub = ResultSubmission(
                exam_id=exam_id,
                class_id=exam.class_id,
                subject_id=exam.subject_id,
                teacher_id=teacher.id,
                academic_year=exam.academic_year,
                exam_name=exam.name,
                status="DRAFT",
                expected_students=enrolled_count,
                completed_students=completed_count,
                pending_students=max(0, enrolled_count - completed_count)
            )
            self.db.add(sub)
        else:
            sub.expected_students = enrolled_count
            sub.completed_students = completed_count
            sub.pending_students = max(0, enrolled_count - completed_count)
            if sub.status == "RETURNED_FOR_CORRECTION":
                # Keep state until resubmission
                pass
            else:
                sub.status = "DRAFT"

        self.db.commit()

        return {
            "success": True,
            "message": "Draft results saved successfully.",
            "completed_students": completed_count,
            "pending_students": max(0, enrolled_count - completed_count)
        }

    def submit_exam_results(
        self,
        user: User,
        exam_id: int,
        results_list: Optional[List[Dict[str, Any]]] = None,
        confirmation_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        teacher = self.get_authenticated_teacher(user)
        exam = self.db.query(Exam).filter(Exam.id == exam_id).first()
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

        # Save any incoming draft results first
        if results_list:
            self.save_draft_results(user, exam_id, results_list)

        # Enforce completeness: all actively enrolled students must have result entered
        y = exam.academic_year
        enrollments = self.db.query(StudentEnrollment).filter(
            StudentEnrollment.class_id == exam.class_id,
            StudentEnrollment.academic_year.in_([y, y.replace("/", "-"), y.replace("-", "/")]),
            StudentEnrollment.status == "ACTIVE"
        ).all()

        enrolled_student_ids = set(en.student_id for en in enrollments)
        existing_results = self.db.query(ExamResult).filter(ExamResult.exam_id == exam_id).all()
        result_map = {r.student_id: r for r in existing_results}

        missing_students = []
        for s_id in enrolled_student_ids:
            res = result_map.get(s_id)
            if not res:
                missing_students.append(s_id)
            elif res.attendance_status == "PRESENT" and res.marks_obtained is None:
                missing_students.append(s_id)

        if missing_students:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Cannot submit results. {len(missing_students)} student(s) marked PRESENT have missing marks. Complete all student results before submitting to Administration."
            )

        # Check duplicate submission prevention
        sub = self.db.query(ResultSubmission).filter(
            ResultSubmission.exam_id == exam.id,
            ResultSubmission.class_id == exam.class_id,
            ResultSubmission.subject_id == exam.subject_id,
            ResultSubmission.teacher_id == teacher.id
        ).first()

        if sub and sub.status in ("SUBMITTED", "UNDER_REVIEW", "APPROVED", "RELEASED"):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Results have already been submitted."
            )

        # Lock all results and set submission status to SUBMITTED
        for r in existing_results:
            r.status = "SUBMITTED"

        now_utc = datetime.now(timezone.utc)
        if not sub:
            sub = ResultSubmission(
                exam_id=exam_id,
                class_id=exam.class_id,
                subject_id=exam.subject_id,
                teacher_id=teacher.id,
                academic_year=exam.academic_year,
                exam_name=exam.name,
                status="SUBMITTED",
                expected_students=len(enrolled_student_ids),
                completed_students=len(enrolled_student_ids),
                pending_students=0,
                submitted_at=now_utc,
                submitted_by_id=user.id
            )
            self.db.add(sub)
        else:
            sub.status = "SUBMITTED"
            sub.expected_students = len(enrolled_student_ids)
            sub.completed_students = len(enrolled_student_ids)
            sub.pending_students = 0
            sub.submitted_at = now_utc
            sub.submitted_by_id = user.id
            sub.return_reason = None

        self.db.commit()
        self.db.refresh(sub)

        # Create Admin notification in PostgreSQL
        try:
            admin_notif = Notification(
                notification_type="RESULT_SUBMITTED",
                title="New examination results submitted",
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
                    "submitted_at": now_utc.isoformat(),
                    "link": "/admin/results"
                }
            )
            self.db.add(admin_notif)
            self.db.commit()
        except Exception:
            pass

        # Audit
        try:
            log = AuditLog(
                user_id=user.id,
                action="TEACHER_SUBMITTED_RESULTS",
                status="SUCCESS",
                details={
                    "exam_id": exam.id,
                    "exam_name": exam.name,
                    "class_id": exam.class_id,
                    "subject_id": exam.subject_id,
                    "teacher_id": teacher.id,
                    "students_count": len(enrolled_student_ids)
                }
            )
            self.db.add(log)
            self.db.commit()
        except Exception:
            pass

        return {
            "success": True,
            "message": "Results submitted successfully to Administration.",
            "submission_id": sub.id,
            "status": "SUBMITTED"
        }

    def recall_exam_results(self, user: User, exam_id: int) -> Dict[str, Any]:
        """
        Recall submitted results back to DRAFT before Administration reviews/approves.
        Guarded: cannot recall once results are APPROVED or RELEASED.
        """
        teacher = self.get_authenticated_teacher(user)
        exam = self.db.query(Exam).filter(Exam.id == exam_id).first()
        if not exam:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found.")

        # IDOR check: ensure teacher owns assignment
        y = exam.academic_year
        assignment = self.db.query(TeacherAssignment).filter(
            TeacherAssignment.teacher_id == teacher.id,
            TeacherAssignment.class_id == exam.class_id,
            TeacherAssignment.subject_id == exam.subject_id,
            TeacherAssignment.academic_year.in_([y, y.replace("/", "-"), y.replace("-", "/")]),
            TeacherAssignment.status == "ACTIVE"
        ).first()

        if not assignment and not user.has_role("ADMIN"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to recall results for this examination."
            )

        sub = self.db.query(ResultSubmission).filter(
            ResultSubmission.exam_id == exam.id,
            ResultSubmission.class_id == exam.class_id,
            ResultSubmission.subject_id == exam.subject_id,
            ResultSubmission.teacher_id == teacher.id
        ).first()

        if not sub:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No submission record found for this examination."
            )

        if sub.status in ("SUBMITTED", "UNDER_REVIEW", "APPROVED", "RELEASED"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Once results are submitted to Administration, they cannot be modified or recalled by the teacher. If a correction is required, the School Administrator must explicitly return the sheet for correction."
            )

        if sub.status == "DRAFT":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Submission is already in draft status."
            )

        # Transition back to DRAFT
        sub.status = "DRAFT"
        sub.return_reason = "Recalled by teacher for editing."

        # Reset exam results to DRAFT
        results = self.db.query(ExamResult).filter(ExamResult.exam_id == exam.id).all()
        for r in results:
            r.status = "DRAFT"

        self.db.commit()

        # Audit
        try:
            log = AuditLog(
                user_id=user.id,
                action="TEACHER_RECALLED_RESULTS",
                status="SUCCESS",
                details={
                    "exam_id": exam.id,
                    "submission_id": sub.id,
                    "teacher_id": teacher.id
                }
            )
            self.db.add(log)
            self.db.commit()
        except Exception:
            pass

        return {
            "success": True,
            "message": "Submitted results recalled back to draft successfully.",
            "submission_id": sub.id,
            "status": "DRAFT"
        }

    def enter_exam_results(self, user: User, exam_id: int, data: BulkExamResultsCreate) -> List[ExamResult]:
        """Backward compatible bulk results entry."""
        results_list = [
            {
                "student_id": entry.student_id,
                "attendance_status": "PRESENT",
                "marks_obtained": entry.marks_obtained,
                "remarks": entry.remarks
            }
            for entry in data.results
        ]
        self.save_draft_results(user, exam_id, results_list)
        return self.db.query(ExamResult).filter(ExamResult.exam_id == exam_id).all()

    # =========================================================================
    # EXAM PAPER DOCUMENT UPLOAD / DOWNLOAD / REMOVAL
    # =========================================================================

    async def upload_exam_paper(
        self,
        user: User,
        exam_id: int,
        student_id: int,
        file: UploadFile
    ) -> Dict[str, Any]:
        teacher = self.get_authenticated_teacher(user)
        exam = self.db.query(Exam).filter(Exam.id == exam_id).first()
        if not exam:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found.")

        is_assigned = self.db.query(TeacherAssignment).filter(
            TeacherAssignment.teacher_id == teacher.id,
            TeacherAssignment.class_id == exam.class_id,
            TeacherAssignment.subject_id == exam.subject_id,
            TeacherAssignment.status == "ACTIVE"
        ).first()

        if not is_assigned:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to upload exam papers for this class/subject."
            )

        # Validate MIME type
        content_type = file.content_type or mimetypes.guess_type(file.filename or "")[0] or ""
        if content_type.lower() not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file format. Only JPG, PNG, and PDF exam documents are accepted."
            )

        # Read file contents & validate size
        contents = await file.read()
        file_size = len(contents)
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File exceeds maximum allowed size (5 MB). File size: {file_size / (1024*1024):.2f} MB"
            )

        # Secure unique filename
        ext = os.path.splitext(file.filename or "")[1].lower()
        if not ext:
            ext = ".jpg" if "jpeg" in content_type or "jpg" in content_type else (".png" if "png" in content_type else ".pdf")
        
        safe_filename = f"result_{exam_id}_{student_id}_{uuid.uuid4().hex[:12]}{ext}"
        saved_path = os.path.join(UPLOAD_DIR, safe_filename)

        with open(saved_path, "wb") as f:
            f.write(contents)

        # Upsert or update ExamResult
        res = self.db.query(ExamResult).filter(
            ExamResult.exam_id == exam_id,
            ExamResult.student_id == student_id,
            ExamResult.subject_id == exam.subject_id
        ).first()

        if not res:
            res = ExamResult(
                exam_id=exam_id,
                class_id=exam.class_id,
                student_id=student_id,
                subject_id=exam.subject_id,
                attendance_status="PRESENT",
                status="DRAFT",
                recorded_by_id=user.id
            )
            self.db.add(res)

        res.paper_file_path = safe_filename
        res.paper_original_name = file.filename
        res.paper_mime_type = content_type
        res.paper_file_size = file_size
        res.paper_uploaded_at = datetime.now(timezone.utc)

        audit = AuditLog(
            user_id=user.id,
            action="UPLOAD_EXAM_PAPER",
            status="SUCCESS",
            details={
                "exam_id": exam_id,
                "exam_name": exam.name,
                "student_id": student_id,
                "filename": file.filename,
                "file_size": file_size
            }
        )
        self.db.add(audit)
        self.db.commit()
        self.db.refresh(res)

        return {
            "message": "Exam paper uploaded successfully.",
            "exam_id": exam_id,
            "student_id": student_id,
            "filename": file.filename,
            "mime_type": content_type,
            "file_size": file_size,
            "uploaded_at": res.paper_uploaded_at.isoformat()
        }

    def get_exam_paper_file(self, user: User, exam_id: int, student_id: int) -> Dict[str, Any]:
        teacher = self.get_authenticated_teacher(user)
        exam = self.db.query(Exam).filter(Exam.id == exam_id).first()
        if not exam:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found.")

        is_assigned = self.db.query(TeacherAssignment).filter(
            TeacherAssignment.teacher_id == teacher.id,
            TeacherAssignment.class_id == exam.class_id,
            TeacherAssignment.subject_id == exam.subject_id,
            TeacherAssignment.status == "ACTIVE"
        ).first()

        if not is_assigned:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to view exam papers for this class/subject."
            )

        res = self.db.query(ExamResult).filter(
            ExamResult.exam_id == exam_id,
            ExamResult.student_id == student_id,
            ExamResult.subject_id == exam.subject_id
        ).first()

        if not res or not res.paper_file_path:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No exam paper uploaded for this student.")

        file_full_path = os.path.join(UPLOAD_DIR, res.paper_file_path)
        if not os.path.exists(file_full_path):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stored exam paper file not found.")

        return {
            "full_path": file_full_path,
            "original_name": res.paper_original_name or "exam_paper.pdf",
            "mime_type": res.paper_mime_type or "application/octet-stream"
        }

    def delete_exam_paper(self, user: User, exam_id: int, student_id: int) -> Dict[str, Any]:
        teacher = self.get_authenticated_teacher(user)
        exam = self.db.query(Exam).filter(Exam.id == exam_id).first()
        if not exam:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found.")

        is_assigned = self.db.query(TeacherAssignment).filter(
            TeacherAssignment.teacher_id == teacher.id,
            TeacherAssignment.class_id == exam.class_id,
            TeacherAssignment.subject_id == exam.subject_id,
            TeacherAssignment.status == "ACTIVE"
        ).first()

        if not is_assigned:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized.")

        res = self.db.query(ExamResult).filter(
            ExamResult.exam_id == exam_id,
            ExamResult.student_id == student_id,
            ExamResult.subject_id == exam.subject_id
        ).first()

        if not res or not res.paper_file_path:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No paper to remove.")

        if res.status in ["SUBMITTED", "APPROVED", "RELEASED"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete exam paper after results have been submitted to administration."
            )

        file_full_path = os.path.join(UPLOAD_DIR, res.paper_file_path)
        if os.path.exists(file_full_path):
            try:
                os.remove(file_full_path)
            except Exception:
                pass

        res.paper_file_path = None
        res.paper_original_name = None
        res.paper_mime_type = None
        res.paper_file_size = None
        res.paper_uploaded_at = None

        self.db.commit()
        return {"message": "Exam paper document removed successfully."}
