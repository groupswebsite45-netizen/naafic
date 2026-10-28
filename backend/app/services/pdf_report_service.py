import io
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape, portrait
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak, Image, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and draw total page count
    along with Somroyal EMS security watermark and metadata footer.
    """
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
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages: int):
        self.saveState()
        # Top subtle bar
        self.setStrokeColor(colors.HexColor("#0f172a"))
        self.setLineWidth(1.5)
        self.line(20, self._pagesize[1] - 15, self._pagesize[0] - 20, self._pagesize[1] - 15)

        # Footer divider
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.75)
        self.line(20, 25, self._pagesize[0] - 20, 25)

        # Footer text
        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#64748b"))
        self.drawString(20, 14, "Somroyal EMS — Official Academic Record • Confidential Document • Valid Only With School Seal")
        
        page_str = f"Page {self._pageNumber} of {total_pages}"
        self.drawRightString(self._pagesize[0] - 20, 14, page_str)
        self.restoreState()


class PDFReportService:
    """Enterprise-grade PDF generator for Somroyal EMS examination results."""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        # Primary Brand Headings
        self.styles.add(ParagraphStyle(
            name="SchoolTitle",
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=18,
            textColor=colors.HexColor("#0f172a"),
        ))
        self.styles.add(ParagraphStyle(
            name="SchoolSubtitle",
            fontName="Helvetica-Oblique",
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#ea580c"),
        ))
        self.styles.add(ParagraphStyle(
            name="SchoolContact",
            fontName="Helvetica",
            fontSize=7.5,
            leading=10,
            textColor=colors.HexColor("#475569"),
        ))
        self.styles.add(ParagraphStyle(
            name="ReportBadge",
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=colors.white,
            alignment=1,  # Center
        ))
        self.styles.add(ParagraphStyle(
            name="TableHeader",
            fontName="Helvetica-Bold",
            fontSize=7.5,
            leading=9,
            textColor=colors.white,
            alignment=1,  # Center
        ))
        self.styles.add(ParagraphStyle(
            name="TableCell",
            fontName="Helvetica",
            fontSize=7.5,
            leading=9.5,
            textColor=colors.HexColor("#1e293b"),
        ))
        self.styles.add(ParagraphStyle(
            name="TableCellBold",
            fontName="Helvetica-Bold",
            fontSize=7.5,
            leading=9.5,
            textColor=colors.HexColor("#0f172a"),
            alignment=1,
        ))
        self.styles.add(ParagraphStyle(
            name="TableCellCenter",
            fontName="Helvetica",
            fontSize=7.5,
            leading=9.5,
            textColor=colors.HexColor("#1e293b"),
            alignment=1,
        ))
        self.styles.add(ParagraphStyle(
            name="PassText",
            fontName="Helvetica-Bold",
            fontSize=7.5,
            leading=9.5,
            textColor=colors.HexColor("#16a34a"),
            alignment=1,
        ))
        self.styles.add(ParagraphStyle(
            name="FailText",
            fontName="Helvetica-Bold",
            fontSize=7.5,
            leading=9.5,
            textColor=colors.HexColor("#dc2626"),
            alignment=1,
        ))
        self.styles.add(ParagraphStyle(
            name="MetaLabel",
            fontName="Helvetica-Bold",
            fontSize=7.5,
            leading=10,
            textColor=colors.HexColor("#475569"),
        ))
        self.styles.add(ParagraphStyle(
            name="MetaValue",
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#0f172a"),
        ))

    def _get_logo_image(self, logo_path: Optional[str], width: float = 48, height: float = 48):
        if logo_path and os.path.exists(logo_path):
            try:
                return Image(logo_path, width=width, height=height)
            except Exception:
                pass
        # Fallback placeholder text in table cell if logo fails
        return Paragraph("<b>SOMROYAL<br/>EMS</b>", self.styles["SchoolSubtitle"])

    # =========================================================================
    # 1. CLASS RESULT SHEET PDF (LANDSCAPE A4)
    # =========================================================================

    def generate_class_result_sheet_pdf(self, sheet_data: Dict[str, Any]) -> bytes:
        """
        Generate a multi-page, landscape class result sheet table with all students,
        all subjects, rankings, totals, grades, pass/fail status, and summary statistics.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            leftMargin=20,
            rightMargin=20,
            topMargin=24,
            bottomMargin=32,
        )

        story = []
        school = sheet_data.get("school", {})
        cls = sheet_data.get("class_info", {})
        exam = sheet_data.get("exam_info", {})
        subjects = sheet_data.get("subjects", [])
        students = sheet_data.get("students", [])
        summary = sheet_data.get("class_summary", {})

        # --- A. BRAND HEADER ---
        logo_img = self._get_logo_image(school.get("logo_path"), width=44, height=44)
        
        school_text = [
            Paragraph(f"<b>{school.get('name', 'Somroyal Educational Management System').upper()}</b>", self.styles["SchoolTitle"]),
            Paragraph(f"<i>{school.get('motto', 'Excellence in Education and Character')}</i>", self.styles["SchoolSubtitle"]),
            Paragraph(f"{school.get('address', 'Mogadishu, Somalia')} • Tel: {school.get('phone', '')} • Email: {school.get('email', '')}", self.styles["SchoolContact"]),
        ]

        title_box = [
            Table(
                [[Paragraph("OFFICIAL CLASS RESULT SHEET", self.styles["ReportBadge"])]],
                colWidths=[210],
                style=TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#0f172a")),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ])
            ),
            Spacer(1, 3),
            Paragraph(f"Generated: {datetime.now().strftime('%d %b %Y, %H:%M')}", self.styles["SchoolContact"]),
        ]

        header_table = Table(
            [[logo_img, school_text, title_box]],
            colWidths=[50, 520, 230],
            style=TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 2),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ])
        )
        story.append(header_table)

        # Orange Accent Line
        story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#ea580c"), spaceAfter=5, spaceBefore=2))

        # --- B. METADATA BAR ---
        meta_data = [
            [
                Paragraph("<b>Academic Year:</b>", self.styles["MetaLabel"]),
                Paragraph(str(cls.get("academic_year") or exam.get("academic_year", "-")), self.styles["MetaValue"]),
                Paragraph("<b>Examination:</b>", self.styles["MetaLabel"]),
                Paragraph(str(exam.get("name", "Examination")), self.styles["MetaValue"]),
                Paragraph("<b>Class & Section:</b>", self.styles["MetaLabel"]),
                Paragraph(f"{cls.get('name', 'Class')} ({cls.get('division', '')})", self.styles["MetaValue"]),
                Paragraph("<b>Registered Students:</b>", self.styles["MetaLabel"]),
                Paragraph(str(summary.get("registered_students", len(students))), self.styles["MetaValue"]),
                Paragraph("<b>Class Average:</b>", self.styles["MetaLabel"]),
                Paragraph(f"{summary.get('class_average_percentage', 0)}%", self.styles["MetaValue"]),
                Paragraph("<b>Pass Rate:</b>", self.styles["MetaLabel"]),
                Paragraph(f"{summary.get('pass_percentage', 0)}%", self.styles["MetaValue"]),
            ]
        ]
        meta_table = Table(
            meta_data,
            colWidths=[65, 65, 65, 125, 75, 100, 95, 45, 65, 45, 55, 45],
            style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
                ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#cbd5e1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
            ])
        )
        story.append(meta_table)
        story.append(Spacer(1, 6))

        # --- C. RESULTS MATRIX TABLE ---
        # Fixed columns: Rank (26), Adm (42), Student Name (105), Gender (20)
        # Trailing columns: Total (34), Max (28), % (32), Grade (26), Status (36)
        # Total fixed width = 26 + 42 + 105 + 20 + 34 + 28 + 32 + 26 + 36 = 349 pt
        # Available width for landscape A4 = 841.89 - 40 = 801.89 pt
        # Available for subjects = 801.89 - 349 = 452.89 pt
        num_subjects = max(1, len(subjects))
        subj_col_width = max(28, min(55, int(452 / num_subjects)))
        
        # Build Header Row
        header_row = [
            Paragraph("Rank", self.styles["TableHeader"]),
            Paragraph("Adm No", self.styles["TableHeader"]),
            Paragraph("Student Name", self.styles["TableHeader"]),
            Paragraph("Gen", self.styles["TableHeader"]),
        ]
        for s in subjects:
            short_name = s.get("code") or s.get("name", "")[:8]
            header_row.append(Paragraph(short_name, self.styles["TableHeader"]))

        header_row.extend([
            Paragraph("Total", self.styles["TableHeader"]),
            Paragraph("Max", self.styles["TableHeader"]),
            Paragraph("%", self.styles["TableHeader"]),
            Paragraph("Grd", self.styles["TableHeader"]),
            Paragraph("Status", self.styles["TableHeader"]),
        ])

        # Widths
        col_widths = [26, 42, 110, 20] + [subj_col_width] * num_subjects + [34, 28, 32, 26, 36]
        
        table_rows = [header_row]

        for std in students:
            status_style = self.styles["PassText"] if std.get("pass_status") == "PASS" else self.styles["FailText"]
            
            row = [
                Paragraph(str(std.get("rank", "-")), self.styles["TableCellBold"]),
                Paragraph(str(std.get("admission_number", "-")), self.styles["TableCell"]),
                Paragraph(str(std.get("student_name", "-")), self.styles["TableCell"]),
                Paragraph(str(std.get("gender", "-"))[:1], self.styles["TableCellCenter"]),
            ]

            std_scores = std.get("subject_marks", {})
            for s in subjects:
                s_id = str(s.get("id"))
                score_obj = std_scores.get(s_id) or std_scores.get(s.get("id"))
                if not score_obj:
                    val_str = "-"
                elif score_obj.get("attendance_status") in ("ABSENT", "EXCUSED"):
                    val_str = "<b>ABS</b>"
                elif score_obj.get("marks_obtained") is not None:
                    marks = score_obj.get("marks_obtained")
                    val_str = f"{marks:.0f}" if marks == int(marks) else f"{marks:.1f}"
                else:
                    val_str = "-"
                row.append(Paragraph(val_str, self.styles["TableCellCenter"]))

            # Totals
            tot_obt = std.get("total_obtained")
            tot_str = f"{tot_obt:.0f}" if tot_obt is not None and tot_obt == int(tot_obt) else (f"{tot_obt:.1f}" if tot_obt is not None else "-")
            max_m = std.get("total_max")
            max_str = f"{max_m:.0f}" if max_m is not None else "-"
            pct = std.get("percentage")
            pct_str = f"{pct:.1f}%" if pct is not None else "-"

            row.extend([
                Paragraph(tot_str, self.styles["TableCellBold"]),
                Paragraph(max_str, self.styles["TableCellCenter"]),
                Paragraph(pct_str, self.styles["TableCellBold"]),
                Paragraph(str(std.get("grade", "-")), self.styles["TableCellBold"]),
                Paragraph(str(std.get("pass_status", "-")), status_style),
            ])
            table_rows.append(row)

        res_table = Table(
            table_rows,
            colWidths=col_widths,
            repeatRows=1,
            style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("LEFTPADDING", (0, 0), (-1, -1), 2),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ])
        )
        story.append(res_table)
        story.append(Spacer(1, 8))

        # --- D. SUMMARY STATISTICS & SIGNATURES ---
        summary_box = []
        
        # Summary Box Data
        sum_rows = [
            [
                Paragraph("<b>CLASS SUMMARY STATISTICS</b>", self.styles["TableHeader"]),
                Paragraph("<b>GRADING SCALE</b>", self.styles["TableHeader"]),
                Paragraph("<b>OFFICIAL VERIFICATION</b>", self.styles["TableHeader"]),
            ],
            [
                Paragraph(
                    f"• Registered: <b>{summary.get('registered_students', 0)}</b><br/>"
                    f"• Sat Examination: <b>{summary.get('sat_exam_students', 0)}</b><br/>"
                    f"• Absent Students: <b>{summary.get('absent_students', 0)}</b><br/>"
                    f"• Passed Students: <b>{summary.get('passed_students', 0)}</b> ({summary.get('pass_percentage', 0)}%)<br/>"
                    f"• Failed Students: <b>{summary.get('failed_students', 0)}</b><br/>"
                    f"• Class Average: <b>{summary.get('class_average_percentage', 0)}%</b><br/>"
                    f"• Highest / Lowest Score: <b>{summary.get('highest_total', '-')} / {summary.get('lowest_total', '-')}</b>",
                    self.styles["TableCell"]
                ),
                Paragraph(
                    "<b>A+</b>: 90% - 100% (High Distinction)<br/>"
                    "<b>A</b> : 80% - 89.9% (Distinction)<br/>"
                    "<b>B</b> : 70% - 79.9% (Merit)<br/>"
                    "<b>C</b> : 60% - 69.9% (Credit)<br/>"
                    "<b>D</b> : 50% - 59.9% (Pass)<br/>"
                    "<b>F</b> : Below 50% (Fail)",
                    self.styles["TableCell"]
                ),
                Paragraph(
                    "Class Teacher: _______________________<br/>"
                    "Signature & Date: ____________________<br/><br/>"
                    "Headteacher / Dean: ___________________<br/>"
                    "Signature & Date: ____________________<br/>"
                    "<i>[ OFFICIAL SCHOOL STAMP ]</i>",
                    self.styles["TableCell"]
                )
            ]
        ]
        
        sum_table = Table(
            sum_rows,
            colWidths=[270, 240, 290],
            style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
                ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#f8fafc")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ])
        )
        summary_box.append(sum_table)

        story.append(KeepTogether(summary_box))

        doc.build(story, canvasmaker=NumberedCanvas)
        return buffer.getvalue()

    # =========================================================================
    # 2. INDIVIDUAL STUDENT RESULT REPORT CARD (PORTRAIT A4)
    # =========================================================================

    def generate_student_report_card_pdf(self, report_data: Dict[str, Any]) -> bytes:
        """
        Generate a professional, print-ready student report card with student profile,
        subject-by-subject scores, overall percentage, class position, teacher remarks,
        and official verification signatures.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=portrait(A4),
            leftMargin=28,
            rightMargin=28,
            topMargin=25,
            bottomMargin=32,
        )

        story = []
        school = report_data.get("school", {})
        std = report_data.get("student", {})
        cls = report_data.get("class_info", {})
        exam = report_data.get("exam_info", {})
        subjects = report_data.get("subjects", [])
        overall = report_data.get("overall", {})

        # --- A. BRAND HEADER ---
        logo_img = self._get_logo_image(school.get("logo_path"), width=52, height=52)
        
        school_text = [
            Paragraph(f"<b>{school.get('name', 'Somroyal Educational Management System').upper()}</b>", self.styles["SchoolTitle"]),
            Paragraph(f"<i>{school.get('motto', 'Excellence in Education and Character')}</i>", self.styles["SchoolSubtitle"]),
            Paragraph(f"{school.get('address', 'Mogadishu, Somalia')} • Tel: {school.get('phone', '')} • Email: {school.get('email', '')}", self.styles["SchoolContact"]),
        ]

        title_box = [
            Table(
                [[Paragraph("STUDENT REPORT CARD", self.styles["ReportBadge"])]],
                colWidths=[165],
                style=TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#0f172a")),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ])
            ),
            Spacer(1, 2),
            Paragraph(f"Issued: {datetime.now().strftime('%d %B %Y')}", self.styles["SchoolContact"]),
        ]

        header_table = Table(
            [[logo_img, school_text, title_box]],
            colWidths=[55, 315, 170],
            style=TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 2),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ])
        )
        story.append(header_table)
        story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#ea580c"), spaceAfter=6, spaceBefore=2))

        # --- B. STUDENT PROFILE CARD ---
        profile_data = [
            [
                Paragraph("<b>Student Name:</b>", self.styles["MetaLabel"]),
                Paragraph(f"<b>{std.get('student_name', std.get('full_name', '-'))}</b>", self.styles["MetaValue"]),
                Paragraph("<b>Admission No:</b>", self.styles["MetaLabel"]),
                Paragraph(f"<b>{std.get('admission_number', '-')}</b>", self.styles["MetaValue"]),
            ],
            [
                Paragraph("<b>Class & Section:</b>", self.styles["MetaLabel"]),
                Paragraph(f"{cls.get('name', '-')} ({cls.get('division', '')})", self.styles["TableCellBold"]),
                Paragraph("<b>Roll Number:</b>", self.styles["MetaLabel"]),
                Paragraph(str(std.get("roll_number") or "-"), self.styles["TableCellBold"]),
            ],
            [
                Paragraph("<b>Academic Year:</b>", self.styles["MetaLabel"]),
                Paragraph(str(cls.get("academic_year") or exam.get("academic_year", "-")), self.styles["TableCellBold"]),
                Paragraph("<b>Examination:</b>", self.styles["MetaLabel"]),
                Paragraph(str(exam.get("name", "Official Examination")), self.styles["TableCellBold"]),
            ],
            [
                Paragraph("<b>Gender / Status:</b>", self.styles["MetaLabel"]),
                Paragraph(f"{std.get('gender', '-')} • Enrolled", self.styles["TableCell"]),
                Paragraph("<b>Class Rank:</b>", self.styles["MetaLabel"]),
                Paragraph(f"<b>Position {overall.get('rank_in_class', '-')}</b> of {overall.get('class_size', '-')} students", self.styles["MetaValue"]),
            ],
        ]

        profile_table = Table(
            profile_data,
            colWidths=[85, 185, 85, 185],
            style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#cbd5e1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ])
        )
        story.append(profile_table)
        story.append(Spacer(1, 8))

        # --- C. SUBJECT SCORES TABLE ---
        sub_headers = [
            Paragraph("Code", self.styles["TableHeader"]),
            Paragraph("Subject Title", self.styles["TableHeader"]),
            Paragraph("Teacher", self.styles["TableHeader"]),
            Paragraph("Marks", self.styles["TableHeader"]),
            Paragraph("Max", self.styles["TableHeader"]),
            Paragraph("Pass", self.styles["TableHeader"]),
            Paragraph("%", self.styles["TableHeader"]),
            Paragraph("Grade", self.styles["TableHeader"]),
            Paragraph("Status", self.styles["TableHeader"]),
            Paragraph("Teacher Remarks", self.styles["TableHeader"]),
        ]
        sub_rows = [sub_headers]

        for s in subjects:
            status_str = s.get("pass_status", "PASS")
            status_style = self.styles["PassText"] if status_str == "PASS" else self.styles["FailText"]

            if s.get("attendance_status") in ("ABSENT", "EXCUSED"):
                marks_str = "ABS"
                pct_str = "0.0%"
            elif s.get("marks_obtained") is not None:
                m = s.get("marks_obtained")
                marks_str = f"{m:.0f}" if m == int(m) else f"{m:.1f}"
                pct = s.get("percentage")
                pct_str = f"{pct:.1f}%" if pct is not None else "-"
            else:
                marks_str = "-"
                pct_str = "-"

            max_m = s.get("max_marks", 100)
            pass_m = s.get("pass_marks", 50)

            sub_rows.append([
                Paragraph(str(s.get("subject_code", "")), self.styles["TableCellCenter"]),
                Paragraph(str(s.get("subject_name", "")), self.styles["TableCellBold"]),
                Paragraph(str(s.get("teacher_name", "Assigned")), self.styles["TableCell"]),
                Paragraph(marks_str, self.styles["TableCellBold"]),
                Paragraph(f"{max_m:.0f}", self.styles["TableCellCenter"]),
                Paragraph(f"{pass_m:.0f}", self.styles["TableCellCenter"]),
                Paragraph(pct_str, self.styles["TableCellBold"]),
                Paragraph(str(s.get("grade", "-")), self.styles["TableCellBold"]),
                Paragraph(status_str, status_style),
                Paragraph(str(s.get("remarks") or "Good effort"), self.styles["TableCell"]),
            ])

        sub_table = Table(
            sub_rows,
            colWidths=[40, 115, 75, 40, 32, 32, 36, 32, 40, 98],
            repeatRows=1,
            style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ])
        )
        story.append(sub_table)
        story.append(Spacer(1, 8))

        # --- D. PERFORMANCE SUMMARY CARD ---
        tot_obt = overall.get("total_obtained", 0)
        tot_max = overall.get("total_max", 0)
        pct_ovr = overall.get("overall_percentage", 0)
        grade_ovr = overall.get("overall_grade", "F")
        pass_ovr = overall.get("pass_status", "PASS")
        rank_ovr = overall.get("rank_in_class", "-")
        cls_size = overall.get("class_size", "-")

        result_color = colors.HexColor("#16a34a") if pass_ovr == "PASS" else colors.HexColor("#dc2626")

        summary_data = [
            [
                Paragraph("<b>TOTAL MARKS</b>", self.styles["TableHeader"]),
                Paragraph("<b>OVERALL PERCENTAGE</b>", self.styles["TableHeader"]),
                Paragraph("<b>FINAL GRADE</b>", self.styles["TableHeader"]),
                Paragraph("<b>CLASS POSITION</b>", self.styles["TableHeader"]),
                Paragraph("<b>DECISION</b>", self.styles["TableHeader"]),
            ],
            [
                Paragraph(f"<b>{tot_obt:.1f} / {tot_max:.0f}</b>", self.styles["TableCellBold"]),
                Paragraph(f"<b>{pct_ovr:.1f}%</b>", self.styles["TableCellBold"]),
                Paragraph(f"<b>{grade_ovr}</b>", self.styles["TableCellBold"]),
                Paragraph(f"<b>Rank {rank_ovr} of {cls_size}</b>", self.styles["TableCellBold"]),
                Paragraph(f"<b>{pass_ovr}</b>", self.styles["PassText"] if pass_ovr == "PASS" else self.styles["FailText"]),
            ]
        ]

        summary_table = Table(
            summary_data,
            colWidths=[110, 115, 100, 115, 100],
            style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
                ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#f1f5f9")),
                ("GRID", (0, 0), (-1, -1), 0.75, colors.HexColor("#94a3b8")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ])
        )
        story.append(summary_table)
        story.append(Spacer(1, 8))

        # --- E. REMARKS & OFFICIAL STAMPS ---
        remarks_data = [
            [
                Paragraph("<b>GRADING SCALE</b>", self.styles["TableHeader"]),
                Paragraph("<b>COMMENTS & VERIFICATION</b>", self.styles["TableHeader"]),
            ],
            [
                Paragraph(
                    "<b>A+</b>: 90% - 100% (High Distinction)<br/>"
                    "<b>A</b> : 80% - 89.9% (Distinction)<br/>"
                    "<b>B</b> : 70% - 79.9% (Merit)<br/>"
                    "<b>C</b> : 60% - 69.9% (Credit)<br/>"
                    "<b>D</b> : 50% - 59.9% (Pass)<br/>"
                    "<b>F</b> : Below 50% (Fail)",
                    self.styles["TableCell"]
                ),
                Paragraph(
                    f"<b>Class Teacher Remarks:</b> {overall.get('teacher_remarks', 'Good performance and active participation in class.')}<br/><br/>"
                    "Class Teacher Signature: __________________   Date: ___________<br/><br/>"
                    "Principal Signature: _______________________   Date: ___________<br/>"
                    "<i>[ OFFICIAL SCHOOL EMBOSSED SEAL ]</i>",
                    self.styles["TableCell"]
                )
            ]
        ]
        remarks_table = Table(
            remarks_data,
            colWidths=[180, 360],
            style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#f8fafc")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ])
        )
        story.append(KeepTogether(remarks_table))

        doc.build(story, canvasmaker=NumberedCanvas)
        return buffer.getvalue()

    # =========================================================================
    # 3. CLASS RANKINGS & MERIT LIST PDF (PORTRAIT A4)
    # =========================================================================

    def generate_class_ranking_pdf(self, ranking_data: Dict[str, Any]) -> bytes:
        """
        Generate a print-ready Class Ranking & Merit List PDF with competition ranking (1, 2, 2, 4),
        tie handling, completed subjects, percentages, grades, and pass/fail status.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=portrait(A4),
            leftMargin=28,
            rightMargin=28,
            topMargin=25,
            bottomMargin=32,
        )

        story = []
        school = ranking_data.get("school", {})
        cls = ranking_data.get("class_info", {})
        exam = ranking_data.get("exam_info", {})
        rankings = ranking_data.get("rankings", [])

        # Header
        logo_img = self._get_logo_image(school.get("logo_path"), width=46, height=46)
        school_text = [
            Paragraph(f"<b>{school.get('name', 'Somroyal Educational Management System').upper()}</b>", self.styles["SchoolTitle"]),
            Paragraph(f"<i>{school.get('motto', 'Excellence in Education and Character')}</i>", self.styles["SchoolSubtitle"]),
            Paragraph(f"{school.get('address', 'Mogadishu, Somalia')} • Tel: {school.get('phone', '')}", self.styles["SchoolContact"]),
        ]

        title_box = [
            Table(
                [[Paragraph("MERIT LIST & RANKINGS", self.styles["ReportBadge"])]],
                colWidths=[165],
                style=TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#0f172a")),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ])
            ),
            Spacer(1, 2),
            Paragraph(f"Generated: {datetime.now().strftime('%d %b %Y, %H:%M')}", self.styles["SchoolContact"]),
        ]

        header_table = Table(
            [[logo_img, school_text, title_box]],
            colWidths=[55, 315, 170],
            style=TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 2),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2),
            ])
        )
        story.append(header_table)
        story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#ea580c"), spaceAfter=6, spaceBefore=2))

        # Metadata Bar
        meta_data = [
            [
                Paragraph("<b>Academic Year:</b>", self.styles["MetaLabel"]),
                Paragraph(str(cls.get("academic_year") or exam.get("academic_year", "-")), self.styles["MetaValue"]),
                Paragraph("<b>Examination:</b>", self.styles["MetaLabel"]),
                Paragraph(str(exam.get("name", "Examination")), self.styles["MetaValue"]),
                Paragraph("<b>Class:</b>", self.styles["MetaLabel"]),
                Paragraph(f"{cls.get('name', 'All Classes')} ({cls.get('division', '')})", self.styles["MetaValue"]),
                Paragraph("<b>Ranked Students:</b>", self.styles["MetaLabel"]),
                Paragraph(str(len(rankings)), self.styles["MetaValue"]),
            ]
        ]
        meta_table = Table(
            meta_data,
            colWidths=[70, 75, 70, 115, 45, 105, 75, 45],
            style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
                ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#cbd5e1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ])
        )
        story.append(meta_table)
        story.append(Spacer(1, 8))

        # Rankings Table
        rank_headers = [
            Paragraph("Rank", self.styles["TableHeader"]),
            Paragraph("Adm No", self.styles["TableHeader"]),
            Paragraph("Student Full Name", self.styles["TableHeader"]),
            Paragraph("Gender", self.styles["TableHeader"]),
            Paragraph("Class", self.styles["TableHeader"]),
            Paragraph("Total Marks", self.styles["TableHeader"]),
            Paragraph("Max", self.styles["TableHeader"]),
            Paragraph("%", self.styles["TableHeader"]),
            Paragraph("Grade", self.styles["TableHeader"]),
            Paragraph("Decision", self.styles["TableHeader"]),
        ]
        rank_rows = [rank_headers]

        for r in rankings:
            pos = r.get("position", "-")
            status_str = r.get("pass_fail", "PASS")
            status_style = self.styles["PassText"] if status_str == "PASS" else self.styles["FailText"]

            tot = r.get("total_marks")
            tot_str = f"{tot:.1f}" if tot is not None else "-"
            max_m = r.get("max_possible_marks")
            max_str = f"{max_m:.0f}" if max_m is not None else "-"
            pct = r.get("percentage")
            pct_str = f"{pct:.1f}%" if pct is not None else "-"

            rank_rows.append([
                Paragraph(str(pos), self.styles["TableCellBold"]),
                Paragraph(str(r.get("admission_number", "-")), self.styles["TableCell"]),
                Paragraph(str(r.get("student_name", "-")), self.styles["TableCellBold"]),
                Paragraph(str(r.get("gender", "-"))[:1], self.styles["TableCellCenter"]),
                Paragraph(str(r.get("class_name", "-")), self.styles["TableCell"]),
                Paragraph(tot_str, self.styles["TableCellBold"]),
                Paragraph(max_str, self.styles["TableCellCenter"]),
                Paragraph(pct_str, self.styles["TableCellBold"]),
                Paragraph(str(r.get("grade", "-")), self.styles["TableCellBold"]),
                Paragraph(status_str, status_style),
            ])

        rank_table = Table(
            rank_rows,
            colWidths=[35, 55, 145, 30, 75, 50, 40, 45, 35, 50],
            repeatRows=1,
            style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ])
        )
        story.append(rank_table)

        doc.build(story, canvasmaker=NumberedCanvas)
        return buffer.getvalue()
