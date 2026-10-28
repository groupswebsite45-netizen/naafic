import io
from typing import Dict, Any, List
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


class ExcelExportService:
    """Service for exporting examination rankings and merit lists to styled Excel workbooks."""

    @staticmethod
    def generate_class_ranking_excel(ranking_data: Dict[str, Any]) -> bytes:
        """
        Build an enterprise styled Excel file containing the class merit list and rankings.
        """
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Class Merit List"

        # Styles
        navy_fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
        sub_navy_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
        alt_row_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
        white_fill = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
        
        white_bold_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        title_font = Font(name="Calibri", size=16, bold=True, color="0F172A")
        subtitle_font = Font(name="Calibri", size=10, italic=True, color="64748B")
        meta_bold_font = Font(name="Calibri", size=10, bold=True, color="0F172A")
        meta_font = Font(name="Calibri", size=10, color="334155")
        
        cell_font = Font(name="Calibri", size=10, color="1E293B")
        cell_bold_font = Font(name="Calibri", size=10, bold=True, color="0F172A")
        pass_font = Font(name="Calibri", size=10, bold=True, color="16A34A")
        fail_font = Font(name="Calibri", size=10, bold=True, color="DC2626")

        thin_border_side = Side(border_style="thin", color="CBD5E1")
        cell_border = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
        
        center_align = Alignment(horizontal="center", vertical="center")
        left_align = Alignment(horizontal="left", vertical="center")
        right_align = Alignment(horizontal="right", vertical="center")

        school = ranking_data.get("school", {})
        cls = ranking_data.get("class_info", {})
        exam = ranking_data.get("exam_info", {})
        rankings = ranking_data.get("rankings", [])

        # 1. Title Block
        school_name = school.get("name", "Somroyal Educational Management System")
        ws.merge_cells("A1:L1")
        ws["A1"] = school_name.upper()
        ws["A1"].font = title_font
        ws["A1"].alignment = left_align

        ws.merge_cells("A2:L2")
        ws["A2"] = f"Official Class Rankings & Merit List • {school.get('motto', 'Excellence in Education and Character')}"
        ws["A2"].font = subtitle_font
        ws["A2"].alignment = left_align

        # 2. Metadata Block
        ws["A3"] = "Academic Year:"
        ws["A3"].font = meta_bold_font
        ws["B3"] = cls.get("academic_year") or exam.get("academic_year", "-")
        ws["B3"].font = meta_font

        ws["C3"] = "Examination:"
        ws["C3"].font = meta_bold_font
        ws["D3"] = exam.get("name", "Examination")
        ws["D3"].font = meta_font

        ws["E3"] = "Class & Section:"
        ws["E3"].font = meta_bold_font
        ws["F3"] = f"{cls.get('name', 'All Classes')} ({cls.get('division', '')})"
        ws["F3"].font = meta_font

        ws["G3"] = "Total Ranked:"
        ws["G3"].font = meta_bold_font
        ws["H3"] = len(rankings)
        ws["H3"].font = meta_font

        ws["I3"] = "Generated At:"
        ws["I3"].font = meta_bold_font
        ws["J3"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        ws["J3"].font = meta_font

        # 3. Table Headers
        headers = [
            "Rank",
            "Admission No",
            "Student Full Name",
            "Gender",
            "Class Name",
            "Subjects Completed",
            "Absent Subjects",
            "Total Marks",
            "Max Marks",
            "Percentage (%)",
            "Grade",
            "Result Status",
        ]

        header_row_idx = 5
        ws.row_dimensions[header_row_idx].height = 26

        for col_idx, header_text in enumerate(headers, start=1):
            cell = ws.cell(row=header_row_idx, column=col_idx, value=header_text)
            cell.font = white_bold_font
            cell.fill = navy_fill
            cell.alignment = center_align
            cell.border = cell_border

        # 4. Data Rows
        current_row = 6
        for idx, r in enumerate(rankings):
            ws.row_dimensions[current_row].height = 20
            row_fill = alt_row_fill if idx % 2 == 1 else white_fill

            pos = r.get("position", "-")
            adm = r.get("admission_number", "-")
            name = r.get("student_name", "-")
            gender = r.get("gender", "-")
            class_name = r.get("class_name", "-")
            comp_sub = r.get("completed_subjects", 0)
            abs_sub = r.get("absent_subjects", 0)
            tot = r.get("total_marks")
            max_m = r.get("max_possible_marks")
            pct = r.get("percentage")
            grade = r.get("grade", "-")
            status = r.get("pass_fail", "PASS")

            row_values = [
                (pos, cell_bold_font, center_align),
                (adm, cell_font, center_align),
                (name, cell_bold_font, left_align),
                (gender, cell_font, center_align),
                (class_name, cell_font, left_align),
                (comp_sub, cell_font, center_align),
                (abs_sub, cell_font, center_align),
                (round(float(tot), 1) if tot is not None else 0.0, cell_bold_font, right_align),
                (round(float(max_m), 1) if max_m is not None else 0.0, cell_font, right_align),
                (round(float(pct), 1) if pct is not None else 0.0, cell_bold_font, right_align),
                (grade, cell_bold_font, center_align),
                (status, pass_font if status == "PASS" else fail_font, center_align),
            ]

            for col_idx, (val, font_style, align_style) in enumerate(row_values, start=1):
                cell = ws.cell(row=current_row, column=col_idx, value=val)
                cell.font = font_style
                cell.alignment = align_style
                cell.fill = row_fill
                cell.border = cell_border

            current_row += 1

        # 5. Auto-fit column widths
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val = cell.value
                if val:
                    val_str = str(val)
                    if len(val_str) > max_len:
                        max_len = len(val_str)
            ws.column_dimensions[col_letter].width = max(max_len + 3, 10)

        buffer = io.BytesIO()
        wb.save(buffer)
        return buffer.getvalue()
