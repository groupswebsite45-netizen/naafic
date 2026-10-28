import io
import re
import json
from typing import Optional, List, Dict, Any, Tuple
from datetime import date, datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.models.school_class import SchoolClass
from app.models.student_import_log import StudentImportLog
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.student_import import (
    StudentImportRowPreview,
    StudentImportPreviewResponse,
    StudentImportExecuteRequest,
    StudentImportSummaryResponse,
    StudentImportLogResponse,
)
from app.utils.logger import logger


def normalize_header_key(raw: Any) -> str:
    """Normalize header text into standard snake_case key."""
    if raw is None:
        return ""
    text = str(raw).strip().lower()
    # Replace symbols with space
    text = re.sub(r"[^\w\s]", " ", text)
    # Collapse multiple spaces into single underscore
    return "_".join(text.split())


def normalize_somali_phone(phone_raw: Optional[Any]) -> Optional[str]:
    """Normalize phone numbers to canonical +252 standard when possible."""
    if not phone_raw:
        return None
    raw_str = str(phone_raw).strip()
    # If float string like '611234501.0', remove trailing decimal
    if raw_str.endswith(".0"):
        raw_str = raw_str[:-2]
    cleaned = re.sub(r"[^\d+]", "", raw_str)
    if not cleaned:
        return None
    
    # Standardize Somali formats
    if cleaned.startswith("+252"):
        return cleaned
    if cleaned.startswith("252"):
        return f"+{cleaned}"
    if cleaned.startswith("06") or cleaned.startswith("07"):
        return f"+252{cleaned[1:]}"
    if len(cleaned) in (8, 9) and (cleaned.startswith("61") or cleaned.startswith("62") or cleaned.startswith("68") or cleaned.startswith("77")):
        return f"+252{cleaned}"
    if not cleaned.startswith("+"):
        return f"+{cleaned}"
    return cleaned


def normalize_gender(gender_raw: Optional[Any]) -> Optional[str]:
    """Normalize gender input to Male / Female."""
    if not gender_raw:
        return None
    g = str(gender_raw).strip().lower()
    if g in ("m", "male", "boy", "man", "lab", "rag"):
        return "Male"
    if g in ("f", "female", "girl", "woman", "dhedig", "dumar"):
        return "Female"
    return None


def parse_date_of_birth(dob_val: Any) -> Tuple[Optional[str], Optional[str]]:
    """
    Parses date of birth from Excel cells (date, datetime, string, float).
    Returns (formatted_iso_string 'YYYY-MM-DD', error_message).
    """
    if dob_val is None:
        return (None, None)
    
    if isinstance(dob_val, (datetime, date)):
        return (dob_val.strftime("%Y-%m-%d"), None)
    
    val_str = str(dob_val).strip()
    if not val_str:
        return (None, None)
        
    if val_str.endswith(".0") and val_str[:-2].isdigit():
        val_str = val_str[:-2]
        
    for fmt in (
        "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d",
        "%d-%m-%Y", "%m-%d-%Y", "%d.%m.%Y", "%Y.%m.%d",
        "%d %b %Y", "%d %B %Y", "%b %d, %Y", "%B %d, %Y"
    ):
        try:
            dt = datetime.strptime(val_str, fmt)
            return (dt.strftime("%Y-%m-%d"), None)
        except ValueError:
            pass
            
    # Try numeric excel serial float/int if passed as string or numeric
    try:
        if isinstance(dob_val, (int, float)) or val_str.replace(".", "", 1).isdigit():
            serial = float(dob_val)
            if 1000 < serial < 100000:
                from openpyxl.utils.datetime import from_excel
                dt = from_excel(serial)
                if isinstance(dt, (datetime, date)):
                    return (dt.strftime("%Y-%m-%d"), None)
    except Exception:
        pass
        
    return (None, f"Invalid date of birth '{val_str}'. Expected format: YYYY-MM-DD.")


