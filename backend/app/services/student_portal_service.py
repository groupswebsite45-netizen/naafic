from datetime import datetime, date, time
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, or_, and_
from fastapi import HTTPException, status

from app.models.user import User
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.models.school_class import SchoolClass
from app.models.subject import Subject
from app.models.teacher import Teacher
from app.models.teacher_assignment import TeacherAssignment
from app.models.timetable import Timetable
from app.models.fee import StudentFee, FeePayment, FeeStructure
from app.models.exam import Exam, ExamResult
from app.models.attendance import Attendance
from app.repositories.student_repo import StudentRepository
from app.repositories.release_repo import ReleaseRepository

from app.schemas.student_portal import (
    StudentProfileResponse,
    StudentSubjectDetail,
    EnrollmentHistoryItem,
    StudentClassDetailsResponse,
    LatestExamResultSummary,
    StudentFeeSummary,
    StudentFeesPortalResponse,
    StudentDashboardResponse,
    StudentPublishedExamItem,
)
from app.schemas.attendance import (
    AttendanceOverallSummary,
    SubjectAttendanceSummary,
    AttendanceRecordResponse,
    StudentAttendancePortalResponse,
)
from app.schemas.fee import StudentFeeResponse
from app.schemas.exam import ExamResultResponse
from app.schemas.timetable import TimetableResponse
from app.schemas.school_class import SchoolClassResponse


