import io
import calendar
from datetime import date, datetime, timedelta, timezone
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc, and_, or_, case
from fastapi import HTTPException, status

from app.models.attendance import Attendance
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.models.school_class import SchoolClass
from app.models.subject import Subject
from app.models.teacher import Teacher
from app.models.teacher_assignment import TeacherAssignment
from app.models.user import User
from app.models.system_setting import SystemSetting
from app.schemas.admin_attendance import (
    AdminTeacherOption,
    AdminClassOption,
    AdminSubjectOption,
    AdminMonthOption,
    AdminAttendanceFilterOptionsResponse,
    AdminAttendanceKPIs,
    AdminAttendanceDailySummaryItem,
    AdminAttendanceWeeklySummaryItem,
    AdminAttendanceMonthlySummaryItem,
    AdminAttendanceRecentSessionItem,
    AbsenceDateDetail,
    AdminAttendanceFrequentAbsenteeItem,
    AdminAttendanceDashboardResponse,
    AdminAttendanceRecordItem,
    AdminAttendanceRecordsListResponse,
    AdminClassInfo,
    AdminClassAttendanceSummaryStats,
    AdminClassStudentAttendanceItem,
    AdminClassAttendanceReportResponse,
)
from app.schemas.attendance import (
    StudentSubjectAttendanceBreakdown,
    StudentAttendanceHistoryDetailResponse,
    AttendanceRecordResponse,
)

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape, portrait
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas


