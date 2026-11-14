import io
import calendar
from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc, case, or_
from fastapi import HTTPException, status

from app.models.teacher import Teacher
from app.models.teacher_attendance import TeacherAttendance
from app.models.user import User
from app.models.audit_log import AuditLog
from app.models.system_setting import SystemSetting
from app.schemas.admin_teacher_attendance import (
    TeacherRosterAttendanceItem,
    TeacherDailyRosterResponse,
    TeacherBulkSavePayload,
    TeacherAttendanceKPIs,
    TeacherAttendanceDailySummaryItem,
    TeacherAttendanceMonthlySummaryItem,
    TeacherAttendanceDashboardResponse,
    TeacherAttendanceRecordItem,
    TeacherAttendanceRecordsResponse,
    TeacherStaffAttendanceSummaryItem,
    StaffAttendanceSummaryResponse,
)

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas


class TeacherAttendanceNumberedCanvas(canvas.Canvas):
    """Two-pass canvas for total page numbering and official staff audit document footer."""
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
        self.drawString(25, 14, "SOMROYAL EMS — OFFICIAL FACULTY & STAFF ATTENDANCE MONITORING RECORD")

        page_str = f"Page {self._pageNumber} of {total_pages}"
        self.drawRightString(self._pagesize[0] - 25, 14, page_str)
        self.restoreState()