def decompose_student_name(full_name_raw: str) -> Tuple[str, Optional[str], str]:
    """
    Safely decomposes complete student name into (first_name, middle_name, last_name)
    for database column compatibility while preserving complete Somali name on reconstruction.
    """
    cleaned = " ".join(str(full_name_raw).strip().split())
    if not cleaned:
        return ("", None, "")
    
    parts = cleaned.split()
    if len(parts) == 1:
        return (parts[0], None, parts[0])
    elif len(parts) == 2:
        return (parts[0], None, parts[1])
    elif len(parts) == 3:
        return (parts[0], parts[1], parts[2])
    else:
        # 4 or more parts (e.g. Mohamed Ali Hassan Mire)
        return (parts[0], " ".join(parts[1:-1]), parts[-1])


class StudentImportService:
    """Domain service managing bulk Excel template generation, validation preview, and atomic database enrollment."""

    def __init__(self, db: Session):
        self.db = db

    # =========================================================================
    # 1. EXCEL TEMPLATE GENERATION
    # =========================================================================

    def generate_template(self) -> bytes:
        """Generate official .xlsx template supporting complete Student Name and essential school columns."""
        wb = openpyxl.Workbook()
        
        # Sheet 1: Students Import
        ws = wb.active
        ws.title = "Students_Import"

        # Styling Definitions
        header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
        header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
        example_font = Font(name="Segoe UI", size=10, color="334155")
        thin_border = Border(
            left=Side(style="thin", color="CBD5E1"),
            right=Side(style="thin", color="CBD5E1"),
            top=Side(style="thin", color="CBD5E1"),
            bottom=Side(style="thin", color="CBD5E1"),
        )
        center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
        left_align = Alignment(horizontal="left", vertical="center")

        headers = [
            ("student_id", "Student ID", 16),
            ("student_name", "Student Name *", 28),
            ("gender", "Gender * (Male/Female)", 24),
            ("date_of_birth", "Date of Birth (YYYY-MM-DD)", 26),
            ("guardian_name", "Guardian Name *", 26),
            ("guardian_phone", "Guardian Phone *", 22),
            ("address", "Residential Address", 26),
        ]

        # Write Header Row
        for col_idx, (field_key, header_title, col_width) in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_idx, value=header_title)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = center_align
            cell.border = thin_border
            ws.column_dimensions[get_column_letter(col_idx)].width = col_width

        ws.row_dimensions[1].height = 32

        # Add Official Example Rows matching school format
        example_rows = [
            ("1", "Mohamed Ali Mire", "Male", "2012-03-15", "Guardian Ahmed Ali", "+252611234501", "Hawlwadaag, Mogadishu"),
            ("2", "Amina Hassan Noor", "Female", "2011-07-22", "Guardian Hassan Noor", "+252611234502", "Wadajir, Mogadishu"),
            ("3", "Abdiqadir Omar Yusuf", "Male", "2013-01-10", "Guardian Omar Yusuf", "+252611234503", "Hodan, Mogadishu"),
        ]

        for row_idx, row_data in enumerate(example_rows, 2):
            ws.row_dimensions[row_idx].height = 24
            for col_idx, val in enumerate(row_data, 1):
                cell = ws.cell(row=row_idx, column=col_idx, value=val)
                cell.font = example_font
                cell.alignment = left_align
                cell.border = thin_border

        # Sheet 2: Guidelines
        ws_guide = wb.create_sheet(title="Instructions")
        guide_title_fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
        guide_title_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
        
        guide_headers = ["Field Name", "Required?", "Example / Format", "Description"]
        for c_idx, gh in enumerate(guide_headers, 1):
            cell = ws_guide.cell(row=1, column=c_idx, value=gh)
            cell.fill = guide_title_fill
            cell.font = guide_title_font
            cell.alignment = left_align
            cell.border = thin_border

        guidelines = [
            ("Student ID", "Optional", "1 or ADM-2026-001", "Existing admission number or ID number."),
            ("Student Name", "REQUIRED", "Mohamed Ali Mire", "Complete 2, 3, or 4-part Somali student name in one column."),
            ("Gender", "REQUIRED", "Male / Female", "Male (or M) or Female (or F)."),
            ("Date of Birth", "Optional", "2012-03-15", "Date of birth in YYYY-MM-DD or standard Excel date format."),
            ("Guardian Name", "REQUIRED", "Guardian Ahmed Ali", "Primary parent or guardian's full name."),
            ("Guardian Phone", "REQUIRED", "+252611234501", "Active guardian contact phone number."),
            ("Residential Address", "Optional", "Hawlwadaag, Mogadishu", "District or home residential address."),
        ]

        for r_idx, row_info in enumerate(guidelines, 2):
            ws_guide.row_dimensions[r_idx].height = 22
            for c_idx, g_val in enumerate(row_info, 1):
                cell = ws_guide.cell(row=r_idx, column=c_idx, value=g_val)
                cell.font = example_font
                cell.alignment = left_align
                cell.border = thin_border

        ws_guide.column_dimensions["A"].width = 20
        ws_guide.column_dimensions["B"].width = 14
        ws_guide.column_dimensions["C"].width = 24
        ws_guide.column_dimensions["D"].width = 50

        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()

    # =========================================================================
    # 2. SERVER-SIDE PARSING & VALIDATION PREVIEW
    # =========================================================================

    def parse_and_validate_excel(
        self,
        file_bytes: bytes,
        class_id: int,
        academic_year: str,
    ) -> StudentImportPreviewResponse:
        """Parse Excel bytes and perform deep PostgreSQL validation for each student row."""
        school_class = self.db.query(SchoolClass).filter(SchoolClass.id == class_id).first()
        if not school_class:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Selected class with ID {class_id} does not exist in the system."
            )
        if school_class.status != "ACTIVE":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Selected class '{school_class.name}' is currently {school_class.status}. Only ACTIVE classes can receive student imports."
            )

        try:
            wb = openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)
            ws = wb.active
        except Exception as e:
            logger.error(f"Excel parsing exception: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to read this Excel file. Please download the official template and try again."
            )

        # ---------------------------------------------------------------------
        # Dynamic Header Normalization & Mapping
        # ---------------------------------------------------------------------
        header_map: Dict[str, int] = {}
        generic_phone_col: Optional[int] = None
        generic_name_col: Optional[int] = None

        for col_idx in range(1, ws.max_column + 1):
            val = ws.cell(row=1, column=col_idx).value
            if not val:
                continue
            k = normalize_header_key(val)
            if not k:
                continue

            # Complete Student Name (Format A)
            if k in ("student_name", "full_name", "student_full_name", "fullname", "magaca_ardayga", "magaca_oo_dhammeystiran"):
                header_map["student_name"] = col_idx
            elif k in ("student", "name"):
                generic_name_col = col_idx
            
            # Split First / Middle / Last Name (Format B)
            elif k in ("first_name", "firstname", "given_name", "magaca_hore"):
                header_map["first_name"] = col_idx
            elif k in ("middle_name", "middlename"):
                header_map["middle_name"] = col_idx
            elif k in ("last_name", "lastname", "surname", "family_name"):
                header_map["last_name"] = col_idx

            # Student ID / Admission Number
            elif k in ("student_id", "admission_number", "admission_no", "admission", "adm_no", "id", "student_no", "number", "no"):
                header_map["admission_number"] = col_idx

            # Gender
            elif k in ("gender", "sex", "jinsiga"):
                header_map["gender"] = col_idx

            # Date of Birth
            elif k in ("date_of_birth", "dob", "birth_date", "birthdate", "date_birth", "taariikhda_dhalashada"):
                header_map["date_of_birth"] = col_idx

            # Guardian Name
            elif k in ("guardian_name", "parent_name", "parent_guardian_name", "guardian", "parent", "magaca_waalidka"):
                header_map["guardian_name"] = col_idx

            # Guardian Phone
            elif k in ("guardian_phone", "parent_phone", "guardian_contact", "parent_contact", "talefoonka_waalidka"):
                header_map["guardian_phone"] = col_idx
            elif k in ("student_phone", "student_contact"):
                header_map["student_phone"] = col_idx
            elif k in ("phone", "contact", "mobile", "telephone", "phone_number"):
                generic_phone_col = col_idx

            # Optional Fields
            elif k in ("guardian_email", "parent_email", "email"):
                header_map["guardian_email"] = col_idx
            elif k in ("guardian_relationship", "relationship", "relation"):
                header_map["guardian_relationship"] = col_idx
            elif k in ("address", "residential_address", "location", "residence", "cinwaanka"):
                header_map["address"] = col_idx

        # Fallback aliases
        if "student_name" not in header_map and generic_name_col and "first_name" not in header_map:
            header_map["student_name"] = generic_name_col
        if "guardian_phone" not in header_map and generic_phone_col:
            header_map["guardian_phone"] = generic_phone_col

        # ---------------------------------------------------------------------
        # Header Presence Validation
        # ---------------------------------------------------------------------
        has_student_name = "student_name" in header_map
        has_split_name = ("first_name" in header_map and "last_name" in header_map)

        missing_headers = []
        if not (has_student_name or has_split_name):
            missing_headers.append("Student Name")
        if "gender" not in header_map:
            missing_headers.append("Gender")
        if "guardian_name" not in header_map:
            missing_headers.append("Guardian Name")
        if "guardian_phone" not in header_map:
            missing_headers.append("Guardian Phone")

        if missing_headers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Excel template error: Missing required column(s): {', '.join(missing_headers)}. Please use the official template with 'Student Name', 'Gender', 'Guardian Name', 'Guardian Phone'."
            )

        preview_rows: List[StudentImportRowPreview] = []
        valid_cnt = 0
        warn_cnt = 0
        err_cnt = 0
        exists_cnt = 0

        # Process each row
        for row_idx in range(2, ws.max_row + 1):
            def get_val(key: str) -> Optional[Any]:
                col = header_map.get(key)
                if not col:
                    return None
                val = ws.cell(row=row_idx, column=col).value
                return val

            raw_student_name = get_val("student_name")
            raw_first_name = get_val("first_name")
            raw_middle_name = get_val("middle_name")
            raw_last_name = get_val("last_name")

            # Check for completely empty row
            all_empty = True
            for col in range(1, ws.max_column + 1):
                cval = ws.cell(row=row_idx, column=col).value
                if cval is not None and str(cval).strip():
                    all_empty = False
                    break
            if all_empty:
                continue

            # Determine Complete Name and decomposed parts
            display_student_name = ""
            first_name = ""
            middle_name: Optional[str] = None
            last_name = ""

            if raw_student_name and str(raw_student_name).strip():
                display_student_name = " ".join(str(raw_student_name).strip().split())
                first_name, middle_name, last_name = decompose_student_name(display_student_name)
            elif raw_first_name or raw_last_name:
                f = str(raw_first_name).strip() if raw_first_name else ""
                m = str(raw_middle_name).strip() if raw_middle_name else ""
                l = str(raw_last_name).strip() if raw_last_name else ""
                parts = [p for p in (f, m, l) if p]
                display_student_name = " ".join(parts)
                first_name = f or (parts[0] if parts else "")
                middle_name = m or None
                last_name = l or (parts[-1] if parts else "")

            gender_raw = get_val("gender")
            dob_raw = get_val("date_of_birth")
            guardian_name_raw = get_val("guardian_name")
            guardian_phone_raw = get_val("guardian_phone")
            guardian_email_raw = get_val("guardian_email")
            guardian_relationship_raw = get_val("guardian_relationship")
            student_phone_raw = get_val("student_phone")
            address_raw = get_val("address")
            admission_number_raw = get_val("admission_number")

            guardian_name = str(guardian_name_raw).strip() if guardian_name_raw is not None else None
            guardian_email = str(guardian_email_raw).strip() if guardian_email_raw is not None else None
            guardian_relationship = str(guardian_relationship_raw).strip() if guardian_relationship_raw is not None else "Parent"
            address = str(address_raw).strip() if address_raw is not None else None
            
            admission_number_clean: Optional[str] = None
            if admission_number_raw is not None:
                adm_str = str(admission_number_raw).strip()
                if adm_str.endswith(".0"):
                    adm_str = adm_str[:-2]
                admission_number_clean = adm_str if adm_str else None

            errors: List[str] = []
            warnings: List[str] = []

            # Validation 1: Student Name
            if not display_student_name or len(display_student_name) < 2:
                errors.append("Student Name is required.")

            # Validation 2: Gender
            normalized_gender = normalize_gender(gender_raw)
            if not normalized_gender:
                errors.append(f"Invalid gender '{gender_raw}'. Must be 'Male' or 'Female'.")

            # Validation 3: Guardian Details
            if not guardian_name:
                errors.append("Guardian name is required.")
            normalized_guardian_phone = normalize_somali_phone(guardian_phone_raw)
            if not normalized_guardian_phone:
                errors.append("Guardian phone is required and must be a valid Somali phone number.")

            normalized_student_phone = normalize_somali_phone(student_phone_raw)

            # Validation 4: Date of Birth
            formatted_dob, dob_err = parse_date_of_birth(dob_raw)
            if dob_err:
                errors.append(dob_err)

            # Validation 5: Check Database Uniqueness & Enrollments
            is_existing_student = False
            is_already_enrolled = False
            existing_student_id = None
            existing_class_name = None

            if admission_number_clean:
                # Check by admission number
                existing_std = self.db.query(Student).filter(
                    func.lower(Student.admission_number) == func.lower(admission_number_clean)
                ).first()
                if existing_std:
                    is_existing_student = True
                    existing_student_id = existing_std.id
                    enr = self.db.query(StudentEnrollment).filter(
                        StudentEnrollment.student_id == existing_std.id,
                        StudentEnrollment.academic_year == academic_year.strip(),
                    ).first()
                    if enr:
                        is_already_enrolled = True
                        existing_class_name = enr.school_class.name if enr.school_class else f"Class #{enr.class_id}"
                        warnings.append(f"Student ID {admission_number_clean} is already enrolled in {existing_class_name} for {academic_year}.")

            if not is_existing_student and display_student_name:
                # Check by student name + guardian phone
                existing_std = self.db.query(Student).filter(
                    func.lower(Student.first_name) == func.lower(first_name),
                    func.lower(Student.last_name) == func.lower(last_name),
                    Student.guardian_phone == normalized_guardian_phone,
                ).first()
                if existing_std:
                    is_existing_student = True
                    existing_student_id = existing_std.id
                    enr = self.db.query(StudentEnrollment).filter(
                        StudentEnrollment.student_id == existing_std.id,
                        StudentEnrollment.academic_year == academic_year.strip(),
                    ).first()
                    if enr:
                        is_already_enrolled = True
                        existing_class_name = enr.school_class.name if enr.school_class else f"Class #{enr.class_id}"
                        warnings.append(f"Matching student already enrolled in {existing_class_name} for {academic_year}.")

            # Determine Row Status
            if errors:
                status_str = "ERROR"
                reason_str = " | ".join(errors)
                err_cnt += 1
            elif is_already_enrolled:
                status_str = "ALREADY_EXISTS"
                reason_str = f"Already enrolled in {existing_class_name} for {academic_year}."
                exists_cnt += 1
            elif is_existing_student:
                status_str = "WARNING"
                reason_str = "Existing student in database (not enrolled in this academic year)."
                warn_cnt += 1
            else:
                status_str = "VALID"
                reason_str = "Ready for enrollment."
                valid_cnt += 1

            preview_rows.append(
                StudentImportRowPreview(
                    row_number=row_idx,
                    admission_number=admission_number_clean,
                    student_name=display_student_name,
                    full_name=display_student_name,
                    first_name=first_name,
                    middle_name=middle_name,
                    last_name=last_name,
                    gender=normalized_gender or (str(gender_raw) if gender_raw is not None else None),
                    date_of_birth=formatted_dob,
                    guardian_name=guardian_name,
                    guardian_phone=normalized_guardian_phone or (str(guardian_phone_raw) if guardian_phone_raw is not None else None),
                    guardian_email=guardian_email,
                    guardian_relationship=guardian_relationship,
                    phone=normalized_student_phone,
                    address=address,
                    status=status_str,
                    error_reason=reason_str,
                    is_existing_student=is_existing_student,
                    is_already_enrolled=is_already_enrolled,
                    existing_student_id=existing_student_id,
                    existing_class_name=existing_class_name,
                )
            )

        if len(preview_rows) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No student records were found in this Excel file."
            )

        return StudentImportPreviewResponse(
            success=True,
            total_rows=len(preview_rows),
            valid_rows=valid_cnt,
            warning_rows=warn_cnt,
            error_rows=err_cnt,
            already_exists_rows=exists_cnt,
            class_id=school_class.id,
            class_name=school_class.name,
            academic_year=academic_year.strip(),
            destination={
                "class_id": school_class.id,
                "class_name": school_class.name,
                "academic_year_id": academic_year.strip(),
                "academic_year": academic_year.strip(),
            },
            summary={
                "total_rows": len(preview_rows),
                "valid_rows": valid_cnt,
                "invalid_rows": err_cnt,
                "existing_rows": exists_cnt + warn_cnt,
            },
            rows=preview_rows,
        )

    # =========================================================================
    # 3. ATOMIC TRANSACTION IMPORT EXECUTION
    # =========================================================================

    def execute_import(
        self,
        request: StudentImportExecuteRequest,
        admin_user: User,
    ) -> StudentImportSummaryResponse:
        """Atomically commit valid students and enrollments to PostgreSQL."""
        school_class = self.db.query(SchoolClass).filter(SchoolClass.id == request.class_id).first()
        if not school_class:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Selected destination class with ID {request.class_id} not found."
            )

        academic_year = request.academic_year.strip()
        imported_cnt = 0
        already_enrolled_cnt = 0
        skipped_cnt = 0
        failed_cnt = 0
        errors: List[str] = []

        current_year = datetime.now().year
        max_adm_row = self.db.query(func.max(Student.id)).scalar() or 0
        seq_counter = int(max_adm_row) + 1

        try:
            for row in request.rows:
                if row.status == "ERROR":
                    skipped_cnt += 1
                    continue

                if row.is_already_enrolled:
                    already_enrolled_cnt += 1
                    skipped_cnt += 1
                    continue

                # Handle Existing Student not yet enrolled
                if row.is_existing_student and row.existing_student_id:
                    if not request.enroll_existing_students:
                        skipped_cnt += 1
                        continue

                    existing_enr = self.db.query(StudentEnrollment).filter(
                        StudentEnrollment.student_id == row.existing_student_id,
                        StudentEnrollment.academic_year == academic_year,
                    ).first()
                    if not existing_enr:
                        enrollment = StudentEnrollment(
                            student_id=row.existing_student_id,
                            class_id=school_class.id,
                            academic_year=academic_year,
                            start_date=date.today(),
                            status="ACTIVE",
                        )
                        self.db.add(enrollment)
                        imported_cnt += 1
                    else:
                        already_enrolled_cnt += 1
                        skipped_cnt += 1
                    continue

                # Prepare student name decomposition
                s_name = row.student_name or row.full_name or ""
                if s_name and (not row.first_name or not row.last_name):
                    f_name, m_name, l_name = decompose_student_name(s_name)
                else:
                    f_name = row.first_name or (s_name.split()[0] if s_name else "Student")
                    m_name = row.middle_name
                    l_name = row.last_name or (s_name.split()[-1] if s_name else "Student")

                # Generate or assign unique admission number
                adm_num = row.admission_number
                if not adm_num:
                    candidate_adm = f"ADM-{current_year}-{seq_counter:04d}"
                    while self.db.query(Student).filter(Student.admission_number == candidate_adm).first():
                        seq_counter += 1
                        candidate_adm = f"ADM-{current_year}-{seq_counter:04d}"
                    adm_num = candidate_adm
                    seq_counter += 1
                else:
                    # If admission number already in DB (from duplicate check), generate distinct if needed
                    existing_adm = self.db.query(Student).filter(Student.admission_number == adm_num).first()
                    if existing_adm:
                        candidate_adm = f"{adm_num}-{seq_counter:02d}"
                        adm_num = candidate_adm
                        seq_counter += 1

                # Parse DOB
                parsed_dob = None
                if row.date_of_birth:
                    try:
                        parsed_dob = datetime.strptime(row.date_of_birth, "%Y-%m-%d").date()
                    except Exception:
                        pass

                new_student = Student(
                    admission_number=adm_num,
                    first_name=f_name.strip(),
                    middle_name=m_name.strip() if m_name else None,
                    last_name=l_name.strip(),
                    gender=row.gender or "Male",
                    date_of_birth=parsed_dob,
                    phone=row.phone,
                    address=row.address,
                    guardian_name=row.guardian_name,
                    guardian_phone=row.guardian_phone,
                    guardian_email=row.guardian_email,
                    guardian_relationship=row.guardian_relationship or "Parent",
                    admission_date=date.today(),
                    status="ACTIVE",
                )
                self.db.add(new_student)
                self.db.flush()

                # Create Class Enrollment
                enrollment = StudentEnrollment(
                    student_id=new_student.id,
                    class_id=school_class.id,
                    academic_year=academic_year,
                    start_date=date.today(),
                    status="ACTIVE",
                )
                self.db.add(enrollment)
                imported_cnt += 1

            # Log Audit Record
            import_log = StudentImportLog(
                admin_user_id=admin_user.id,
                file_name=request.file_name or "students.xlsx",
                class_id=school_class.id,
                academic_year=academic_year,
                total_rows=len(request.rows),
                imported_count=imported_cnt,
                already_enrolled_count=already_enrolled_cnt,
                skipped_count=skipped_cnt,
                failed_count=failed_cnt,
                details=json.dumps({
                    "destination_class": school_class.name,
                    "academic_year": academic_year,
                    "enroll_existing_flag": request.enroll_existing_students,
                }),
            )
            self.db.add(import_log)

            # System Audit Log
            self.db.add(
                AuditLog(
                    action="STUDENT_BULK_IMPORT",
                    user_id=admin_user.id,
                    details=json.dumps({
                        "file_name": request.file_name,
                        "class_id": school_class.id,
                        "class_name": school_class.name,
                        "academic_year": academic_year,
                        "imported_count": imported_cnt,
                        "skipped_count": skipped_cnt,
                    }),
                )
            )

            self.db.commit()

            return StudentImportSummaryResponse(
                success=True,
                total_rows=len(request.rows),
                imported_count=imported_cnt,
                already_enrolled_count=already_enrolled_cnt,
                skipped_count=skipped_cnt,
                failed_count=failed_cnt,
                class_id=school_class.id,
                class_name=school_class.name,
                academic_year=academic_year,
                message=f"Successfully imported and enrolled {imported_cnt} student(s) into {school_class.name} ({academic_year}).",
                errors=errors,
            )

        except Exception as e:
            self.db.rollback()
            logger.exception("Bulk student import failed during transaction")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Import transaction failed: {str(e)}"
            )

    # =========================================================================
    # 4. AUDIT & IMPORT HISTORY
    # =========================================================================

    def get_import_history(self, limit: int = 50) -> List[StudentImportLogResponse]:
        """Fetch audit log history of bulk Excel imports."""
        logs = (
            self.db.query(StudentImportLog)
            .order_by(StudentImportLog.created_at.desc())
            .limit(limit)
            .all()
        )
        res = []
        for l in logs:
            res.append(
                StudentImportLogResponse(
                    id=l.id,
                    file_name=l.file_name,
                    class_id=l.class_id,
                    class_name=l.school_class.name if l.school_class else None,
                    academic_year=l.academic_year,
                    total_rows=l.total_rows,
                    imported_count=l.imported_count,
                    already_enrolled_count=l.already_enrolled_count,
                    skipped_count=l.skipped_count,
                    failed_count=l.failed_count,
                    admin_name=l.admin_user.full_name if l.admin_user else None,
                    created_at=l.created_at,
                )
            )
        return res
