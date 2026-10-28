import io
from datetime import datetime
from typing import List, Optional
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from app.models.timetable import Timetable
from app.models.school_class import SchoolClass
from app.models.teacher import Teacher
from app.models.institution import Institution


class TimetablePdfService:
    """Generates print-ready high-fidelity weekly Timetable PDF schedules for classes and teachers."""

    @staticmethod
    def generate_class_pdf(
        school_class: SchoolClass,
        academic_year: str,
        entries: List[Timetable],
        institution: Optional[Institution] = None
    ) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(letter),
            leftMargin=0.5 * inch,
            rightMargin=0.5 * inch,
            topMargin=0.5 * inch,
            bottomMargin=0.5 * inch
        )

        elements = []
        styles = getSampleStyleSheet()

        # Styles
        inst_name = institution.name if institution else "Hawlwadaag Secondary School"
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#1e3a8a"),
            alignment=1
        )
        subtitle_style = ParagraphStyle(
            "DocSubTitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#475569"),
            alignment=1
        )
        class_header_style = ParagraphStyle(
            "ClassHeader",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#0f172a"),
            alignment=1
        )

        elements.append(Paragraph(inst_name.upper(), title_style))
        elements.append(Paragraph("OFFICIAL ACADEMIC TIMETABLE", subtitle_style))
        elements.append(Spacer(1, 4))
        elements.append(Paragraph(f"Class: {school_class.name} ({school_class.code}) — Academic Year: {academic_year}", class_header_style))
        elements.append(Spacer(1, 12))

        # Days of week
        standard_days = ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
        # Extract unique time slots
        time_slot_set = set()
        for e in entries:
            time_slot_set.add((e.start_time, e.end_time))
        
        sorted_times = sorted(list(time_slot_set), key=lambda x: x[0])
        if not sorted_times:
            # Default empty grid if no entries
            elements.append(Paragraph("No timetable periods scheduled for this class.", subtitle_style))
            doc.build(elements)
            buffer.seek(0)
            return buffer.getvalue()

        # Build Table Data
        # Header row: [Time Slot, Saturday, Sunday, Monday, Tuesday, Wednesday, Thursday]
        header_row = ["TIME"] + [d.upper() for d in standard_days]
        table_data = [header_row]

        # Map entries: (start_time, day) -> list of entries
        slot_map = {}
        for e in entries:
            key = (e.start_time.strftime("%H:%M"), e.day_of_week.lower())
            slot_map[key] = e

        cell_style = ParagraphStyle(
            "GridCell",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#0f172a")
        )
        sub_cell_style = ParagraphStyle(
            "GridSubCell",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=7,
            leading=9,
            textColor=colors.HexColor("#475569")
        )

        for st, et in sorted_times:
            t_str = f"{st.strftime('%H:%M')} - {et.strftime('%H:%M')}"
            row = [Paragraph(f"<b>{t_str}</b>", cell_style)]

            for day in standard_days:
                key = (st.strftime("%H:%M"), day.lower())
                entry = slot_map.get(key)
                if entry:
                    subj_name = entry.subject.name if entry.subject else "Subject"
                    teacher_name = entry.teacher.full_name if entry.teacher else ""
                    room = entry.room or ""

                    cell_html = f"<b>{subj_name}</b>"
                    if teacher_name:
                        cell_html += f"<br/><font color='#2563eb'>{teacher_name}</font>"
                    if room:
                        cell_html += f"<br/><font color='#64748b'>📍 {room}</font>"
                    row.append(Paragraph(cell_html, cell_style))
                else:
                    row.append(Paragraph("<font color='#94a3b8'>— Free —</font>", sub_cell_style))

            table_data.append(row)

        # Build ReportLab Table
        col_width = 1.35 * inch
        time_width = 1.1 * inch
        t = Table(table_data, colWidths=[time_width] + [col_width] * len(standard_days))
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e40af")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ]))

        elements.append(t)
        elements.append(Spacer(1, 14))

        # Footer note
        footer_style = ParagraphStyle(
            "DocFooter",
            parent=styles["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#94a3b8"),
            alignment=1
        )
        generated_at = datetime.now().strftime("%B %d, %Y at %H:%M")
        elements.append(Paragraph(f"Official schedule generated by Somroyal EMS on {generated_at}. Any modifications require authorized administrative approval.", footer_style))

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()

    @staticmethod
    def generate_teacher_pdf(
        teacher: Teacher,
        academic_year: str,
        entries: List[Timetable],
        institution: Optional[Institution] = None
    ) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(letter),
            leftMargin=0.5 * inch,
            rightMargin=0.5 * inch,
            topMargin=0.5 * inch,
            bottomMargin=0.5 * inch
        )

        elements = []
        styles = getSampleStyleSheet()

        inst_name = institution.name if institution else "Hawlwadaag Secondary School"
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#0f766e"),
            alignment=1
        )
        subtitle_style = ParagraphStyle(
            "DocSubTitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#475569"),
            alignment=1
        )
        teacher_header_style = ParagraphStyle(
            "TeacherHeader",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#0f172a"),
            alignment=1
        )

        elements.append(Paragraph(inst_name.upper(), title_style))
        elements.append(Paragraph("FACULTY TEACHING TIMETABLE", subtitle_style))
        elements.append(Spacer(1, 4))
        elements.append(Paragraph(f"Faculty: {teacher.full_name} ({teacher.teacher_number or 'Staff'}) — Academic Year: {academic_year}", teacher_header_style))
        elements.append(Spacer(1, 12))

        standard_days = ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
        time_slot_set = set()
        for e in entries:
            time_slot_set.add((e.start_time, e.end_time))
        
        sorted_times = sorted(list(time_slot_set), key=lambda x: x[0])
        if not sorted_times:
            elements.append(Paragraph("No timetable periods assigned to this teacher.", subtitle_style))
            doc.build(elements)
            buffer.seek(0)
            return buffer.getvalue()

        header_row = ["TIME"] + [d.upper() for d in standard_days]
        table_data = [header_row]

        slot_map = {}
        for e in entries:
            key = (e.start_time.strftime("%H:%M"), e.day_of_week.lower())
            slot_map[key] = e

        cell_style = ParagraphStyle(
            "GridCell",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#0f172a")
        )
        sub_cell_style = ParagraphStyle(
            "GridSubCell",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=7,
            leading=9,
            textColor=colors.HexColor("#475569")
        )

        for st, et in sorted_times:
            t_str = f"{st.strftime('%H:%M')} - {et.strftime('%H:%M')}"
            row = [Paragraph(f"<b>{t_str}</b>", cell_style)]

            for day in standard_days:
                key = (st.strftime("%H:%M"), day.lower())
                entry = slot_map.get(key)
                if entry:
                    subj_name = entry.subject.name if entry.subject else "Subject"
                    class_name = entry.school_class.name if entry.school_class else ""
                    room = entry.room or ""

                    cell_html = f"<b>{subj_name}</b>"
                    if class_name:
                        cell_html += f"<br/><font color='#047857'>{class_name}</font>"
                    if room:
                        cell_html += f"<br/><font color='#64748b'>📍 {room}</font>"
                    row.append(Paragraph(cell_html, cell_style))
                else:
                    row.append(Paragraph("<font color='#94a3b8'>— Free —</font>", sub_cell_style))

            table_data.append(row)

        col_width = 1.35 * inch
        time_width = 1.1 * inch
        t = Table(table_data, colWidths=[time_width] + [col_width] * len(standard_days))
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f766e")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ]))

        elements.append(t)
        elements.append(Spacer(1, 14))

        footer_style = ParagraphStyle(
            "DocFooter",
            parent=styles["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#94a3b8"),
            alignment=1
        )
        generated_at = datetime.now().strftime("%B %d, %Y at %H:%M")
        elements.append(Paragraph(f"Faculty teaching schedule issued by Somroyal EMS on {generated_at}.", footer_style))

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