class AttendanceNumberedCanvas(canvas.Canvas):
    """Two-pass canvas for total page numbering and official document footer."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_decorations(self, total_pages: int):
        self.saveState()
        self.setStrokeColor(colors.HexColor("#0f172a"))
        self.setLineWidth(1.5)
        self.line(25, self._pagesize[1] - 18, self._pagesize[0] - 25, self._pagesize[1] - 18)

        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.75)
        self.line(25, 25, self._pagesize[0] - 25, 25)

        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(colors.HexColor("#64748b"))
        self.drawString(25, 14, "SOMROYAL EMS — OFFICIAL ATTENDANCE & ABSENCE MONITORING AUDIT RECORD")

        page_str = f"Page {self._pageNumber} of {total_pages}"
        self.drawRightString(self._pagesize[0] - 25, 14, page_str)
        self.restoreState()


class AdminAttendanceService:
    """Service providing school-wide attendance monitoring, analysis, and reports for School Admins."""

    def __init__(self, db: Session):
        self.db = db

    def get_school_metadata(self) -> Dict[str, str]:
        settings_rows = self.db.query(SystemSetting).all()
        settings_map = {s.key: s.value for s in settings_rows}
        return {
            "name": settings_map.get("school_name", "Somroyal Educational Management System"),
            "motto": settings_map.get("school_motto", "Excellence in Education and Character"),
            "phone": settings_map.get("school_phone", "+252 61 0000000"),
            "email": settings_map.get("school_email", "info@ems.edu.so"),
            "address": settings_map.get("school_address", "Mogadishu, Somalia"),
            "academic_year": settings_map.get("academic_year_current", "2026/2027"),
        }

    def get_filter_options(
        self,
        academic_year: Optional[str] = None,
        class_id: Optional[int] = None,
        subject_id: Optional[int] = None,
    ) -> AdminAttendanceFilterOptionsResponse:
        today = date.today()
        all_years = ["2026/2027"]

        target_year = academic_year.strip() if academic_year else None
        year_variants = {target_year, target_year.replace('/', '-'), target_year.replace('-', '/')} if target_year else set()

        # Classes: filter by academic year if provided
        class_query = self.db.query(SchoolClass).filter(SchoolClass.status == "ACTIVE")
        if target_year:
            class_query = class_query.filter(SchoolClass.academic_year.in_(year_variants))
        classes = class_query.order_by(SchoolClass.name.asc()).all()
        if not classes and target_year:
            # Fallback to all classes if exact academic_year string had no classes
            classes = self.db.query(SchoolClass).filter(SchoolClass.status == "ACTIVE").order_by(SchoolClass.name.asc()).all()

        class_options = [
            AdminClassOption(
                id=c.id,
                name=c.name,
                code=c.code or f"CLS-{c.id}",
                academic_year=c.academic_year or "2026/2027",
                grade_level=c.level,
                section=c.section,
            )
            for c in classes
        ]

        # Subjects:
        # If class_id is provided, load ONLY subjects officially assigned to that class
        if class_id:
            subj_query = (
                self.db.query(Subject, TeacherAssignment.class_id, TeacherAssignment.academic_year)
                .join(TeacherAssignment, TeacherAssignment.subject_id == Subject.id)
                .filter(
                    TeacherAssignment.class_id == class_id,
                    TeacherAssignment.status == "ACTIVE",
                    Subject.status == "ACTIVE"
                )
            )
            if target_year:
                subj_query = subj_query.filter(TeacherAssignment.academic_year.in_(year_variants))
            
            raw_subjects = subj_query.order_by(Subject.name.asc()).all()
            
            # Also check if attendance exists for this class with subjects (e.g. historical sessions)
            att_sub_ids = [
                r[0] for r in self.db.query(Attendance.subject_id)
                .filter(Attendance.class_id == class_id)
                .distinct().all() if r[0]
            ]
            seen_sub_ids = set()
            subject_options = []
            for s, c_id, yr in raw_subjects:
                if s.id not in seen_sub_ids:
                    seen_sub_ids.add(s.id)
                    subject_options.append(
                        AdminSubjectOption(
                            id=s.id,
                            name=s.name,
                            code=s.code or f"SUB-{s.id}",
                            class_id=c_id,
                            academic_year=yr,
                        )
                    )
            
            if att_sub_ids:
                missing_sub_ids = [sid for sid in att_sub_ids if sid not in seen_sub_ids]
                if missing_sub_ids:
                    extra_subs = self.db.query(Subject).filter(Subject.id.in_(missing_sub_ids), Subject.status == "ACTIVE").all()
                    for es in extra_subs:
                        subject_options.append(
                            AdminSubjectOption(
                                id=es.id,
                                name=es.name,
                                code=es.code or f"SUB-{es.id}",
                                class_id=class_id,
                                academic_year=target_year,
                            )
                        )
        else:
            # All active subjects
            subjects = self.db.query(Subject).filter(Subject.status == "ACTIVE").order_by(Subject.name.asc()).all()
            subject_options = [
                AdminSubjectOption(
                    id=s.id,
                    name=s.name,
                    code=s.code or f"SUB-{s.id}",
                )
                for s in subjects
            ]

        # Teachers:
        # If class_id is provided, load ONLY teachers assigned to teach that specific class
        # If subject_id is ALSO provided, narrow to teachers assigned to that specific class AND subject
        if class_id:
            tch_query = (
                self.db.query(Teacher, TeacherAssignment.class_id, TeacherAssignment.subject_id, TeacherAssignment.academic_year)
                .join(TeacherAssignment, TeacherAssignment.teacher_id == Teacher.id)
                .filter(
                    TeacherAssignment.class_id == class_id,
                    TeacherAssignment.status == "ACTIVE",
                    Teacher.status == "ACTIVE"
                )
            )
            if target_year:
                tch_query = tch_query.filter(TeacherAssignment.academic_year.in_(year_variants))
            if subject_id:
                tch_query = tch_query.filter(TeacherAssignment.subject_id == subject_id)

            raw_teachers = tch_query.order_by(Teacher.first_name.asc(), Teacher.last_name.asc()).all()
            seen_tch_ids = set()
            teacher_options = []
            for t, c_id, s_id, yr in raw_teachers:
                if t.id not in seen_tch_ids:
                    seen_tch_ids.add(t.id)
                    teacher_options.append(
                        AdminTeacherOption(
                            id=t.id,
                            name=t.full_name,
                            employee_number=t.teacher_number,
                            class_id=c_id,
                            subject_id=s_id,
                            academic_year=yr,
                        )
                    )
        else:
            # All active teachers
            teachers = self.db.query(Teacher).filter(Teacher.status == "ACTIVE").order_by(Teacher.first_name.asc(), Teacher.last_name.asc()).all()
            teacher_options = [
                AdminTeacherOption(
                    id=t.id,
                    name=t.full_name,
                    employee_number=t.teacher_number,
                )
                for t in teachers
            ]

        # Months
        months = [
            AdminMonthOption(value=m, name=calendar.month_name[m])
            for m in range(1, 13)
        ]

        return AdminAttendanceFilterOptionsResponse(
            academic_years=all_years,
            classes=class_options,
            subjects=subject_options,
            teachers=teacher_options,
            months=months,
        )

    def get_dashboard(
        self,
        academic_year: Optional[str] = None,
        month: Optional[int] = None,
        year: Optional[int] = None,
        class_id: Optional[int] = None,
        subject_id: Optional[int] = None,
        teacher_id: Optional[int] = None,
        attendance_date: Optional[date] = None,
        threshold: int = 3,
    ) -> AdminAttendanceDashboardResponse:
        today = date.today()
        
        # Base query for attendance strictly enforcing past & today only
        query = self.db.query(Attendance).filter(Attendance.date <= today)

        if class_id:
            query = query.filter(Attendance.class_id == class_id)
        if subject_id:
            query = query.filter(Attendance.subject_id == subject_id)
        if teacher_id:
            query = query.filter(Attendance.teacher_id == teacher_id)
        if attendance_date:
            query = query.filter(Attendance.date == attendance_date)
        if academic_year:
            years = [academic_year, academic_year.replace("/", "-"), academic_year.replace("-", "/")]
            query = query.filter(Attendance.academic_year.in_(years))
        if month:
            query = query.filter(func.extract("month", Attendance.date) == month)
        if year:
            query = query.filter(func.extract("year", Attendance.date) == year)

        # 1. KPIs
        # Total active students
        std_query = self.db.query(Student).filter(Student.status == "ACTIVE")
        if class_id:
            std_query = std_query.join(StudentEnrollment, StudentEnrollment.student_id == Student.id).filter(
                StudentEnrollment.class_id == class_id,
                StudentEnrollment.status == "ACTIVE"
            )
        total_students = std_query.count()

        # Today's attendance
        today_target = attendance_date if attendance_date else today
        today_att = self.db.query(
            Attendance.status,
            func.count(Attendance.id)
        ).filter(
            Attendance.date == today_target
        )
        if class_id:
            today_att = today_att.filter(Attendance.class_id == class_id)
        if subject_id:
            today_att = today_att.filter(Attendance.subject_id == subject_id)
        if teacher_id:
            today_att = today_att.filter(Attendance.teacher_id == teacher_id)
        today_counts = dict(today_att.group_by(Attendance.status).all())

        today_present = today_counts.get("PRESENT", 0)
        today_absent = today_counts.get("ABSENT", 0) + today_counts.get("EXCUSED", 0) + today_counts.get("UNEXCUSED", 0)
        today_late = today_counts.get("LATE", 0)
        today_total_marked = today_present + today_absent + today_late
        today_pct = round((today_present + today_late) / today_total_marked * 100, 1) if today_total_marked > 0 else 0.0

        # Overall in current filter
        overall_counts = dict(
            query.with_entities(Attendance.status, func.count(Attendance.id)).group_by(Attendance.status).all()
        )
        total_p = overall_counts.get("PRESENT", 0)
        total_a = overall_counts.get("ABSENT", 0) + overall_counts.get("EXCUSED", 0) + overall_counts.get("UNEXCUSED", 0)
        total_l = overall_counts.get("LATE", 0)
        all_marked = total_p + total_a + total_l
        overall_pct = round((total_p + total_l) / all_marked * 100, 1) if all_marked > 0 else 0.0

        # Frequent absentees
        frequent_absentees = self.get_frequent_absentees(
            class_id=class_id,
            subject_id=subject_id,
            teacher_id=teacher_id,
            academic_year=academic_year,
            month=month,
            year=year,
            threshold=threshold,
        )

        # 2. Daily summary (last 14 days where records exist up to today)
        daily_rows = self.db.query(
            Attendance.date,
            func.sum(case((Attendance.status.in_(["PRESENT", "LATE"]), 1), else_=0)).label("present"),
            func.sum(case((Attendance.status.in_(["ABSENT", "EXCUSED", "UNEXCUSED"]), 1), else_=0)).label("absent"),
            func.sum(case((Attendance.status == "LATE", 1), else_=0)).label("late"),
        ).filter(
            Attendance.date <= today
        )
        if class_id:
            daily_rows = daily_rows.filter(Attendance.class_id == class_id)
        if subject_id:
            daily_rows = daily_rows.filter(Attendance.subject_id == subject_id)
        if teacher_id:
            daily_rows = daily_rows.filter(Attendance.teacher_id == teacher_id)
        if academic_year:
            years = [academic_year, academic_year.replace("/", "-"), academic_year.replace("-", "/")]
            daily_rows = daily_rows.filter(Attendance.academic_year.in_(years))
        if month:
            daily_rows = daily_rows.filter(func.extract("month", Attendance.date) == month)
        if year:
            daily_rows = daily_rows.filter(func.extract("year", Attendance.date) == year)

        daily_rows = daily_rows.group_by(Attendance.date).order_by(desc(Attendance.date)).limit(14).all()
        daily_rows.reverse()

        daily_summary = [
            AdminAttendanceDailySummaryItem(
                date=r.date,
                day_name=r.date.strftime("%a"),
                present_count=r.present or 0,
                absent_count=r.absent or 0,
                late_count=r.late or 0,
                attendance_percentage=round((r.present or 0) / ((r.present or 0) + (r.absent or 0)) * 100, 1)
                if ((r.present or 0) + (r.absent or 0)) > 0 else 0.0,
            )
            for r in daily_rows
        ]

        # 3. Weekly summary (last 8 calendar weeks)
        weekly_summary = self._compute_weekly_summary(class_id, subject_id, teacher_id, academic_year)

        # 4. Monthly summary
        monthly_summary = self._compute_monthly_summary(class_id, subject_id, teacher_id, academic_year)

        # 5. Recent sessions
        recent_sessions = self._compute_recent_sessions(class_id, subject_id, teacher_id, academic_year)

        return AdminAttendanceDashboardResponse(
            kpis=AdminAttendanceKPIs(
                total_students=total_students,
                today_present=today_present,
                today_absent=today_absent,
                today_late=today_late,
                today_attendance_percentage=today_pct,
                overall_attendance_percentage=overall_pct,
                frequent_absentees_count=len(frequent_absentees),
            ),
            daily_summary=daily_summary,
            weekly_summary=weekly_summary,
            monthly_summary=monthly_summary,
            frequent_absentees=frequent_absentees,
            recent_sessions=recent_sessions,
        )

    def _compute_weekly_summary(
        self,
        class_id: Optional[int],
        subject_id: Optional[int],
        teacher_id: Optional[int],
        academic_year: Optional[str]
    ) -> List[AdminAttendanceWeeklySummaryItem]:
        today = date.today()
        eight_weeks_ago = today - timedelta(days=56)
        query = self.db.query(
            func.date_trunc("week", Attendance.date).label("week_start"),
            func.sum(case((Attendance.status.in_(["PRESENT", "LATE"]), 1), else_=0)).label("present"),
            func.sum(case((Attendance.status.in_(["ABSENT", "EXCUSED", "UNEXCUSED"]), 1), else_=0)).label("absent"),
        ).filter(
            Attendance.date >= eight_weeks_ago,
            Attendance.date <= today
        )
        if class_id:
            query = query.filter(Attendance.class_id == class_id)
        if subject_id:
            query = query.filter(Attendance.subject_id == subject_id)
        if teacher_id:
            query = query.filter(Attendance.teacher_id == teacher_id)
        if academic_year:
            years = [academic_year, academic_year.replace("/", "-"), academic_year.replace("-", "/")]
            query = query.filter(Attendance.academic_year.in_(years))

        rows = query.group_by(func.date_trunc("week", Attendance.date)).order_by(asc("week_start")).all()
        results = []
        for r in rows:
            w_start = r.week_start.date() if isinstance(r.week_start, datetime) else r.week_start
            w_end = min(w_start + timedelta(days=6), today)
            pres = r.present or 0
            ab = r.absent or 0
            tot = pres + ab
            pct = round(pres / tot * 100, 1) if tot > 0 else 0.0
            results.append(
                AdminAttendanceWeeklySummaryItem(
                    week_label=f"{w_start.strftime('%b %d')} - {w_end.strftime('%b %d')}",
                    start_date=w_start,
                    end_date=w_end,
                    present_count=pres,
                    absent_count=ab,
                    attendance_percentage=pct,
                )
            )
        return results

    def _compute_monthly_summary(
        self,
        class_id: Optional[int],
        subject_id: Optional[int],
        teacher_id: Optional[int],
        academic_year: Optional[str]
    ) -> List[AdminAttendanceMonthlySummaryItem]:
        today = date.today()
        query = self.db.query(
            func.extract("year", Attendance.date).label("yr"),
            func.extract("month", Attendance.date).label("mo"),
            func.sum(case((Attendance.status.in_(["PRESENT", "LATE"]), 1), else_=0)).label("present"),
            func.sum(case((Attendance.status.in_(["ABSENT", "EXCUSED", "UNEXCUSED"]), 1), else_=0)).label("absent"),
        ).filter(
            Attendance.date <= today
        )
        if class_id:
            query = query.filter(Attendance.class_id == class_id)
        if subject_id:
            query = query.filter(Attendance.subject_id == subject_id)
        if teacher_id:
            query = query.filter(Attendance.teacher_id == teacher_id)
        if academic_year:
            years = [academic_year, academic_year.replace("/", "-"), academic_year.replace("-", "/")]
            query = query.filter(Attendance.academic_year.in_(years))

        rows = query.group_by("yr", "mo").order_by(asc("yr"), asc("mo")).all()
        results = []
        for r in rows:
            m = int(r.mo)
            y = int(r.yr)
            pres = r.present or 0
            ab = r.absent or 0
            tot = pres + ab
            pct = round(pres / tot * 100, 1) if tot > 0 else 0.0
            results.append(
                AdminAttendanceMonthlySummaryItem(
                    month_name=f"{calendar.month_name[m]} {y}",
                    month=m,
                    year=y,
                    present_count=pres,
                    absent_count=ab,
                    attendance_percentage=pct,
                )
            )
        return results

    def _compute_recent_sessions(
        self,
        class_id: Optional[int],
        subject_id: Optional[int],
        teacher_id: Optional[int],
        academic_year: Optional[str]
    ) -> List[AdminAttendanceRecentSessionItem]:
        today = date.today()
        query = self.db.query(
            Attendance.date,
            Attendance.period,
            Attendance.class_id,
            Attendance.subject_id,
            Attendance.teacher_id,
            func.count(Attendance.id).label("total"),
            func.sum(case((Attendance.status == "PRESENT", 1), else_=0)).label("present"),
            func.sum(case((Attendance.status == "LATE", 1), else_=0)).label("late"),
            func.sum(case((Attendance.status.in_(["ABSENT", "EXCUSED", "UNEXCUSED"]), 1), else_=0)).label("absent"),
            func.max(Attendance.created_at).label("recorded_at"),
        ).filter(
            Attendance.date <= today
        )
        if class_id:
            query = query.filter(Attendance.class_id == class_id)
        if subject_id:
            query = query.filter(Attendance.subject_id == subject_id)
        if teacher_id:
            query = query.filter(Attendance.teacher_id == teacher_id)
        if academic_year:
            years = [academic_year, academic_year.replace("/", "-"), academic_year.replace("-", "/")]
            query = query.filter(Attendance.academic_year.in_(years))

        rows = query.group_by(
            Attendance.date,
            Attendance.period,
            Attendance.class_id,
            Attendance.subject_id,
            Attendance.teacher_id
        ).order_by(desc(Attendance.date), desc("recorded_at")).limit(12).all()

        # Cache lookups
        class_ids = list(set(r.class_id for r in rows))
        subj_ids = list(set(r.subject_id for r in rows))
        teacher_ids = list(set(r.teacher_id for r in rows if r.teacher_id))

        classes_map = {c.id: c.name for c in self.db.query(SchoolClass).filter(SchoolClass.id.in_(class_ids)).all()}
        subjects_map = {s.id: s.name for s in self.db.query(Subject).filter(Subject.id.in_(subj_ids)).all()}
        teachers_map = {t.id: t.full_name for t in self.db.query(Teacher).filter(Teacher.id.in_(teacher_ids)).all()}

        results = []
        for r in rows:
            tot = r.total or 0
            p = r.present or 0
            lt = r.late or 0
            pct = round((p + lt) / tot * 100, 1) if tot > 0 else 0.0
            results.append(
                AdminAttendanceRecentSessionItem(
                    date=r.date,
                    period=r.period,
                    class_id=r.class_id,
                    class_name=classes_map.get(r.class_id, f"Class {r.class_id}"),
                    subject_id=r.subject_id,
                    subject_name=subjects_map.get(r.subject_id, f"Subject {r.subject_id}"),
                    teacher_name=teachers_map.get(r.teacher_id, "Teacher"),
                    total_students=tot,
                    present_count=p,
                    late_count=lt,
                    absent_count=r.absent or 0,
                    attendance_percentage=pct,
                    recorded_at=r.recorded_at,
                )
            )
        return results

    def get_records(
        self,
        academic_year: Optional[str] = None,
        month: Optional[int] = None,
        year: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        class_id: Optional[int] = None,
        subject_id: Optional[int] = None,
        teacher_id: Optional[int] = None,
        student_id: Optional[int] = None,
        status_filter: Optional[str] = None,
        search: Optional[str] = None,
        attendance_date: Optional[date] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> AdminAttendanceRecordsListResponse:
        today = date.today()
        # Cap end_date at today to prevent future date querying
        effective_end_date = min(end_date, today) if end_date else today

        query = self.db.query(Attendance).join(Student, Attendance.student_id == Student.id).filter(
            Attendance.date <= effective_end_date
        )

        if attendance_date:
            query = query.filter(Attendance.date == attendance_date)
        elif start_date:
            query = query.filter(Attendance.date >= start_date)
        if academic_year:
            years = [academic_year, academic_year.replace("/", "-"), academic_year.replace("-", "/")]
            query = query.filter(Attendance.academic_year.in_(years))
        if month:
            query = query.filter(func.extract("month", Attendance.date) == month)
        if year:
            query = query.filter(func.extract("year", Attendance.date) == year)
        if class_id:
            query = query.filter(Attendance.class_id == class_id)
        if subject_id:
            query = query.filter(Attendance.subject_id == subject_id)
        if teacher_id:
            query = query.filter(Attendance.teacher_id == teacher_id)
        if student_id:
            query = query.filter(Attendance.student_id == student_id)
        if status_filter and status_filter.upper() != "ALL":
            query = query.filter(Attendance.status == status_filter.upper())
        if search and search.strip():
            s = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Student.first_name.ilike(s),
                    Student.last_name.ilike(s),
                    Student.middle_name.ilike(s),
                    Student.admission_number.ilike(s),
                )
            )

        total = query.count()
        offset = (page - 1) * page_size
        records = query.order_by(desc(Attendance.date), desc(Attendance.id)).offset(offset).limit(page_size).all()

        # Cache lookups
        class_ids = list(set(r.class_id for r in records))
        subj_ids = list(set(r.subject_id for r in records))
        teacher_ids = list(set(r.teacher_id for r in records if r.teacher_id))

        classes_map = {c.id: c.name for c in self.db.query(SchoolClass).filter(SchoolClass.id.in_(class_ids)).all()}
        subjects_map = {s.id: s.name for s in self.db.query(Subject).filter(Subject.id.in_(subj_ids)).all()}
        teachers_map = {t.id: t.full_name for t in self.db.query(Teacher).filter(Teacher.id.in_(teacher_ids)).all()}

        items = [
            AdminAttendanceRecordItem(
                id=r.id,
                date=r.date,
                period=r.period,
                student_id=r.student_id,
                student_name=r.student.full_name if r.student else "Student",
                admission_number=r.student.admission_number if r.student else "ADM-000",
                class_id=r.class_id,
                class_name=classes_map.get(r.class_id, f"Class {r.class_id}"),
                subject_id=r.subject_id,
                subject_name=subjects_map.get(r.subject_id, f"Subject {r.subject_id}"),
                teacher_name=teachers_map.get(r.teacher_id, "Teacher"),
                status=r.status,
                remarks=r.remarks,
                recorded_at=r.created_at,
            )
            for r in records
        ]

        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 1

        return AdminAttendanceRecordsListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    def get_class_report(
        self,
        class_id: int,
        subject_id: Optional[int] = None,
        teacher_id: Optional[int] = None,
        academic_year: Optional[str] = None,
        month: Optional[int] = None,
        year: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        attendance_date: Optional[date] = None,
    ) -> AdminClassAttendanceReportResponse:
        today = date.today()
        effective_end_date = min(end_date, today) if end_date else today

        school_cls = self.db.query(SchoolClass).filter(SchoolClass.id == class_id).first()
        if not school_cls:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class not found.")

        target_year = academic_year or school_cls.academic_year or "2026/2027"

        # Active enrolled students
        enr_query = self.db.query(StudentEnrollment).filter(
            StudentEnrollment.class_id == class_id,
            StudentEnrollment.status == "ACTIVE"
        )
        if target_year:
            years = [target_year, target_year.replace("/", "-"), target_year.replace("-", "/")]
            enr_query = enr_query.filter(StudentEnrollment.academic_year.in_(years))

        enrollments = enr_query.join(Student).order_by(Student.first_name.asc(), Student.last_name.asc()).all()
        if not enrollments:
            # Fallback to any active enrollments in class
            enrollments = self.db.query(StudentEnrollment).filter(
                StudentEnrollment.class_id == class_id,
                StudentEnrollment.status == "ACTIVE"
            ).join(Student).order_by(Student.first_name.asc(), Student.last_name.asc()).all()

        student_list = [e.student for e in enrollments if e.student]
        # Deduplicate
        seen_stds = set()
        students: List[Student] = []
        for s in student_list:
            if s.id not in seen_stds:
                seen_stds.add(s.id)
                students.append(s)

        # Base attendance query for this class
        att_query = self.db.query(Attendance).filter(
            Attendance.class_id == class_id,
            Attendance.date <= effective_end_date
        )
        if subject_id:
            att_query = att_query.filter(Attendance.subject_id == subject_id)
        if teacher_id:
            att_query = att_query.filter(Attendance.teacher_id == teacher_id)
        if attendance_date:
            att_query = att_query.filter(Attendance.date == attendance_date)
        elif start_date:
            att_query = att_query.filter(Attendance.date >= start_date)
        if target_year:
            years = [target_year, target_year.replace("/", "-"), target_year.replace("-", "/")]
            att_query = att_query.filter(Attendance.academic_year.in_(years))
        if month:
            att_query = att_query.filter(func.extract("month", Attendance.date) == month)
        if year:
            att_query = att_query.filter(func.extract("year", Attendance.date) == year)

        all_class_records = att_query.all()

        # Unique dates header
        unique_dates = sorted(list(set(r.date for r in all_class_records)))

        # Cache subjects
        sub_ids = list(set(r.subject_id for r in all_class_records))
        subjects_map = {s.id: s.name for s in self.db.query(Subject).filter(Subject.id.in_(sub_ids)).all()}

        # Group records by student
        records_by_student: Dict[int, List[Attendance]] = {}
        for r in all_class_records:
            records_by_student.setdefault(r.student_id, []).append(r)

        class_present = 0
        class_absent = 0
        class_late = 0
        total_records_count = len(all_class_records)

        student_summaries: List[AdminClassStudentAttendanceItem] = []
        for s in students:
            s_recs = records_by_student.get(s.id, [])
            p_cnt = sum(1 for r in s_recs if r.status == "PRESENT")
            l_cnt = sum(1 for r in s_recs if r.status == "LATE")
            a_cnt = sum(1 for r in s_recs if r.status in ["ABSENT", "EXCUSED", "UNEXCUSED"])
            tot = p_cnt + l_cnt + a_cnt
            pct = round((p_cnt + l_cnt) / tot * 100, 1) if tot > 0 else 0.0

            class_present += p_cnt
            class_late += l_cnt
            class_absent += a_cnt

            # Absence dates list
            absent_details = [
                AbsenceDateDetail(
                    date=r.date,
                    period=r.period,
                    subject_name=subjects_map.get(r.subject_id, "Subject"),
                    status=r.status,
                    remarks=r.remarks,
                )
                for r in sorted(s_recs, key=lambda x: x.date)
                if r.status in ["ABSENT", "EXCUSED", "UNEXCUSED"]
            ]

            # Daily status matrix map: "YYYY-MM-DD" -> status
            daily_status_map = {r.date.isoformat(): r.status for r in s_recs}

            # Subject-by-subject breakdown for this student
            s_by_sub: Dict[int, List[Attendance]] = {}
            for r in s_recs:
                s_by_sub.setdefault(r.subject_id, []).append(r)

            s_breakdown: List[StudentSubjectAttendanceBreakdown] = []
            for sub_id, sub_recs in s_by_sub.items():
                sp = sum(1 for r in sub_recs if r.status == "PRESENT")
                sl = sum(1 for r in sub_recs if r.status == "LATE")
                sa = sum(1 for r in sub_recs if r.status in ["ABSENT", "UNEXCUSED"])
                se = sum(1 for r in sub_recs if r.status == "EXCUSED")
                stot = sp + sl + sa + se
                spct = round((sp + sl) / stot * 100, 1) if stot > 0 else 0.0
                s_name = subjects_map.get(sub_id, f"Subject {sub_id}")
                s_breakdown.append(
                    StudentSubjectAttendanceBreakdown(
                        subject_id=sub_id,
                        subject_name=s_name,
                        present_count=sp,
                        absent_count=sa,
                        late_count=sl,
                        excused_count=se,
                        total_sessions=stot,
                        attendance_percentage=spct
                    )
                )
            s_breakdown.sort(key=lambda x: x.subject_name)

            student_summaries.append(
                AdminClassStudentAttendanceItem(
                    student_id=s.id,
                    student_name=s.full_name,
                    admission_number=s.admission_number,
                    gender=s.gender,
                    guardian_name=s.guardian_name,
                    guardian_phone=s.guardian_phone,
                    total_sessions=tot,
                    days_present=p_cnt,
                    days_absent=a_cnt,
                    days_late=l_cnt,
                    attendance_percentage=pct,
                    absence_dates=absent_details,
                    daily_status=daily_status_map,
                    subject_breakdown=s_breakdown,
                )
            )

        overall_class_tot = class_present + class_absent + class_late
        overall_class_pct = round((class_present + class_late) / overall_class_tot * 100, 1) if overall_class_tot > 0 else 0.0

        period_label = "All Academic Sessions"
        if subject_id and subject_id in subjects_map:
            period_label = f"Subject: {subjects_map[subject_id]}"
        elif month:
            m_name = calendar.month_name[month]
            y_name = year or today.year
            period_label = f"{m_name} {y_name}"
        elif start_date and end_date:
            period_label = f"{start_date.isoformat()} to {effective_end_date.isoformat()}"
        elif attendance_date:
            period_label = f"Date: {attendance_date.isoformat()}"

        return AdminClassAttendanceReportResponse(
            class_info=AdminClassInfo(
                id=school_cls.id,
                name=school_cls.name,
                code=school_cls.code or f"CLS-{school_cls.id}",
                academic_year=target_year,
                total_enrolled=len(students),
            ),
            summary=AdminClassAttendanceSummaryStats(
                total_sessions=len(unique_dates),
                total_records=total_records_count,
                present_count=class_present,
                absent_count=class_absent,
                late_count=class_late,
                attendance_percentage=overall_class_pct,
            ),
            students=student_summaries,
            dates_header=unique_dates,
            academic_year=target_year,
            period_label=period_label,
        )

    def get_frequent_absentees(
        self,
        class_id: Optional[int] = None,
        subject_id: Optional[int] = None,
        teacher_id: Optional[int] = None,
        academic_year: Optional[str] = None,
        month: Optional[int] = None,
        year: Optional[int] = None,
        threshold: int = 3,
        percentage_threshold: Optional[float] = None,
    ) -> List[AdminAttendanceFrequentAbsenteeItem]:
        today = date.today()
        query = self.db.query(Attendance).join(Student, Attendance.student_id == Student.id).filter(
            Attendance.date <= today
        )
        if class_id:
            query = query.filter(Attendance.class_id == class_id)
        if subject_id:
            query = query.filter(Attendance.subject_id == subject_id)
        if teacher_id:
            query = query.filter(Attendance.teacher_id == teacher_id)
        if academic_year:
            years = [academic_year, academic_year.replace("/", "-"), academic_year.replace("-", "/")]
            query = query.filter(Attendance.academic_year.in_(years))
        if month:
            query = query.filter(func.extract("month", Attendance.date) == month)
        if year:
            query = query.filter(func.extract("year", Attendance.date) == year)

        records = query.all()
        if not records:
            return []

        # Cache lookups
        sub_ids = list(set(r.subject_id for r in records))
        cls_ids = list(set(r.class_id for r in records))
        subjects_map = {s.id: s.name for s in self.db.query(Subject).filter(Subject.id.in_(sub_ids)).all()}
        classes_map = {c.id: c.name for c in self.db.query(SchoolClass).filter(SchoolClass.id.in_(cls_ids)).all()}

        # Group by student
        by_student: Dict[int, List[Attendance]] = {}
        for r in records:
            by_student.setdefault(r.student_id, []).append(r)

        result: List[AdminAttendanceFrequentAbsenteeItem] = []
        for s_id, s_recs in by_student.items():
            first_rec = s_recs[0]
            student = first_rec.student
            if not student:
                continue

            p_cnt = sum(1 for r in s_recs if r.status == "PRESENT")
            l_cnt = sum(1 for r in s_recs if r.status == "LATE")
            a_cnt = sum(1 for r in s_recs if r.status in ["ABSENT", "EXCUSED", "UNEXCUSED"])
            tot = p_cnt + l_cnt + a_cnt
            pct = round((p_cnt + l_cnt) / tot * 100, 1) if tot > 0 else 0.0

            # Check threshold
            exceeds_absent_count = a_cnt >= threshold
            exceeds_pct = percentage_threshold is not None and pct < percentage_threshold

            if exceeds_absent_count or exceeds_pct:
                absent_recs = [r for r in sorted(s_recs, key=lambda x: x.date, reverse=True) if r.status in ["ABSENT", "EXCUSED", "UNEXCUSED"]]
                last_absent_date = absent_recs[0].date if absent_recs else None
                absent_details = [
                    AbsenceDateDetail(
                        date=r.date,
                        period=r.period,
                        subject_name=subjects_map.get(r.subject_id, "Subject"),
                        status=r.status,
                        remarks=r.remarks,
                    )
                    for r in absent_recs
                ]

                result.append(
                    AdminAttendanceFrequentAbsenteeItem(
                        student_id=student.id,
                        student_name=student.full_name,
                        admission_number=student.admission_number,
                        class_id=first_rec.class_id,
                        class_name=classes_map.get(first_rec.class_id, f"Class {first_rec.class_id}"),
                        gender=student.gender,
                        guardian_name=student.guardian_name,
                        guardian_phone=student.guardian_phone,
                        total_sessions=tot,
                        present_count=p_cnt,
                        absent_count=a_cnt,
                        late_count=l_cnt,
                        attendance_percentage=pct,
                        last_absent_date=last_absent_date,
                        absence_dates=absent_details,
                    )
                )

        # Rank by total absences descending, then lowest attendance %
        result.sort(key=lambda x: (-x.absent_count, x.attendance_percentage))
        return result

    def get_student_breakdown(
        self,
        student_id: int,
        academic_year: Optional[str] = None
    ) -> StudentAttendanceHistoryDetailResponse:
        student = self.db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")

        enrollment = self.db.query(StudentEnrollment).filter(
            StudentEnrollment.student_id == student_id,
            StudentEnrollment.status == "ACTIVE"
        ).first()

        school_class = enrollment.school_class if enrollment else None
        target_year = academic_year or (enrollment.academic_year if enrollment else "2026/2027")

        today = date.today()
        query = self.db.query(Attendance).filter(
            Attendance.student_id == student_id,
            Attendance.date <= today
        )
        if target_year:
            years = [target_year, target_year.replace("/", "-"), target_year.replace("-", "/")]
            query = query.filter(Attendance.academic_year.in_(years))

        records = query.order_by(Attendance.date.desc(), Attendance.id.desc()).all()

        sub_ids = list(set(r.subject_id for r in records))
        subjects_map = {s.id: s for s in self.db.query(Subject).filter(Subject.id.in_(sub_ids)).all()}

        by_sub: Dict[int, List[Attendance]] = {}
        for r in records:
            by_sub.setdefault(r.subject_id, []).append(r)

        breakdown: List[StudentSubjectAttendanceBreakdown] = []
        tot_p = 0
        tot_a = 0
        tot_l = 0
        tot_s = len(records)

        for s_id, s_recs in by_sub.items():
            subj = subjects_map.get(s_id)
            sub_name = subj.name if subj else f"Subject {s_id}"
            sub_code = subj.code if subj else None
            p = sum(1 for r in s_recs if r.status == "PRESENT")
            l = sum(1 for r in s_recs if r.status == "LATE")
            a = sum(1 for r in s_recs if r.status in ["ABSENT", "UNEXCUSED"])
            exc = sum(1 for r in s_recs if r.status == "EXCUSED")
            tot = p + l + a + exc
            pct = round(((p + l) / tot * 100), 1) if tot > 0 else 0.0

            tot_p += p
            tot_l += l
            tot_a += (a + exc)

            breakdown.append(
                StudentSubjectAttendanceBreakdown(
                    subject_id=s_id,
                    subject_name=sub_name,
                    subject_code=sub_code,
                    present_count=p,
                    absent_count=a,
                    late_count=l,
                    excused_count=exc,
                    total_sessions=tot,
                    attendance_percentage=pct
                )
            )

        breakdown.sort(key=lambda x: x.subject_name)
        overall_pct = round(((tot_p + tot_l) / tot_s * 100), 1) if tot_s > 0 else 0.0

        history_items = [
            AttendanceRecordResponse(
                id=r.id,
                date=r.date,
                subject_id=r.subject_id,
                subject_name=r.subject.name if r.subject else f"Subject {r.subject_id}",
                subject_code=r.subject.code if r.subject else None,
                period=r.period,
                status=r.status,
                teacher_name=r.teacher.full_name if r.teacher else None,
                remarks=r.remarks
            )
            for r in records
        ]

        class_id = school_class.id if school_class else (enrollment.class_id if enrollment else 0)
        class_name = school_class.name if school_class else (f"Class {enrollment.class_id}" if enrollment else "Unassigned")

        return StudentAttendanceHistoryDetailResponse(
            student_id=student.id,
            student_name=student.full_name,
            admission_number=student.admission_number,
            class_id=class_id,
            class_name=class_name,
            academic_year=target_year,
            total_sessions=tot_s,
            total_present=tot_p,
            total_absent=tot_a,
            total_late=tot_l,
            overall_percentage=overall_pct,
            by_subject=breakdown,
            records=history_items
        )

    def export_excel(
        self,
        report_type: str,
        class_id: Optional[int] = None,
        subject_id: Optional[int] = None,
        teacher_id: Optional[int] = None,
        academic_year: Optional[str] = None,
        month: Optional[int] = None,
        year: Optional[int] = None,
        threshold: int = 3,
    ) -> bytes:
        school = self.get_school_metadata()
        wb = openpyxl.Workbook()
        ws = wb.active

        # Enterprise Styles
        navy_fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
        header_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
        alt_row_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
        white_fill = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
        warning_fill = PatternFill(start_color="FEF2F2", end_color="FEF2F2", fill_type="solid")

        white_bold_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        title_font = Font(name="Calibri", size=15, bold=True, color="0F172A")
        sub_font = Font(name="Calibri", size=10, italic=True, color="64748B")
        meta_bold = Font(name="Calibri", size=10, bold=True, color="0F172A")
        meta_normal = Font(name="Calibri", size=10, color="334155")
        cell_font = Font(name="Calibri", size=10, color="1E293B")
        cell_bold = Font(name="Calibri", size=10, bold=True, color="0F172A")
        alert_font = Font(name="Calibri", size=10, bold=True, color="DC2626")
        success_font = Font(name="Calibri", size=10, bold=True, color="16A34A")

        thin_side = Side(border_style="thin", color="CBD5E1")
        cell_border = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)

        center_align = Alignment(horizontal="center", vertical="center")
        left_align = Alignment(horizontal="left", vertical="center")
        right_align = Alignment(horizontal="right", vertical="center")

        target_subj = self.db.query(Subject).filter(Subject.id == subject_id).first() if subject_id else None

        if report_type == "class_report" and class_id:
            ws.title = "Class Attendance Report"
            report = self.get_class_report(
                class_id=class_id,
                subject_id=subject_id,
                teacher_id=teacher_id,
                academic_year=academic_year,
                month=month,
                year=year
            )

            # Header
            ws.merge_cells("A1:J1")
            ws["A1"] = school["name"].upper()
            ws["A1"].font = title_font
            ws["A1"].alignment = left_align

            ws.merge_cells("A2:J2")
            subj_subtitle = f" • Subject: {target_subj.name}" if target_subj else ""
            ws["A2"] = f"Official Class Attendance & Absence Report{subj_subtitle} • {school['motto']}"
            ws["A2"].font = sub_font
            ws["A2"].alignment = left_align

            # Metadata block
            ws["A4"] = "Class:"
            ws["A4"].font = meta_bold
            ws["B4"] = report.class_info.name
            ws["B4"].font = meta_normal

            ws["D4"] = "Academic Year:"
            ws["D4"].font = meta_bold
            ws["E4"] = report.academic_year
            ws["E4"].font = meta_normal

            ws["A5"] = "Reporting Period:"
            ws["A5"].font = meta_bold
            ws["B5"] = report.period_label
            ws["B5"].font = meta_normal

            ws["D5"] = "Class Attendance Rate:"
            ws["D5"].font = meta_bold
            ws["E5"] = f"{report.summary.attendance_percentage}%"
            ws["E5"].font = meta_bold

            ws["G4"] = "Total Enrolled:"
            ws["G4"].font = meta_bold
            ws["H4"] = report.class_info.total_enrolled
            ws["H4"].font = meta_normal

            ws["G5"] = "Report Generated:"
            ws["G5"].font = meta_bold
            ws["H5"] = date.today().isoformat()
            ws["H5"].font = meta_normal

            if target_subj:
                ws["A6"] = "Subject:"
                ws["A6"].font = meta_bold
                ws["B6"] = f"{target_subj.name} ({target_subj.code})"
                ws["B6"].font = meta_bold

            # Table Header
            headers = [
                "#", "Admission No", "Student Name", "Gender",
                "Total Sessions", "Days Present", "Days Late", "Days Absent", "Attendance %", "Absence Dates"
            ]
            row_idx = 8 if target_subj else 7
            for col_idx, h in enumerate(headers, 1):
                cell = ws.cell(row=row_idx, column=col_idx, value=h)
                cell.font = white_bold_font
                cell.fill = header_fill
                cell.alignment = center_align if col_idx in [1, 2, 4, 5, 6, 7, 8, 9] else left_align
                cell.border = cell_border
            ws.row_dimensions[row_idx].height = 24

            # Data rows
            for i, st in enumerate(report.students, 1):
                row_idx += 1
                is_alt = (i % 2 == 0)
                is_high_absent = st.days_absent >= threshold
                r_fill = warning_fill if is_high_absent else (alt_row_fill if is_alt else white_fill)

                abs_dates_str = ", ".join([d.date.strftime("%d/%m") for d in st.absence_dates]) or "None"

                row_vals = [
                    (i, center_align, cell_font),
                    (st.admission_number, center_align, cell_bold),
                    (st.student_name, left_align, cell_font),
                    (st.gender or "—", center_align, cell_font),
                    (st.total_sessions, center_align, cell_font),
                    (st.days_present, center_align, success_font),
                    (st.days_late, center_align, cell_bold),
                    (st.days_absent, center_align, alert_font if st.days_absent > 0 else cell_font),
                    (f"{st.attendance_percentage}%", center_align, alert_font if st.attendance_percentage < 80 else cell_bold),
                    (abs_dates_str, left_align, cell_font),
                ]

                for col_idx, (val, align, font) in enumerate(row_vals, 1):
                    cell = ws.cell(row=row_idx, column=col_idx, value=val)
                    cell.alignment = align
                    cell.font = font
                    cell.fill = r_fill
                    cell.border = cell_border

            # Auto fit widths
            for col in ws.columns:
                max_len = max(len(str(cell.value or '')) for cell in col)
                col_letter = get_column_letter(col[0].column)
                ws.column_dimensions[col_letter].width = max(max_len + 3, 11)

        else:
            # Frequent absentees report
            ws.title = "Frequent Absentees"
            absentees = self.get_frequent_absentees(
                class_id=class_id,
                subject_id=subject_id,
                teacher_id=teacher_id,
                academic_year=academic_year,
                month=month,
                year=year,
                threshold=threshold,
            )

            ws.merge_cells("A1:H1")
            ws["A1"] = school["name"].upper()
            ws["A1"].font = title_font
            ws["A1"].alignment = left_align

            ws.merge_cells("A2:H2")
            subj_subtitle = f" • Subject: {target_subj.name}" if target_subj else ""
            ws["A2"] = f"Frequent Absentees & Intervention Audit Report{subj_subtitle} • Threshold: >= {threshold} Absences"
            ws["A2"].font = sub_font
            ws["A2"].alignment = left_align

            # Metadata
            ws["A4"] = "Academic Year:"
            ws["A4"].font = meta_bold
            ws["B4"] = academic_year or school["academic_year"]
            ws["B4"].font = meta_normal

            ws["D4"] = "Absence Threshold:"
            ws["D4"].font = meta_bold
            ws["E4"] = f">= {threshold} unexcused absences"
            ws["E4"].font = meta_bold

            ws["G4"] = "Flagged Students:"
            ws["G4"].font = meta_bold
            ws["H4"] = len(absentees)
            ws["H4"].font = alert_font

            if target_subj:
                ws["A5"] = "Subject Scoped:"
                ws["A5"].font = meta_bold
                ws["B5"] = target_subj.name
                ws["B5"].font = meta_bold

            headers = [
                "Rank", "Admission No", "Student Name", "Class",
                "Total Absences", "Attendance %", "Guardian Contact", "Absence Dates History"
            ]
            row_idx = 7 if target_subj else 6
            for col_idx, h in enumerate(headers, 1):
                cell = ws.cell(row=row_idx, column=col_idx, value=h)
                cell.font = white_bold_font
                cell.fill = navy_fill
                cell.alignment = center_align if col_idx in [1, 2, 5, 6] else left_align
                cell.border = cell_border
            ws.row_dimensions[row_idx].height = 24

            for i, st in enumerate(absentees, 1):
                row_idx += 1
                is_alt = (i % 2 == 0)
                r_fill = alt_row_fill if is_alt else white_fill
                abs_dates_str = ", ".join([f"{d.date.strftime('%b %d')} ({d.subject_name})" for d in st.absence_dates[:6]])

                guardian_info = f"{st.guardian_name or ''} {st.guardian_phone or ''}".strip() or "—"

                row_vals = [
                    (i, center_align, cell_bold),
                    (st.admission_number, center_align, cell_bold),
                    (st.student_name, left_align, cell_font),
                    (st.class_name, left_align, cell_font),
                    (st.absent_count, center_align, alert_font),
                    (f"{st.attendance_percentage}%", center_align, alert_font),
                    (guardian_info, left_align, cell_font),
                    (abs_dates_str, left_align, cell_font),
                ]

                for col_idx, (val, align, font) in enumerate(row_vals, 1):
                    cell = ws.cell(row=row_idx, column=col_idx, value=val)
                    cell.alignment = align
                    cell.font = font
                    cell.fill = r_fill
                    cell.border = cell_border

            for col in ws.columns:
                max_len = max(len(str(cell.value or '')) for cell in col)
                col_letter = get_column_letter(col[0].column)
                ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

        output = io.BytesIO()
        wb.save(output)
        return output.getvalue()

    def export_pdf(
        self,
        report_type: str,
        class_id: Optional[int] = None,
        subject_id: Optional[int] = None,
        teacher_id: Optional[int] = None,
        academic_year: Optional[str] = None,
        month: Optional[int] = None,
        year: Optional[int] = None,
        threshold: int = 3,
    ) -> bytes:
        school = self.get_school_metadata()
        target_subj = self.db.query(Subject).filter(Subject.id == subject_id).first() if subject_id else None
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=25,
            leftMargin=25,
            topMargin=25,
            bottomMargin=30,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontSize=16,
            leading=20,
            textColor=colors.HexColor("#0f172a"),
            fontName="Helvetica-Bold",
        )
        subtitle_style = ParagraphStyle(
            "DocSubTitle",
            parent=styles["Normal"],
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#64748b"),
            fontName="Helvetica-Oblique",
        )
        meta_label_style = ParagraphStyle(
            "MetaLabel",
            parent=styles["Normal"],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#0f172a"),
            fontName="Helvetica-Bold",
        )
        meta_val_style = ParagraphStyle(
            "MetaVal",
            parent=styles["Normal"],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#334155"),
            fontName="Helvetica",
        )
        th_style = ParagraphStyle(
            "TH",
            parent=styles["Normal"],
            fontSize=8.5,
            leading=11,
            textColor=colors.white,
            fontName="Helvetica-Bold",
            alignment=1,
        )
        td_style = ParagraphStyle(
            "TD",
            parent=styles["Normal"],
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#1e293b"),
            fontName="Helvetica",
        )
        td_bold_style = ParagraphStyle(
            "TDBold",
            parent=styles["Normal"],
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#0f172a"),
            fontName="Helvetica-Bold",
            alignment=1,
        )
        td_alert_style = ParagraphStyle(
            "TDAlert",
            parent=styles["Normal"],
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#dc2626"),
            fontName="Helvetica-Bold",
            alignment=1,
        )
        td_success_style = ParagraphStyle(
            "TDSuccess",
            parent=styles["Normal"],
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#16a34a"),
            fontName="Helvetica-Bold",
            alignment=1,
        )

        story = []

        # 1. Header Banner
        school_name = school["name"].upper()
        story.append(Paragraph(school_name, title_style))
        subj_suffix = f" • Subject: {target_subj.name}" if target_subj else ""
        if report_type == "class_report":
            story.append(Paragraph(f"Official Class Attendance & Absence Report{subj_suffix} • {school['motto']}", subtitle_style))
        else:
            story.append(Paragraph(f"Frequent Absence Detection & Intervention Report{subj_suffix} • Threshold: >= {threshold} Absences", subtitle_style))
        story.append(Spacer(1, 10))

        if report_type == "class_report" and class_id:
            report = self.get_class_report(
                class_id=class_id,
                subject_id=subject_id,
                teacher_id=teacher_id,
                academic_year=academic_year,
                month=month,
                year=year
            )

            # Metadata Table
            meta_data = [
                [
                    Paragraph("<b>Class:</b>", meta_label_style),
                    Paragraph(report.class_info.name, meta_val_style),
                    Paragraph("<b>Academic Year:</b>", meta_label_style),
                    Paragraph(report.academic_year, meta_val_style),
                    Paragraph("<b>Enrolled Students:</b>", meta_label_style),
                    Paragraph(str(report.class_info.total_enrolled), meta_val_style),
                ],
                [
                    Paragraph("<b>Period:</b>", meta_label_style),
                    Paragraph(report.period_label, meta_val_style),
                    Paragraph("<b>Attendance Rate:</b>", meta_label_style),
                    Paragraph(f"<b>{report.summary.attendance_percentage}%</b>", meta_label_style),
                    Paragraph("<b>Date Generated:</b>", meta_label_style),
                    Paragraph(date.today().isoformat(), meta_val_style),
                ],
            ]
            if target_subj:
                meta_data.append([
                    Paragraph("<b>Subject:</b>", meta_label_style),
                    Paragraph(f"{target_subj.name} ({target_subj.code})", meta_val_style),
                    Paragraph("", meta_val_style),
                    Paragraph("", meta_val_style),
                    Paragraph("", meta_val_style),
                    Paragraph("", meta_val_style),
                ])
            meta_table = Table(meta_data, colWidths=[90, 160, 100, 140, 110, 140])
            meta_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ("PADDING", (0, 0), (-1, -1), 4),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]))
            story.append(meta_table)
            story.append(Spacer(1, 12))

            # Student table
            table_data = [[
                Paragraph("#", th_style),
                Paragraph("Adm No", th_style),
                Paragraph("Student Name", th_style),
                Paragraph("Gender", th_style),
                Paragraph("Sessions", th_style),
                Paragraph("Present", th_style),
                Paragraph("Late", th_style),
                Paragraph("Absent", th_style),
                Paragraph("Rate %", th_style),
                Paragraph("Absence Dates (Subject)", th_style),
            ]]

            for idx, st in enumerate(report.students, 1):
                abs_str = ", ".join([f"{d.date.strftime('%d/%m')} ({d.subject_name[:10]})" for d in st.absence_dates[:6]]) or "—"
                is_alert = st.days_absent >= threshold

                table_data.append([
                    Paragraph(str(idx), td_bold_style),
                    Paragraph(st.admission_number, td_bold_style),
                    Paragraph(st.student_name, td_style),
                    Paragraph(st.gender or "—", td_style),
                    Paragraph(str(st.total_sessions), td_bold_style),
                    Paragraph(str(st.days_present), td_success_style),
                    Paragraph(str(st.days_late), td_bold_style),
                    Paragraph(str(st.days_absent), td_alert_style if st.days_absent > 0 else td_bold_style),
                    Paragraph(f"{st.attendance_percentage}%", td_alert_style if is_alert else td_bold_style),
                    Paragraph(abs_str, td_style),
                ])

            t = Table(table_data, colWidths=[25, 75, 150, 45, 50, 50, 45, 50, 55, 245], repeatRows=1)
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]))
            story.append(t)

        else:
            # Frequent absentees
            absentees = self.get_frequent_absentees(
                class_id=class_id,
                subject_id=subject_id,
                teacher_id=teacher_id,
                academic_year=academic_year,
                month=month,
                year=year,
                threshold=threshold,
            )

            meta_data = [
                [
                    Paragraph("<b>Academic Year:</b>", meta_label_style),
                    Paragraph(academic_year or school["academic_year"], meta_val_style),
                    Paragraph("<b>Absence Threshold:</b>", meta_label_style),
                    Paragraph(f"<b>&ge; {threshold} absences</b>", meta_label_style),
                    Paragraph("<b>Flagged Students:</b>", meta_label_style),
                    Paragraph(f"<b>{len(absentees)}</b>", meta_label_style),
                ]
            ]
            if target_subj:
                meta_data.append([
                    Paragraph("<b>Subject:</b>", meta_label_style),
                    Paragraph(f"{target_subj.name} ({target_subj.code})", meta_val_style),
                    Paragraph("", meta_val_style),
                    Paragraph("", meta_val_style),
                    Paragraph("", meta_val_style),
                    Paragraph("", meta_val_style),
                ])
            meta_table = Table(meta_data, colWidths=[110, 150, 120, 140, 110, 110])
            meta_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fef2f2")),
                ("PADDING", (0, 0), (-1, -1), 5),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#fca5a5")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]))
            story.append(meta_table)
            story.append(Spacer(1, 12))

            table_data = [[
                Paragraph("Rank", th_style),
                Paragraph("Adm No", th_style),
                Paragraph("Student Name", th_style),
                Paragraph("Class", th_style),
                Paragraph("Absences", th_style),
                Paragraph("Rate %", th_style),
                Paragraph("Guardian Contact", th_style),
                Paragraph("Recorded Absence Dates & Subjects", th_style),
            ]]

            for idx, st in enumerate(absentees, 1):
                abs_str = ", ".join([f"{d.date.strftime('%b %d')} ({d.subject_name})" for d in st.absence_dates[:5]])
                g_info = f"{st.guardian_name or ''} {st.guardian_phone or ''}".strip() or "—"

                table_data.append([
                    Paragraph(str(idx), td_bold_style),
                    Paragraph(st.admission_number, td_bold_style),
                    Paragraph(st.student_name, td_style),
                    Paragraph(st.class_name, td_style),
                    Paragraph(str(st.absent_count), td_alert_style),
                    Paragraph(f"{st.attendance_percentage}%", td_alert_style),
                    Paragraph(g_info, td_style),
                    Paragraph(abs_str, td_style),
                ])

            t = Table(table_data, colWidths=[35, 80, 140, 90, 60, 55, 120, 200], repeatRows=1)
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fef2f2")]),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]))
            story.append(t)

        # Signature Footer
        story.append(Spacer(1, 15))
        sig_data = [
            [
                Paragraph("<b>Prepared By:</b> Attendance Office", meta_val_style),
                Paragraph("<b>Reviewed By:</b> Principal / Head of School", meta_val_style),
                Paragraph("<b>Official School Seal:</b> ____________________", meta_val_style),
            ]
        ]
        sig_table = Table(sig_data, colWidths=[250, 270, 260])
        sig_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(sig_table)

        doc.build(story, canvasmaker=AttendanceNumberedCanvas)
        return buffer.getvalue()

        # Signature Footer
        story.append(Spacer(1, 15))
        sig_data = [
            [
                Paragraph("<b>Prepared By:</b> Attendance Office", meta_val_style),
                Paragraph("<b>Reviewed By:</b> Principal / Head of School", meta_val_style),
                Paragraph("<b>Official School Seal:</b> ____________________", meta_val_style),
            ]
        ]
        sig_table = Table(sig_data, colWidths=[250, 270, 260])
        sig_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(sig_table)

        doc.build(story, canvasmaker=AttendanceNumberedCanvas)
        return buffer.getvalue()