class AdminTeacherAttendanceService:
    """Service providing School Admin recording, tracking, and reporting for Faculty & Staff Attendance."""

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

    def get_daily_roster(
        self,
        attendance_date: date,
        academic_year: Optional[str] = None
    ) -> TeacherDailyRosterResponse:
        today = date.today()
        if attendance_date > today:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Teacher attendance date cannot be in the future (Today is {today.isoformat()})."
            )

        school = self.get_school_metadata()
        target_year = academic_year or school["academic_year"]

        # Fetch ALL registered teachers for the school (sorted alphabetically by name)
        teachers = self.db.query(Teacher).order_by(Teacher.first_name.asc(), Teacher.last_name.asc()).all()

        # Lookup existing attendance for this date
        existing_records = self.db.query(TeacherAttendance).filter(
            TeacherAttendance.date == attendance_date
        ).all()
        rec_map: Dict[int, TeacherAttendance] = {r.teacher_id: r for r in existing_records}
        is_recorded = len(existing_records) > 0

        roster_items: List[TeacherRosterAttendanceItem] = []
        present_cnt = 0
        absent_cnt = 0
        late_cnt = 0
        on_leave_cnt = 0

        for t in teachers:
            existing = rec_map.get(t.id)
            if existing:
                st = existing.status.upper()
                rsn = existing.reason
                att_id = existing.id
                saved = True
            else:
                # Default for new daily sheet: default to PRESENT or ON_LEAVE if teacher status is ON_LEAVE
                st = "ON_LEAVE" if t.status == "ON_LEAVE" else "PRESENT"
                rsn = "Approved Leave" if t.status == "ON_LEAVE" else None
                att_id = None
                saved = False

            if st == "PRESENT":
                present_cnt += 1
            elif st == "LATE":
                late_cnt += 1
            elif st == "ON_LEAVE":
                on_leave_cnt += 1
            else:
                absent_cnt += 1

            roster_items.append(
                TeacherRosterAttendanceItem(
                    teacher_id=t.id,
                    teacher_number=t.teacher_number,
                    teacher_name=t.full_name,
                    gender=t.gender,
                    phone=t.phone,
                    email=t.email,
                    qualification=t.qualification,
                    employment_status=t.status,
                    status=st,
                    reason=rsn,
                    attendance_id=att_id,
                    is_saved=saved,
                )
            )

        return TeacherDailyRosterResponse(
            date=attendance_date,
            academic_year=target_year,
            is_recorded=is_recorded,
            total_teachers=len(roster_items),
            present_count=present_cnt,
            absent_count=absent_cnt,
            late_count=late_cnt,
            on_leave_count=on_leave_cnt,
            teachers=roster_items,
        )

    def save_daily_attendance(
        self,
        admin_user: User,
        payload: TeacherBulkSavePayload
    ) -> Dict[str, Any]:
        today = date.today()
        if payload.date > today:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Teacher attendance cannot be recorded for future dates (Today is {today.isoformat()})."
            )

        if not payload.entries:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Teacher attendance entries cannot be empty."
            )

        # Existing records on this date
        existing_records = self.db.query(TeacherAttendance).filter(
            TeacherAttendance.date == payload.date
        ).all()
        rec_map = {r.teacher_id: r for r in existing_records}

        valid_statuses = {"PRESENT", "ABSENT", "LATE", "ON_LEAVE"}
        saved_count = 0
        present_cnt = 0
        absent_cnt = 0
        late_cnt = 0
        on_leave_cnt = 0

        # Deduplicate payload entries by teacher_id
        unique_entries = {e.teacher_id: e for e in payload.entries}

        for entry in unique_entries.values():
            st = entry.status.upper() if entry.status else "PRESENT"
            if st not in valid_statuses:
                st = "PRESENT"

            if st == "PRESENT":
                present_cnt += 1
            elif st == "LATE":
                late_cnt += 1
            elif st == "ON_LEAVE":
                on_leave_cnt += 1
            else:
                absent_cnt += 1

            rsn = entry.reason.strip() if entry.reason else None

            existing = rec_map.get(entry.teacher_id)
            if existing:
                existing.status = st
                existing.reason = rsn
                existing.academic_year = payload.academic_year
                existing.recorded_by_id = admin_user.id
            else:
                new_rec = TeacherAttendance(
                    teacher_id=entry.teacher_id,
                    date=payload.date,
                    academic_year=payload.academic_year,
                    status=st,
                    reason=rsn,
                    recorded_by_id=admin_user.id,
                )
                self.db.add(new_rec)

            saved_count += 1

        # Audit Log
        audit = AuditLog(
            user_id=admin_user.id,
            action="SAVE_TEACHER_ATTENDANCE",
            status="SUCCESS",
            details={
                "date": payload.date.isoformat(),
                "academic_year": payload.academic_year,
                "total_teachers_marked": saved_count,
                "present_count": present_cnt,
                "absent_count": absent_cnt,
                "late_count": late_cnt,
                "on_leave_count": on_leave_cnt,
            }
        )
        self.db.add(audit)
        self.db.commit()

        return {
            "message": "Teacher attendance recorded and persisted successfully.",
            "date": payload.date.isoformat(),
            "academic_year": payload.academic_year,
            "total_saved": saved_count,
            "present_count": present_cnt,
            "absent_count": absent_cnt,
            "late_count": late_cnt,
            "on_leave_count": on_leave_cnt,
        }

    def get_dashboard(
        self,
        academic_year: Optional[str] = None,
        month: Optional[int] = None,
        year: Optional[int] = None
    ) -> TeacherAttendanceDashboardResponse:
        today = date.today()

        # Total teachers
        total_teachers = self.db.query(Teacher).count()

        # Today's attendance
        today_records = self.db.query(TeacherAttendance).filter(
            TeacherAttendance.date == today
        ).all()
        today_p = sum(1 for r in today_records if r.status == "PRESENT")
        today_l = sum(1 for r in today_records if r.status == "LATE")
        today_a = sum(1 for r in today_records if r.status == "ABSENT")
        today_leave = sum(1 for r in today_records if r.status == "ON_LEAVE")
        today_total_marked = len(today_records)
        today_pct = round((today_p + today_l) / today_total_marked * 100, 1) if today_total_marked > 0 else 0.0

        # Overall in filter
        query = self.db.query(TeacherAttendance).filter(TeacherAttendance.date <= today)
        if academic_year:
            years = [academic_year, academic_year.replace("/", "-"), academic_year.replace("-", "/")]
            query = query.filter(TeacherAttendance.academic_year.in_(years))
        if month:
            query = query.filter(func.extract("month", TeacherAttendance.date) == month)
        if year:
            query = query.filter(func.extract("year", TeacherAttendance.date) == year)

        overall_records = query.all()
        tot_p = sum(1 for r in overall_records if r.status == "PRESENT")
        tot_l = sum(1 for r in overall_records if r.status == "LATE")
        tot_all = len(overall_records)
        overall_pct = round((tot_p + tot_l) / tot_all * 100, 1) if tot_all > 0 else 0.0

        # 14-day daily summary
        daily_rows = self.db.query(
            TeacherAttendance.date,
            func.sum(case((TeacherAttendance.status == "PRESENT", 1), else_=0)).label("present"),
            func.sum(case((TeacherAttendance.status == "ABSENT", 1), else_=0)).label("absent"),
            func.sum(case((TeacherAttendance.status == "LATE", 1), else_=0)).label("late"),
            func.sum(case((TeacherAttendance.status == "ON_LEAVE", 1), else_=0)).label("on_leave"),
        ).filter(
            TeacherAttendance.date <= today
        )
        if academic_year:
            years = [academic_year, academic_year.replace("/", "-"), academic_year.replace("-", "/")]
            daily_rows = daily_rows.filter(TeacherAttendance.academic_year.in_(years))
        if month:
            daily_rows = daily_rows.filter(func.extract("month", TeacherAttendance.date) == month)
        if year:
            daily_rows = daily_rows.filter(func.extract("year", TeacherAttendance.date) == year)

        daily_rows = daily_rows.group_by(TeacherAttendance.date).order_by(desc(TeacherAttendance.date)).limit(14).all()
        daily_rows.reverse()

        daily_summary = [
            TeacherAttendanceDailySummaryItem(
                date=r.date,
                day_name=r.date.strftime("%a"),
                present_count=r.present or 0,
                absent_count=r.absent or 0,
                late_count=r.late or 0,
                on_leave_count=r.on_leave or 0,
                attendance_percentage=round(((r.present or 0) + (r.late or 0)) / ((r.present or 0) + (r.absent or 0) + (r.late or 0) + (r.on_leave or 0)) * 100, 1)
                if ((r.present or 0) + (r.absent or 0) + (r.late or 0) + (r.on_leave or 0)) > 0 else 0.0,
            )
            for r in daily_rows
        ]

        # Monthly summary
        m_query = self.db.query(
            func.extract("year", TeacherAttendance.date).label("yr"),
            func.extract("month", TeacherAttendance.date).label("mo"),
            func.sum(case((TeacherAttendance.status == "PRESENT", 1), else_=0)).label("present"),
            func.sum(case((TeacherAttendance.status == "ABSENT", 1), else_=0)).label("absent"),
            func.sum(case((TeacherAttendance.status == "LATE", 1), else_=0)).label("late"),
            func.sum(case((TeacherAttendance.status == "ON_LEAVE", 1), else_=0)).label("on_leave"),
        ).filter(TeacherAttendance.date <= today)

        if academic_year:
            years = [academic_year, academic_year.replace("/", "-"), academic_year.replace("-", "/")]
            m_query = m_query.filter(TeacherAttendance.academic_year.in_(years))

        m_rows = m_query.group_by("yr", "mo").order_by(asc("yr"), asc("mo")).all()
        monthly_summary = []
        for r in m_rows:
            mo = int(r.mo)
            yr = int(r.yr)
            p = r.present or 0
            l = r.late or 0
            a = r.absent or 0
            lv = r.on_leave or 0
            tot = p + l + a + lv
            pct = round((p + l) / tot * 100, 1) if tot > 0 else 0.0
            monthly_summary.append(
                TeacherAttendanceMonthlySummaryItem(
                    month_name=f"{calendar.month_name[mo]} {yr}",
                    month=mo,
                    year=yr,
                    present_count=p,
                    absent_count=a,
                    late_count=l,
                    on_leave_count=lv,
                    attendance_percentage=pct,
                )
            )

        return TeacherAttendanceDashboardResponse(
            kpis=TeacherAttendanceKPIs(
                total_teachers=total_teachers,
                today_present=today_p,
                today_absent=today_a,
                today_late=today_l,
                today_on_leave=today_leave,
                today_attendance_percentage=today_pct,
                overall_attendance_percentage=overall_pct,
            ),
            daily_summary=daily_summary,
            monthly_summary=monthly_summary,
        )

    def get_records(
        self,
        teacher_id: Optional[int] = None,
        academic_year: Optional[str] = None,
        month: Optional[int] = None,
        year: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status_filter: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> TeacherAttendanceRecordsResponse:
        today = date.today()
        effective_end = min(end_date, today) if end_date else today

        query = self.db.query(TeacherAttendance).join(Teacher, TeacherAttendance.teacher_id == Teacher.id).filter(
            TeacherAttendance.date <= effective_end
        )

        if teacher_id:
            query = query.filter(TeacherAttendance.teacher_id == teacher_id)
        if start_date:
            query = query.filter(TeacherAttendance.date >= start_date)
        if academic_year:
            years = [academic_year, academic_year.replace("/", "-"), academic_year.replace("-", "/")]
            query = query.filter(TeacherAttendance.academic_year.in_(years))
        if month:
            query = query.filter(func.extract("month", TeacherAttendance.date) == month)
        if year:
            query = query.filter(func.extract("year", TeacherAttendance.date) == year)
        if status_filter and status_filter.upper() != "ALL":
            query = query.filter(TeacherAttendance.status == status_filter.upper())
        if search and search.strip():
            s = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Teacher.first_name.ilike(s),
                    Teacher.last_name.ilike(s),
                    Teacher.middle_name.ilike(s),
                    Teacher.teacher_number.ilike(s),
                )
            )

        total = query.count()
        offset = (page - 1) * page_size
        records = query.order_by(desc(TeacherAttendance.date), desc(TeacherAttendance.id)).offset(offset).limit(page_size).all()

        items = [
            TeacherAttendanceRecordItem(
                id=r.id,
                teacher_id=r.teacher_id,
                teacher_name=r.teacher.full_name if r.teacher else "Teacher",
                teacher_number=r.teacher.teacher_number if r.teacher else "TCH-000",
                phone=r.teacher.phone if r.teacher else None,
                email=r.teacher.email if r.teacher else None,
                date=r.date,
                academic_year=r.academic_year,
                status=r.status,
                reason=r.reason,
                recorded_by_name=r.recorded_by.full_name if r.recorded_by else "Admin",
                recorded_at=r.created_at,
            )
            for r in records
        ]

        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 1

        return TeacherAttendanceRecordsResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    def get_staff_summary(
        self,
        academic_year: Optional[str] = None,
        month: Optional[int] = None,
        year: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> StaffAttendanceSummaryResponse:
        today = date.today()
        effective_end = min(end_date, today) if end_date else today

        school = self.get_school_metadata()
        target_year = academic_year or school["academic_year"]

        teachers = self.db.query(Teacher).order_by(Teacher.first_name.asc(), Teacher.last_name.asc()).all()

        att_query = self.db.query(TeacherAttendance).filter(TeacherAttendance.date <= effective_end)
        if start_date:
            att_query = att_query.filter(TeacherAttendance.date >= start_date)
        if target_year:
            years = [target_year, target_year.replace("/", "-"), target_year.replace("-", "/")]
            att_query = att_query.filter(TeacherAttendance.academic_year.in_(years))
        if month:
            att_query = att_query.filter(func.extract("month", TeacherAttendance.date) == month)
        if year:
            att_query = att_query.filter(func.extract("year", TeacherAttendance.date) == year)

        all_records = att_query.all()
        by_teacher: Dict[int, List[TeacherAttendance]] = {}
        for r in all_records:
            by_teacher.setdefault(r.teacher_id, []).append(r)

        total_p = 0
        total_a = 0
        total_l = 0
        total_lv = 0

        teacher_items: List[TeacherStaffAttendanceSummaryItem] = []
        for t in teachers:
            recs = by_teacher.get(t.id, [])
            p_cnt = sum(1 for r in recs if r.status == "PRESENT")
            l_cnt = sum(1 for r in recs if r.status == "LATE")
            a_cnt = sum(1 for r in recs if r.status == "ABSENT")
            lv_cnt = sum(1 for r in recs if r.status == "ON_LEAVE")
            tot = len(recs)
            pct = round((p_cnt + l_cnt) / tot * 100, 1) if tot > 0 else 0.0

            total_p += p_cnt
            total_l += l_cnt
            total_a += a_cnt
            total_lv += lv_cnt

            sorted_recs = sorted(recs, key=lambda x: x.date, reverse=True)
            last_date = sorted_recs[0].date if sorted_recs else None
            last_st = sorted_recs[0].status if sorted_recs else None

            teacher_items.append(
                TeacherStaffAttendanceSummaryItem(
                    teacher_id=t.id,
                    teacher_name=t.full_name,
                    teacher_number=t.teacher_number,
                    gender=t.gender,
                    phone=t.phone,
                    email=t.email,
                    total_days=tot,
                    days_present=p_cnt,
                    days_absent=a_cnt,
                    days_late=l_cnt,
                    days_on_leave=lv_cnt,
                    attendance_percentage=pct,
                    last_attendance_date=last_date,
                    last_status=last_st,
                )
            )

        overall_total = total_p + total_l + total_a + total_lv
        overall_pct = round((total_p + total_l) / overall_total * 100, 1) if overall_total > 0 else 0.0

        period_label = "Complete Staff History"
        if month:
            period_label = f"{calendar.month_name[month]} {year or today.year}"
        elif start_date and end_date:
            period_label = f"{start_date.isoformat()} to {effective_end.isoformat()}"

        return StaffAttendanceSummaryResponse(
            academic_year=target_year,
            period_label=period_label,
            total_teachers=len(teachers),
            overall_percentage=overall_pct,
            total_present_days=total_p,
            total_absent_days=total_a,
            total_late_days=total_l,
            total_leave_days=total_lv,
            teachers=teacher_items,
        )

    def export_excel(
        self,
        report_type: str,  # "daily", "monthly", "staff_summary", "teacher_history"
        teacher_id: Optional[int] = None,
        target_date: Optional[date] = None,
        academic_year: Optional[str] = None,
        month: Optional[int] = None,
        year: Optional[int] = None,
    ) -> bytes:
        school = self.get_school_metadata()
        wb = openpyxl.Workbook()
        ws = wb.active

        navy_fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
        header_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
        alt_row_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
        white_fill = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")

        white_bold_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        title_font = Font(name="Calibri", size=15, bold=True, color="0F172A")
        sub_font = Font(name="Calibri", size=10, italic=True, color="64748B")
        meta_bold = Font(name="Calibri", size=10, bold=True, color="0F172A")
        meta_normal = Font(name="Calibri", size=10, color="334155")
        cell_font = Font(name="Calibri", size=10, color="1E293B")
        cell_bold = Font(name="Calibri", size=10, bold=True, color="0F172A")
        success_font = Font(name="Calibri", size=10, bold=True, color="16A34A")
        alert_font = Font(name="Calibri", size=10, bold=True, color="DC2626")
        warn_font = Font(name="Calibri", size=10, bold=True, color="D97706")
        blue_font = Font(name="Calibri", size=10, bold=True, color="0284C7")

        thin_side = Side(border_style="thin", color="CBD5E1")
        cell_border = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)

        center_align = Alignment(horizontal="center", vertical="center")
        left_align = Alignment(horizontal="left", vertical="center")

        ws.merge_cells("A1:G1")
        ws["A1"] = school["name"].upper()
        ws["A1"].font = title_font
        ws["A1"].alignment = left_align

        if report_type == "daily":
            eff_date = target_date or date.today()
            ws.title = f"Staff Daily {eff_date.strftime('%Y-%m-%d')}"
            ws.merge_cells("A2:G2")
            ws["A2"] = f"Official Faculty Daily Attendance Register • {school['motto']}"
            ws["A2"].font = sub_font
            ws["A2"].alignment = left_align

            roster = self.get_daily_roster(attendance_date=eff_date, academic_year=academic_year)

            ws["A4"] = "Attendance Date:"
            ws["A4"].font = meta_bold
            ws["B4"] = eff_date.isoformat()
            ws["B4"].font = meta_normal

            ws["D4"] = "Academic Year:"
            ws["D4"].font = meta_bold
            ws["E4"] = roster.academic_year
            ws["E4"].font = meta_normal

            ws["A5"] = "Total Staff:"
            ws["A5"].font = meta_bold
            ws["B5"] = roster.total_teachers
            ws["B5"].font = meta_normal

            ws["D5"] = "Turnout Rate:"
            ws["D5"].font = meta_bold
            ws["E5"] = f"{round((roster.present_count + roster.late_count) / roster.total_teachers * 100, 1) if roster.total_teachers > 0 else 0}%"
            ws["E5"].font = meta_bold

            headers = ["#", "Staff ID", "Teacher Name", "Phone", "Email", "Status", "Reason / Remarks"]
            row_idx = 7
            for col_idx, h in enumerate(headers, 1):
                c = ws.cell(row=row_idx, column=col_idx, value=h)
                c.font = white_bold_font
                c.fill = header_fill
                c.alignment = center_align if col_idx in [1, 2, 6] else left_align
                c.border = cell_border
            ws.row_dimensions[row_idx].height = 24

            for idx, t in enumerate(roster.teachers, 1):
                row_idx += 1
                is_alt = (idx % 2 == 0)
                st_font = cell_bold
                if t.status == "PRESENT":
                    st_font = success_font
                elif t.status == "ABSENT":
                    st_font = alert_font
                elif t.status == "LATE":
                    st_font = warn_font
                elif t.status == "ON_LEAVE":
                    st_font = blue_font

                row_vals = [
                    (idx, center_align, cell_font),
                    (t.teacher_number, center_align, cell_bold),
                    (t.teacher_name, left_align, cell_font),
                    (t.phone or "—", left_align, cell_font),
                    (t.email or "—", left_align, cell_font),
                    (t.status, center_align, st_font),
                    (t.reason or "—", left_align, cell_font),
                ]
                for col_idx, (val, align, font) in enumerate(row_vals, 1):
                    cell = ws.cell(row=row_idx, column=col_idx, value=val)
                    cell.alignment = align
                    cell.font = font
                    cell.fill = alt_row_fill if is_alt else white_fill
                    cell.border = cell_border

        else:
            # Complete staff summary or monthly report
            ws.title = "Staff Attendance Summary"
            ws.merge_cells("A2:H2")
            ws["A2"] = f"Official Staff Attendance Summary Report • {school['motto']}"
            ws["A2"].font = sub_font
            ws["A2"].alignment = left_align

            summary = self.get_staff_summary(
                academic_year=academic_year,
                month=month,
                year=year
            )

            ws["A4"] = "Academic Year:"
            ws["A4"].font = meta_bold
            ws["B4"] = summary.academic_year
            ws["B4"].font = meta_normal

            ws["D4"] = "Reporting Period:"
            ws["D4"].font = meta_bold
            ws["E4"] = summary.period_label
            ws["E4"].font = meta_normal

            ws["A5"] = "Total Staff:"
            ws["A5"].font = meta_bold
            ws["B5"] = summary.total_teachers
            ws["B5"].font = meta_normal

            ws["D5"] = "Staff Attendance Rate:"
            ws["D5"].font = meta_bold
            ws["E5"] = f"{summary.overall_percentage}%"
            ws["E5"].font = meta_bold

            headers = [
                "#", "Staff ID", "Teacher Name", "Total Days",
                "Days Present", "Days Absent", "Days Late", "On Leave", "Attendance %"
            ]
            row_idx = 7
            for col_idx, h in enumerate(headers, 1):
                c = ws.cell(row=row_idx, column=col_idx, value=h)
                c.font = white_bold_font
                c.fill = navy_fill
                c.alignment = center_align if col_idx in [1, 2, 4, 5, 6, 7, 8, 9] else left_align
                c.border = cell_border
            ws.row_dimensions[row_idx].height = 24

            for idx, t in enumerate(summary.teachers, 1):
                row_idx += 1
                is_alt = (idx % 2 == 0)
                row_vals = [
                    (idx, center_align, cell_font),
                    (t.teacher_number, center_align, cell_bold),
                    (t.teacher_name, left_align, cell_font),
                    (t.total_days, center_align, cell_font),
                    (t.days_present, center_align, success_font),
                    (t.days_absent, center_align, alert_font if t.days_absent > 0 else cell_font),
                    (t.days_late, center_align, warn_font if t.days_late > 0 else cell_font),
                    (t.days_on_leave, center_align, blue_font if t.days_on_leave > 0 else cell_font),
                    (f"{t.attendance_percentage}%", center_align, alert_font if t.attendance_percentage < 80 else cell_bold),
                ]
                for col_idx, (val, align, font) in enumerate(row_vals, 1):
                    cell = ws.cell(row=row_idx, column=col_idx, value=val)
                    cell.alignment = align
                    cell.font = font
                    cell.fill = alt_row_fill if is_alt else white_fill
                    cell.border = cell_border

        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = max(max_len + 3, 11)

        buf = io.BytesIO()
        wb.save(buf)
        return buf.getvalue()

    def export_pdf(
        self,
        report_type: str,
        teacher_id: Optional[int] = None,
        target_date: Optional[date] = None,
        academic_year: Optional[str] = None,
        month: Optional[int] = None,
        year: Optional[int] = None,
    ) -> bytes:
        school = self.get_school_metadata()
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
            fontSize=15,
            leading=19,
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
        td_warn_style = ParagraphStyle(
            "TDWarn",
            parent=styles["Normal"],
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#d97706"),
            fontName="Helvetica-Bold",
            alignment=1,
        )
        td_blue_style = ParagraphStyle(
            "TDBlue",
            parent=styles["Normal"],
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#0284c7"),
            fontName="Helvetica-Bold",
            alignment=1,
        )

        story = []

        school_name = school["name"].upper()
        story.append(Paragraph(school_name, title_style))
        if report_type == "daily":
            story.append(Paragraph(f"Faculty & Staff Daily Attendance Register • {school['motto']}", subtitle_style))
        else:
            story.append(Paragraph(f"Faculty & Staff Attendance Performance Summary • {school['motto']}", subtitle_style))
        story.append(Spacer(1, 10))

        if report_type == "daily":
            eff_date = target_date or date.today()
            roster = self.get_daily_roster(attendance_date=eff_date, academic_year=academic_year)

            meta_data = [
                [
                    Paragraph("<b>Attendance Date:</b>", meta_label_style),
                    Paragraph(eff_date.isoformat(), meta_val_style),
                    Paragraph("<b>Academic Year:</b>", meta_label_style),
                    Paragraph(roster.academic_year, meta_val_style),
                    Paragraph("<b>Total Staff:</b>", meta_label_style),
                    Paragraph(str(roster.total_teachers), meta_val_style),
                ],
                [
                    Paragraph("<b>Present Today:</b>", meta_label_style),
                    Paragraph(f"<font color='#16a34a'><b>{roster.present_count}</b></font>", meta_val_style),
                    Paragraph("<b>Absent:</b>", meta_label_style),
                    Paragraph(f"<font color='#dc2626'><b>{roster.absent_count}</b></font>", meta_val_style),
                    Paragraph("<b>Late / On Leave:</b>", meta_label_style),
                    Paragraph(f"Late: {roster.late_count} | Leave: {roster.on_leave_count}", meta_val_style),
                ]
            ]
            meta_table = Table(meta_data, colWidths=[100, 150, 100, 150, 100, 140])
            meta_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ("PADDING", (0, 0), (-1, -1), 4),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]))
            story.append(meta_table)
            story.append(Spacer(1, 12))

            table_data = [[
                Paragraph("#", th_style),
                Paragraph("Staff ID", th_style),
                Paragraph("Teacher Name", th_style),
                Paragraph("Gender", th_style),
                Paragraph("Phone", th_style),
                Paragraph("Status", th_style),
                Paragraph("Reason / Remarks", th_style),
            ]]

            for idx, t in enumerate(roster.teachers, 1):
                st_p = td_bold_style
                if t.status == "PRESENT":
                    st_p = td_success_style
                elif t.status == "ABSENT":
                    st_p = td_alert_style
                elif t.status == "LATE":
                    st_p = td_warn_style
                elif t.status == "ON_LEAVE":
                    st_p = td_blue_style

                table_data.append([
                    Paragraph(str(idx), td_bold_style),
                    Paragraph(t.teacher_number, td_bold_style),
                    Paragraph(t.teacher_name, td_style),
                    Paragraph(t.gender or "—", td_style),
                    Paragraph(t.phone or "—", td_style),
                    Paragraph(t.status, st_p),
                    Paragraph(t.reason or "—", td_style),
                ])

            t = Table(table_data, colWidths=[30, 90, 190, 60, 110, 80, 230], repeatRows=1)
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
            summary = self.get_staff_summary(
                academic_year=academic_year,
                month=month,
                year=year
            )

            meta_data = [
                [
                    Paragraph("<b>Academic Year:</b>", meta_label_style),
                    Paragraph(summary.academic_year, meta_val_style),
                    Paragraph("<b>Reporting Period:</b>", meta_label_style),
                    Paragraph(summary.period_label, meta_val_style),
                    Paragraph("<b>Staff Turnout Rate:</b>", meta_label_style),
                    Paragraph(f"<b>{summary.overall_percentage}%</b>", meta_label_style),
                ]
            ]
            meta_table = Table(meta_data, colWidths=[120, 140, 130, 150, 120, 80])
            meta_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ("PADDING", (0, 0), (-1, -1), 4),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]))
            story.append(meta_table)
            story.append(Spacer(1, 12))

            table_data = [[
                Paragraph("#", th_style),
                Paragraph("Staff ID", th_style),
                Paragraph("Teacher Name", th_style),
                Paragraph("Total Days", th_style),
                Paragraph("Present", th_style),
                Paragraph("Absent", th_style),
                Paragraph("Late", th_style),
                Paragraph("On Leave", th_style),
                Paragraph("Rate %", th_style),
            ]]

            for idx, t in enumerate(summary.teachers, 1):
                table_data.append([
                    Paragraph(str(idx), td_bold_style),
                    Paragraph(t.teacher_number, td_bold_style),
                    Paragraph(t.teacher_name, td_style),
                    Paragraph(str(t.total_days), td_bold_style),
                    Paragraph(str(t.days_present), td_success_style),
                    Paragraph(str(t.days_absent), td_alert_style if t.days_absent > 0 else td_bold_style),
                    Paragraph(str(t.days_late), td_warn_style if t.days_late > 0 else td_bold_style),
                    Paragraph(str(t.days_on_leave), td_blue_style if t.days_on_leave > 0 else td_bold_style),
                    Paragraph(f"{t.attendance_percentage}%", td_alert_style if t.attendance_percentage < 80 else td_bold_style),
                ])

            t = Table(table_data, colWidths=[30, 85, 210, 65, 65, 65, 65, 65, 75], repeatRows=1)
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

        story.append(Spacer(1, 15))
        sig_data = [
            [
                Paragraph("<b>Recorded By:</b> Human Resources / Admin", meta_val_style),
                Paragraph("<b>Approved By:</b> Principal / Head of School", meta_val_style),
                Paragraph("<b>School Seal:</b> ____________________", meta_val_style),
            ]
        ]
        sig_table = Table(sig_data, colWidths=[250, 270, 260])
        sig_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(sig_table)

        doc.build(story, canvasmaker=TeacherAttendanceNumberedCanvas)
        return buffer.getvalue()