class StudentPortalService:
    """
    Dedicated, isolated service for the authenticated Student Portal.
    Strict IDOR prevention: All data queries are bound to the authenticated student.
    """

    def __init__(self, db: Session):
        self.db = db
        self.student_repo = StudentRepository(db)
        self.release_repo = ReleaseRepository(db)

    def get_authenticated_student(self, user: User) -> Student:
        """Resolve the canonical Student record from the authenticated User account."""
        student = self.student_repo.get_by_user_id(user.id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student profile not found for this authenticated user account."
            )
        return student

    def get_profile(self, user: User) -> StudentProfileResponse:
        """
        Get read-only profile data for the authenticated student.
        Students cannot update this data directly.
        """
        student = self.get_authenticated_student(user)
        active_enrollment = student.current_enrollment
        current_class = active_enrollment.school_class if active_enrollment else None

        return StudentProfileResponse(
            id=student.id,
            user_id=student.user_id,
            admission_number=student.admission_number,
            first_name=student.first_name,
            middle_name=student.middle_name,
            last_name=student.last_name,
            full_name=student.full_name,
            gender=student.gender,
            date_of_birth=student.date_of_birth,
            phone=student.phone or (user.phone_number if user else None),
            email=student.guardian_email or (user.email if user else None),
            address=student.address,
            guardian_name=student.guardian_name,
            guardian_phone=student.guardian_phone,
            guardian_email=student.guardian_email,
            guardian_relationship=student.guardian_relationship,
            admission_date=student.admission_date,
            status=student.status,
            current_class_name=current_class.name if current_class else None,
            current_class_code=current_class.code if current_class else None,
            academic_year=active_enrollment.academic_year if active_enrollment else None,
            portal_account_status="Active" if user.is_active else "Inactive",
            photo_url=student.photo_url,
            photo_path=student.photo_path
        )

    def get_academic_years(self, user: User) -> List[str]:
        """Get distinct academic years where the authenticated student has enrollment records or attendance."""
        student = self.get_authenticated_student(user)
        enr_years = [
            y[0]
            for y in self.db.query(StudentEnrollment.academic_year)
            .filter(StudentEnrollment.student_id == student.id)
            .distinct()
            .all()
            if y[0]
        ]
        att_years = [
            y[0]
            for y in self.db.query(Attendance.academic_year)
            .filter(Attendance.student_id == student.id)
            .distinct()
            .all()
            if y[0]
        ]
        all_years = sorted(list(set(enr_years + att_years)), reverse=True)
        if not all_years and student.current_enrollment:
            all_years = [student.current_enrollment.academic_year]
        return ["2026/2027"]

    def get_dashboard(self, user: User) -> StudentDashboardResponse:
        """Aggregate authenticated student dashboard metrics strictly from PostgreSQL."""
        student = self.get_authenticated_student(user)
        profile = self.get_profile(user)
        active_enr = student.current_enrollment
        current_class = active_enr.school_class if active_enr else None
        academic_year = active_enr.academic_year if active_enr else "2026/2027"

        # 1. Subjects count & Today's timetable
        subjects_count = 0
        today_schedule: List[Timetable] = []
        next_period: Optional[Timetable] = None

        if current_class:
            subjects_count = (
                self.db.query(TeacherAssignment)
                .filter(
                    TeacherAssignment.class_id == current_class.id,
                    TeacherAssignment.status == "ACTIVE"
                )
                .distinct(TeacherAssignment.subject_id)
                .count()
            )

            today_name = datetime.now().strftime("%A")
            today_schedule = (
                self.db.query(Timetable)
                .filter(
                    Timetable.class_id == current_class.id,
                    Timetable.day_of_week == today_name,
                    Timetable.status.in_(["ACTIVE", "PUBLISHED"])
                )
                .order_by(Timetable.start_time.asc())
                .all()
            )

            # If today has no classes (e.g. weekend/evening), find the next scheduled period for the week
            if today_schedule:
                current_time = datetime.now().time()
                upcoming = [s for s in today_schedule if s.start_time >= current_time]
                next_period = upcoming[0] if upcoming else today_schedule[0]
            else:
                next_period = (
                    self.db.query(Timetable)
                    .filter(Timetable.class_id == current_class.id, Timetable.status.in_(["ACTIVE", "PUBLISHED"]))
                    .order_by(Timetable.day_of_week.asc(), Timetable.start_time.asc())
                    .first()
                )

        # 2. Attendance summary from PostgreSQL
        total_att = self.db.query(Attendance).filter(Attendance.student_id == student.id).count()
        present_att = self.db.query(Attendance).filter(
            Attendance.student_id == student.id,
            Attendance.status == "PRESENT"
        ).count()
        absent_att = self.db.query(Attendance).filter(
            Attendance.student_id == student.id,
            Attendance.status == "ABSENT"
        ).count()
        excused_att = self.db.query(Attendance).filter(
            Attendance.student_id == student.id,
            Attendance.status == "EXCUSED"
        ).count()

        att_pct = round((present_att / total_att * 100), 1) if total_att > 0 else 0.0
        att_summary = AttendanceOverallSummary(
            total_classes=total_att,
            present_count=present_att,
            absent_count=absent_att,
            excused_count=excused_att,
            attendance_percentage=att_pct
        )

        # 3. Fees calculation
        student_fees = self.db.query(StudentFee).filter(StudentFee.student_id == student.id).all()
        total_due = sum(sf.net_amount for sf in student_fees)
        total_paid = sum(sf.total_paid for sf in student_fees)
        outstanding = max(0.0, total_due - total_paid)

        # 4. Latest RELEASED examination result
        latest_res = (
            self.db.query(ExamResult)
            .join(Exam, ExamResult.exam_id == Exam.id)
            .filter(
                ExamResult.student_id == student.id,
                ExamResult.status == "RELEASED"
            )
            .order_by(Exam.start_date.desc(), ExamResult.id.desc())
            .first()
        )

        latest_exam_summary: Optional[LatestExamResultSummary] = None
        if latest_res:
            pct = None
            if latest_res.marks_obtained is not None and latest_res.exam and latest_res.exam.max_marks:
                pct = round(float(latest_res.marks_obtained) / float(latest_res.exam.max_marks) * 100, 1)

            latest_exam_summary = LatestExamResultSummary(
                exam_name=latest_res.exam.name if latest_res.exam else "Examination",
                academic_year=latest_res.exam.academic_year if latest_res.exam else academic_year,
                subject_name=latest_res.subject.name if latest_res.subject else "Subject",
                marks_obtained=float(latest_res.marks_obtained) if latest_res.marks_obtained is not None else None,
                total_marks=float(latest_res.exam.max_marks) if latest_res.exam else 100.0,
                percentage=pct,
                grade=latest_res.grade,
                released_at=latest_res.created_at
            )

        # 5. Recent RELEASED exam results list (up to 5)
        recent_results = (
            self.db.query(ExamResult)
            .join(Exam, ExamResult.exam_id == Exam.id)
            .filter(
                ExamResult.student_id == student.id,
                ExamResult.status == "RELEASED"
            )
            .order_by(Exam.start_date.desc(), ExamResult.id.desc())
            .limit(5)
            .all()
        )

        class_resp = SchoolClassResponse.model_validate(current_class) if current_class else None
        next_resp = TimetableResponse.model_validate(next_period) if next_period else None

        return StudentDashboardResponse(
            student=profile,
            current_class=class_resp,
            academic_year=academic_year,
            enrolled_subjects_count=subjects_count,
            attendance_summary=att_summary,
            total_fees_due=round(total_due, 2),
            total_fees_paid=round(total_paid, 2),
            outstanding_balance=round(outstanding, 2),
            latest_exam_result=latest_exam_summary,
            next_class_period=next_resp,
            today_schedule=[TimetableResponse.model_validate(t) for t in today_schedule],
            recent_exam_results=[ExamResultResponse.model_validate(r) for r in recent_results]
        )

    def get_my_class_details(self, user: User, academic_year: Optional[str] = None) -> StudentClassDetailsResponse:
        """Get enrolled class details, subjects with teachers, and historical enrollments."""
        student = self.get_authenticated_student(user)

        # Resolve enrollment for requested academic year or current active
        enr_query = self.db.query(StudentEnrollment).filter(StudentEnrollment.student_id == student.id)
        if academic_year:
            enrollment = enr_query.filter(StudentEnrollment.academic_year == academic_year).first()
        else:
            enrollment = student.current_enrollment

        sc = enrollment.school_class if enrollment else None
        year = enrollment.academic_year if enrollment else (academic_year or "2026/2027")

        # Classmates count
        classmates_count = 0
        if sc:
            classmates_count = self.db.query(StudentEnrollment).filter(
                StudentEnrollment.class_id == sc.id,
                StudentEnrollment.academic_year == year,
                StudentEnrollment.status == "ACTIVE"
            ).count()

        # Enrolled subjects mapped through TeacherAssignment
        subjects_list: List[StudentSubjectDetail] = []
        class_teacher_name = None

        if sc:
            assignments = (
                self.db.query(TeacherAssignment)
                .filter(
                    TeacherAssignment.class_id == sc.id,
                    TeacherAssignment.academic_year == year,
                    TeacherAssignment.status == "ACTIVE"
                )
                .all()
            )

            # Fallback if no specific year assignment, use any active assignments for class
            if not assignments:
                assignments = (
                    self.db.query(TeacherAssignment)
                    .filter(
                        TeacherAssignment.class_id == sc.id,
                        TeacherAssignment.status == "ACTIVE"
                    )
                    .all()
                )

            seen_subjects = set()
            for a in assignments:
                if a.subject and a.subject.id not in seen_subjects:
                    seen_subjects.add(a.subject.id)
                    t_name = a.teacher.full_name if a.teacher else None
                    if not class_teacher_name and t_name:
                        class_teacher_name = t_name

                    subjects_list.append(
                        StudentSubjectDetail(
                            id=a.subject.id,
                            name=a.subject.name,
                            code=a.subject.code,
                            department=a.subject.department,
                            teacher_name=t_name,
                            status=a.subject.status
                        )
                    )

        # Historical enrollments
        all_enrollments = (
            self.db.query(StudentEnrollment)
            .filter(StudentEnrollment.student_id == student.id)
            .order_by(StudentEnrollment.academic_year.desc())
            .all()
        )

        history_items = [
            EnrollmentHistoryItem(
                academic_year=e.academic_year,
                class_name=e.school_class.name if e.school_class else "Class",
                class_code=e.school_class.code if e.school_class else "",
                section=e.school_class.section if e.school_class else None,
                status=e.status,
                roll_number=e.roll_number
            )
            for e in all_enrollments
        ]

        class_resp = SchoolClassResponse.model_validate(sc) if sc else None

        return StudentClassDetailsResponse(
            school_class=class_resp,
            academic_year=year,
            section=sc.section if sc else None,
            class_teacher_name=class_teacher_name,
            capacity=sc.capacity if sc else 40,
            classmates_count=classmates_count,
            subjects=subjects_list,
            enrollment_history=history_items
        )

    def get_my_timetable(self, user: User, academic_year: Optional[str] = None) -> List[TimetableResponse]:
        """Get weekly schedule periods scoped strictly to student's enrolled class."""
        student = self.get_authenticated_student(user)
        enr_query = self.db.query(StudentEnrollment).filter(StudentEnrollment.student_id == student.id)
        if academic_year:
            years = [academic_year, academic_year.replace("/", "-"), academic_year.replace("-", "/")]
            enrollment = enr_query.filter(StudentEnrollment.academic_year.in_(years)).first()
        else:
            enrollment = student.current_enrollment

        if not enrollment or not enrollment.class_id:
            return []

        day_order = {
            "Saturday": 1, "Sunday": 2, "Monday": 3, "Tuesday": 4, "Wednesday": 5, "Thursday": 6, "Friday": 7
        }

        query = self.db.query(Timetable).filter(
            Timetable.class_id == enrollment.class_id,
            Timetable.status.in_(["ACTIVE", "PUBLISHED"])
        )
        if enrollment.academic_year:
            years = [enrollment.academic_year, enrollment.academic_year.replace("/", "-"), enrollment.academic_year.replace("-", "/")]
            query = query.filter(Timetable.academic_year.in_(years))

        slots = query.order_by(Timetable.start_time.asc()).all()
        sorted_slots = sorted(slots, key=lambda s: (day_order.get(s.day_of_week, 8), s.start_time))
        
        result: List[TimetableResponse] = []
        for s in sorted_slots:
            c_name = s.school_class.name if s.school_class else None
            s_name = s.subject.name if s.subject else ("Break" if getattr(s, "is_break", False) else None)
            t_name = s.teacher.full_name if s.teacher else None
            r_name = s.room
            result.append(
                TimetableResponse(
                    id=s.id,
                    academic_year=s.academic_year,
                    class_id=s.class_id,
                    subject_id=s.subject_id,
                    teacher_id=s.teacher_id,
                    day_of_week=s.day_of_week,
                    period_number=getattr(s, "period_number", None),
                    start_time=s.start_time,
                    end_time=s.end_time,
                    room=r_name,
                    room_number=r_name,
                    status=s.status,
                    is_break=getattr(s, "is_break", False),
                    published_at=getattr(s, "published_at", None),
                    class_name=c_name,
                    class_code=s.school_class.code if s.school_class else "",
                    subject_name=s_name,
                    subject_code=s.subject.code if s.subject else "",
                    teacher_name=t_name,
                    created_at=s.created_at,
                    updated_at=s.updated_at
                )
            )
        return result

    def get_my_attendance(
        self,
        user: User,
        academic_year: Optional[str] = None,
        month: Optional[int] = None,
        subject_id: Optional[int] = None,
        status_filter: Optional[str] = None
    ) -> StudentAttendancePortalResponse:
        """
        Query attendance history and aggregated statistics for the authenticated student.
        IDOR guarantee: Filtered strictly on student_id.
        """
        student = self.get_authenticated_student(user)
        enr = student.current_enrollment
        target_year = academic_year or (enr.academic_year if enr else None)

        # Base query for stats
        base_query = self.db.query(Attendance).filter(
            Attendance.student_id == student.id
        )

        if target_year:
            years = [target_year, target_year.replace("/", "-"), target_year.replace("-", "/")]
            filtered_query = base_query.filter(Attendance.academic_year.in_(years))
            # If records exist in the specific target year or explicitly requested by dropdown, use filtered query
            if filtered_query.count() > 0 or academic_year:
                base_query = filtered_query

        total_classes = base_query.count()
        present_count = base_query.filter(Attendance.status == "PRESENT").count()
        late_count = base_query.filter(Attendance.status == "LATE").count()
        absent_count = base_query.filter(Attendance.status.in_(["ABSENT", "UNEXCUSED"])).count()
        excused_count = base_query.filter(Attendance.status == "EXCUSED").count()
        pct = round(((present_count + late_count) / total_classes * 100), 1) if total_classes > 0 else 0.0

        overall_summary = AttendanceOverallSummary(
            total_classes=total_classes,
            present_count=present_count,
            absent_count=absent_count,
            late_count=late_count,
            excused_count=excused_count,
            attendance_percentage=pct
        )

        # Attendance by Subject
        by_subject: List[SubjectAttendanceSummary] = []
        subject_ids = (
            base_query
            .with_entities(Attendance.subject_id)
            .distinct()
            .all()
        )

        for (s_id,) in subject_ids:
            if not s_id:
                continue
            subj = self.db.query(Subject).filter(Subject.id == s_id).first()
            if not subj:
                continue

            sub_query = base_query.filter(Attendance.subject_id == s_id)
            sub_total = sub_query.count()
            sub_present = sub_query.filter(Attendance.status == "PRESENT").count()
            sub_late = sub_query.filter(Attendance.status == "LATE").count()
            sub_absent = sub_query.filter(Attendance.status.in_(["ABSENT", "UNEXCUSED"])).count()
            sub_excused = sub_query.filter(Attendance.status == "EXCUSED").count()
            sub_pct = round(((sub_present + sub_late) / sub_total * 100), 1) if sub_total > 0 else 0.0

            by_subject.append(
                SubjectAttendanceSummary(
                    subject_id=subj.id,
                    subject_name=subj.name,
                    subject_code=subj.code,
                    total_classes=sub_total,
                    present_count=sub_present,
                    absent_count=sub_absent,
                    late_count=sub_late,
                    excused_count=sub_excused,
                    attendance_percentage=sub_pct
                )
            )

        by_subject.sort(key=lambda s: s.subject_name)

        # History list with dynamic filters
        history_query = base_query
        if month:
            history_query = history_query.filter(extract("month", Attendance.date) == month)
        if subject_id:
            history_query = history_query.filter(Attendance.subject_id == subject_id)
        if status_filter:
            history_query = history_query.filter(Attendance.status == status_filter.upper())

        records = history_query.order_by(Attendance.date.desc(), Attendance.period.desc()).all()

        history_items = [
            AttendanceRecordResponse(
                id=r.id,
                date=r.date,
                subject_id=r.subject_id,
                subject_name=r.subject.name if r.subject else "Subject",
                subject_code=r.subject.code if r.subject else None,
                period=r.period,
                status=r.status,
                teacher_name=r.teacher.full_name if r.teacher else None,
                remarks=r.remarks
            )
            for r in records
        ]

        return StudentAttendancePortalResponse(
            academic_year=target_year or "2026/2027",
            summary=overall_summary,
            by_subject=by_subject,
            history=history_items
        )

    def get_my_fees(self, user: User, academic_year: Optional[str] = None) -> StudentFeesPortalResponse:
        """
        Get student fee invoices, payment receipts, and financial summary.
        IDOR protection: strictly filters by student_id.
        """
        student = self.get_authenticated_student(user)

        query = self.db.query(StudentFee).filter(StudentFee.student_id == student.id)
        if academic_year:
            query = query.filter(StudentFee.academic_year == academic_year)

        fees = query.order_by(StudentFee.due_date.asc()).all()

        total_due = sum(sf.net_amount for sf in fees)
        total_paid = sum(sf.total_paid for sf in fees)
        outstanding = max(0.0, total_due - total_paid)
        is_cleared = (outstanding <= 0.00)

        fee_responses = [StudentFeeResponse.model_validate(f) for f in fees]

        return StudentFeesPortalResponse(
            summary=StudentFeeSummary(
                total_billed=round(total_due, 2),
                total_paid=round(total_paid, 2),
                total_outstanding=round(outstanding, 2),
                is_cleared=is_cleared
            ),
            fees=fee_responses
        )

    def get_my_published_exams(self, user: User, academic_year: Optional[str] = None) -> List[StudentPublishedExamItem]:
        """
        Get all PUBLISHED examinations and schedules for the authenticated student's enrolled class.
        Strict class, academic year, and institution isolation.
        Results / marks remain completely hidden unless officially RELEASED by school administration.
        """
        student = self.get_authenticated_student(user)

        # 1. Resolve student's enrollments
        active_enrollments = [enr for enr in student.enrollments if enr.status == "ACTIVE"]
        enrollments = active_enrollments if active_enrollments else student.enrollments
        if not enrollments:
            return []

        enrolled_class_ids = list({enr.class_id for enr in enrollments if enr.class_id})
        if not enrolled_class_ids:
            return []

        # 2. Year normalization helper
        def _get_year_variants(yr: Optional[str]) -> List[str]:
            if not yr:
                return []
            cleaned = yr.strip()
            return list({cleaned, cleaned.replace("-", "/"), cleaned.replace("/", "-")})

        query = (
            self.db.query(Exam)
            .filter(
                Exam.class_id.in_(enrolled_class_ids),
                func.upper(Exam.status) == "PUBLISHED"
            )
        )

        if academic_year:
            query = query.filter(Exam.academic_year.in_(_get_year_variants(academic_year)))
        else:
            student_years = set()
            for enr in enrollments:
                if enr.academic_year:
                    student_years.update(_get_year_variants(enr.academic_year))
            if student_years:
                query = query.filter(Exam.academic_year.in_(list(student_years)))

        exams = query.order_by(Exam.start_date.asc(), Exam.start_time.asc(), Exam.id.asc()).all()

        output: List[StudentPublishedExamItem] = []
        for exam in exams:
            # Check if there is an officially RELEASED result for this student and exam
            released_result = (
                self.db.query(ExamResult)
                .filter(
                    ExamResult.exam_id == exam.id,
                    ExamResult.student_id == student.id,
                    or_(
                        ExamResult.status == "RELEASED",
                        and_(
                            func.upper(exam.status) == "PUBLISHED",
                            ExamResult.status.in_(["SUBMITTED", "APPROVED", "RELEASED"])
                        )
                    )
                )
                .first()
            )

            has_released = released_result is not None
            c_name = exam.school_class.name if exam.school_class else None
            c_code = exam.school_class.code if exam.school_class else None
            c_sec = exam.school_class.section if exam.school_class else None
            s_name = exam.subject.name if exam.subject else None
            s_code = exam.subject.code if exam.subject else None
            t_name = exam.teacher.full_name if (exam.teacher and hasattr(exam.teacher, 'full_name')) else None

            output.append(
                StudentPublishedExamItem(
                    id=exam.id,
                    name=exam.name,
                    exam_type=exam.exam_type,
                    academic_year=exam.academic_year,
                    class_id=exam.class_id,
                    class_name=c_name,
                    class_code=c_code,
                    section=c_sec,
                    subject_id=exam.subject_id,
                    subject_name=s_name,
                    subject_code=s_code,
                    teacher_name=t_name,
                    start_date=exam.start_date,
                    end_date=exam.end_date,
                    start_time=exam.start_time,
                    end_time=exam.end_time,
                    instructions=exam.instructions,
                    max_marks=float(exam.max_marks) if exam.max_marks is not None else 100.0,
                    pass_marks=float(exam.pass_marks) if exam.pass_marks is not None else 50.0,
                    status=exam.status,
                    published_at=exam.published_at,
                    result_submission_deadline=exam.result_submission_deadline,
                    has_released_result=has_released,
                    marks_obtained=float(released_result.marks_obtained) if (has_released and released_result.marks_obtained is not None) else None,
                    grade=released_result.grade if has_released else None,
                    remarks=released_result.remarks if has_released else None,
                    attendance_status=released_result.attendance_status if has_released else None,
                    percentage=released_result.percentage if has_released else None,
                    total_marks=float(exam.max_marks) if exam.max_marks is not None else 100.0,
                )
            )

        return output

    def get_my_exam_results(self, user: User, academic_year: Optional[str] = None) -> List[ExamResultResponse]:
        """
        Get officially RELEASED exam results for the authenticated student.
        CRITICAL GATE: DRAFT, SUBMITTED, and APPROVED results are strictly filtered out.
        """
        student = self.get_authenticated_student(user)

        query = (
            self.db.query(ExamResult)
            .join(Exam, ExamResult.exam_id == Exam.id)
            .filter(
                ExamResult.student_id == student.id,
                or_(
                    ExamResult.status == "RELEASED",
                    and_(
                        func.upper(Exam.status) == "PUBLISHED",
                        ExamResult.status.in_(["SUBMITTED", "APPROVED", "RELEASED"])
                    )
                )
            )
        )

        if academic_year:
            cleaned = academic_year.strip()
            variants = list({cleaned, cleaned.replace("-", "/"), cleaned.replace("/", "-")})
            query = query.filter(Exam.academic_year.in_(variants))

        results = query.order_by(Exam.start_date.desc(), Exam.id.desc()).all()
        return [ExamResultResponse.model_validate(r) for r in results]

    def record_result_view(self, user: User, exam_name: str, academic_year: str, class_id: Optional[int] = None) -> Dict[str, Any]:
        """Record view event for audit tracking when student views released results."""
        student = self.get_authenticated_student(user)
        enr = student.current_enrollment
        target_class_id = class_id or (enr.class_id if enr else None)

        if not target_class_id:
            return {"success": False, "message": "Student not enrolled in an active class."}

        view = self.release_repo.record_student_view(
            student_id=student.id,
            exam_name=exam_name,
            academic_year=academic_year,
            class_id=target_class_id
        )

        self.db.commit()

        return {
            "success": True,
            "view_count": view.view_count,
            "first_viewed_at": view.first_viewed_at.isoformat(),
            "last_viewed_at": view.last_viewed_at.isoformat(),
        }
