import re
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc

from app.models.school_class import SchoolClass
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.models.class_promotion import ClassPromotionBatch, ClassPromotionRecord
from app.models.user import User
from app.repositories.promotion_repo import PromotionRepository
from app.repositories.student_repo import StudentRepository
from app.repositories.class_repo import ClassRepository
from app.repositories.audit_repo import AuditLogRepository
from app.schemas.class_promotion import (
    ClassPromotionMappingItem,
    ClassPromotionMappingSuggestion,
    TargetClassOption,
    SuggestedMappingsResponse,
    PromotionPreviewRequest,
    StudentPromotionPreviewItem,
    ClassMappingPreviewSummary,
    BulkPromotionPreviewResponse,
    ExecuteBulkPromotionPayload,
    IndividualClassChangePayload,
    IndividualClassChangeResponse,
    ClassLevelPromotionPayload,
    IndividualStudentPromotionPayload,
    StudentSearchForPromotionItem,
    StudentPromotionOverrideItem,
    PromotionRecordItemResponse,
    PromotionBatchResponse,
    BatchRollbackResponse,
)


class ClassPromotionService:
    """
    Comprehensive service for:
    1. Separate Primary (Grade 1..8) and Secondary (Form 1..4) promotion.
    2. Automatic section-preserving class-to-class progression.
    3. Bulk promotion, single-class promotion, and individual student promotion.
    4. Repeat, transfer, graduation, and exclusion workflows.
    5. Atomic transaction execution, validation, audit history, and safe rollback.
    """

    def __init__(self, db: Session):
        self.db = db
        self.repo = PromotionRepository(db)
        self.student_repo = StudentRepository(db)
        self.class_repo = ClassRepository(db)
        self.audit_repo = AuditLogRepository(db)

    # --------------------------------------------------------------------------
    # Helper Utilities
    # --------------------------------------------------------------------------
    def _parse_class_info(self, c: SchoolClass) -> Dict[str, Any]:
        """
        Extract education division, level number, level name, and section.
        Supports Somali / Somroyal EMS standard:
          Primary: Grade 1..8 (Terminal: Grade 8)
          Secondary: Form 1..4 (Terminal: Form 4)
        """
        raw_name = (c.name or "").strip()
        raw_level = (c.level or "").strip()
        raw_div = (c.division or "").strip().upper()
        raw_sec = (c.section or "").strip()

        # Determine division
        if re.search(r'\bform\b', raw_name, re.IGNORECASE) or re.search(r'\bform\b', raw_level, re.IGNORECASE):
            division = "SECONDARY"
        elif re.search(r'\bgrade\b', raw_name, re.IGNORECASE) or re.search(r'\bgrade\b', raw_level, re.IGNORECASE):
            division = "PRIMARY"
        elif raw_div in ["PRIMARY", "SECONDARY"]:
            division = raw_div
        else:
            division = "PRIMARY"

        # Determine level prefix and number
        level_number: Optional[int] = None
        prefix: str = "Grade" if division == "PRIMARY" else "Form"

        # Try match from level or name
        match = re.search(r'(form|grade|class|standard)\s*(\d+)', raw_level or raw_name, re.IGNORECASE)
        if match:
            prefix = match.group(1).title()
            level_number = int(match.group(2))
        else:
            # Fallback numeric search
            num_match = re.search(r'\b(\d+)\b', raw_level or raw_name)
            if num_match:
                level_number = int(num_match.group(1))

        level_name = f"{prefix} {level_number}" if level_number is not None else (raw_level or raw_name)

        # Determine section (e.g., "A", "B", "C", "Stream A", "12D7")
        section = raw_sec
        if not section:
            # Check pattern like "Grade 4 - A" or "Grade 4A"
            dash_match = re.search(r'-\s*([A-Za-z0-9\s]+)$', raw_name)
            if dash_match:
                section = dash_match.group(1).strip()
            else:
                tail_letter = re.search(r'(?:grade|form)\s*\d+\s*([A-Za-z])$', raw_name, re.IGNORECASE)
                if tail_letter:
                    section = tail_letter.group(1).upper()

        # Terminal determination
        is_terminal = False
        if division == "PRIMARY" and level_number is not None and level_number >= 8:
            is_terminal = True
        elif division == "SECONDARY" and level_number is not None and level_number >= 4:
            is_terminal = True

        return {
            "class": c,
            "division": division,
            "level_name": level_name,
            "level_number": level_number,
            "section": section or None,
            "is_terminal": is_terminal
        }

    def _next_academic_year(self, current_year: str) -> str:
        """Academic year is strictly unified to 2026/2027 across the entire system."""
        return "2026/2027"

    def _build_year_filter(self, year_str: str):
        """Build SQLAlchemy filter matching both 'YYYY/YYYY' and 'YYYY-YYYY'."""
        clean = year_str.strip()
        slash_ver = clean.replace('-', '/')
        hyphen_ver = clean.replace('/', '-')
        return or_(
            StudentEnrollment.academic_year == clean,
            StudentEnrollment.academic_year == slash_ver,
            StudentEnrollment.academic_year == hyphen_ver
        )

    # --------------------------------------------------------------------------
    # 1. Suggested Mappings (Section Preserving & Separated Levels)
    # --------------------------------------------------------------------------
    def get_suggested_mappings(
        self,
        source_year: Optional[str] = None,
        target_year: Optional[str] = None,
        education_level: Optional[str] = None
    ) -> SuggestedMappingsResponse:
        """
        Prepare intelligent class-to-class progression mappings:
        - Primary: Grade 1 -> Grade 2 ... Grade 7 -> Grade 8 -> Graduation
        - Secondary: Form 1 -> Form 2 ... Form 3 -> Form 4 -> Graduation
        - Section preservation: Grade 4A -> Grade 5A, Grade 4B -> Grade 5B
        - Warning flag if destination class or section does not exist.
        - Strict education level separation.
        """
        all_active_classes = self.db.query(SchoolClass).filter(SchoolClass.status == "ACTIVE").all()

        # Discover distinct academic years
        class_years = [c.academic_year for c in all_active_classes if c.academic_year]
        enr_years = [y[0] for y in self.db.query(StudentEnrollment.academic_year).distinct().all() if y[0]]
        all_years = ["2026/2027"]
        resolved_source_year = "2026/2027"
        resolved_target_year = "2026/2027"

        # Parse all classes
        parsed_classes = [self._parse_class_info(c) for c in all_active_classes]

        # Filter by education level if provided (PRIMARY or SECONDARY)
        req_level = education_level.upper().strip() if education_level else None
        if req_level in ["PRIMARY", "SECONDARY"]:
            parsed_classes = [p for p in parsed_classes if p["division"] == req_level]

        # Separate into source classes and target candidate classes
        source_classes_info = []
        target_classes_info = []

        year_slash = resolved_source_year.replace('-', '/')
        year_hyphen = resolved_source_year.replace('/', '-')

        target_slash = resolved_target_year.replace('-', '/')
        target_hyphen = resolved_target_year.replace('/', '-')

        for p in parsed_classes:
            c_yr = p["class"].academic_year or ""
            is_source_yr = (c_yr in [resolved_source_year, year_slash, year_hyphen])
            is_target_yr = (c_yr in [resolved_target_year, target_slash, target_hyphen])

            # Count enrolled students for source academic year
            enr_count = self.db.query(StudentEnrollment).filter(
                StudentEnrollment.class_id == p["class"].id,
                self._build_year_filter(resolved_source_year),
                StudentEnrollment.status == "ACTIVE"
            ).count()

            p["enrolled_count"] = enr_count

            # Source candidate
            if is_source_yr or enr_count > 0:
                source_classes_info.append(p)

            # Target candidate
            if is_target_yr:
                target_classes_info.append(p)

        # Fallback if specific year classes not separated yet
        if not source_classes_info:
            source_classes_info = parsed_classes
        if not target_classes_info:
            target_classes_info = parsed_classes

        # Sort source classes by division, level_number, section, name
        def sort_key(item):
            div_val = 0 if item["division"] == "PRIMARY" else 1
            lvl_val = item["level_number"] if item["level_number"] is not None else 99
            sec_val = (item["section"] or "").upper()
            return (div_val, lvl_val, sec_val, item["class"].name)

        source_classes_info.sort(key=sort_key)

        mappings: List[ClassPromotionMappingSuggestion] = []

        for src in source_classes_info:
            c: SchoolClass = src["class"]
            div = src["division"]
            lvl_num = src["level_number"]
            lvl_name = src["level_name"]
            sec = src["section"]
            enrolled = src["enrolled_count"]
            is_terminal = src["is_terminal"]

            to_class_id = None
            to_class_name = None
            to_class_code = None
            action = "PROMOTE"
            missing_warning = False
            warning_msg = None

            if is_terminal:
                # Grade 8 (Primary) or Form 4 (Secondary) -> Graduation
                action = "GRADUATE"
                to_class_id = None
                missing_warning = False
                warning_msg = f"Final grade ({lvl_name}). Eligible students will complete/graduate."
            else:
                next_lvl_num = (lvl_num + 1) if lvl_num is not None else None
                if next_lvl_num is not None:
                    # Look for candidate destination in target_classes_info
                    # 1st Priority: Same division, next level number, and SAME SECTION
                    matching_dest = None
                    for tc in target_classes_info:
                        if (
                            tc["division"] == div and
                            tc["level_number"] == next_lvl_num and
                            tc["class"].id != c.id
                        ):
                            # Compare section (case-insensitive)
                            src_sec_clean = (sec or "").strip().upper()
                            tgt_sec_clean = (tc["section"] or "").strip().upper()
                            if src_sec_clean and tgt_sec_clean and src_sec_clean == tgt_sec_clean:
                                matching_dest = tc
                                break
                            elif not src_sec_clean and not tgt_sec_clean:
                                matching_dest = tc
                                break

                    # If no exact section match found, do NOT arbitrarily lump into Section A!
                    # Flag a warning so admin can map or create the destination class
                    if matching_dest:
                        to_class_id = matching_dest["class"].id
                        to_class_name = matching_dest["class"].name
                        to_class_code = matching_dest["class"].code
                        action = "PROMOTE"
                    else:
                        to_class_id = None
                        action = "PROMOTE"
                        missing_warning = True
                        sec_label = f"Section '{sec}'" if sec else "Same Section"
                        target_prefix = "Grade" if div == "PRIMARY" else "Form"
                        warning_msg = (
                            f"Destination class for '{c.name}' ({target_prefix} {next_lvl_num} {sec_label}) "
                            f"was not found in target academic year {resolved_target_year}. Please map destination."
                        )
                else:
                    action = "NO_CHANGE"
                    missing_warning = True
                    warning_msg = f"Could not determine next numeric grade for '{c.name}'."

            mappings.append(ClassPromotionMappingSuggestion(
                from_class_id=c.id,
                from_class_name=c.name,
                from_class_code=c.code,
                education_level=div,
                level_name=lvl_name,
                level_number=lvl_num,
                section=sec,
                to_class_id=to_class_id,
                to_class_name=to_class_name,
                to_class_code=to_class_code,
                action=action,
                student_count=enrolled,
                is_terminal_class=is_terminal,
                missing_destination_warning=missing_warning,
                warning_message=warning_msg
            ))

        # Available target class options (filtered by education level to prevent cross-mixing)
        target_options: List[TargetClassOption] = []
        target_candidates = [p for p in parsed_classes if (not req_level or p["division"] == req_level)]
        target_candidates.sort(key=sort_key)

        for tc in target_candidates:
            c = tc["class"]
            enr_c = self.db.query(StudentEnrollment).filter(
                StudentEnrollment.class_id == c.id,
                StudentEnrollment.status == "ACTIVE"
            ).count()

            target_options.append(TargetClassOption(
                id=c.id,
                name=c.name,
                code=c.code,
                division=tc["division"],
                level=tc["level_name"],
                section=tc["section"],
                academic_year=c.academic_year,
                capacity=c.capacity,
                enrolled_count=enr_c,
                status=c.status
            ))

        return SuggestedMappingsResponse(
            source_academic_year=resolved_source_year,
            target_academic_year=resolved_target_year,
            education_level=req_level,
            mappings=mappings,
            available_target_classes=target_options,
            academic_years=all_years
        )

    # --------------------------------------------------------------------------
    # 2. Live Preview and Validation
    # --------------------------------------------------------------------------
    def preview_bulk_promotion(self, payload: PromotionPreviewRequest) -> BulkPromotionPreviewResponse:
        """
        Validate and live preview the proposed promotion mappings before execution.
        Evaluates each student's eligibility, overrides, and detects duplicate enrollments.
        """
        source_year = payload.source_academic_year.strip()
        target_year = payload.target_academic_year.strip()

        class_summaries: List[ClassMappingPreviewSummary] = []
        student_previews: List[StudentPromotionPreviewItem] = []
        validation_errors: List[str] = []

        total_affected = 0
        total_to_promote = 0
        total_to_repeat = 0
        total_to_graduate = 0
        total_excluded = 0
        total_errors = 0
        missing_dest_count = 0

        # Build overrides lookup by student_id
        overrides_map: Dict[int, StudentPromotionOverrideItem] = {}
        if payload.student_overrides:
            for ov in payload.student_overrides:
                overrides_map[ov.student_id] = ov

        # Load referenced classes
        all_class_ids = set()
        for m in payload.mappings:
            all_class_ids.add(m.from_class_id)
            if m.to_class_id:
                all_class_ids.add(m.to_class_id)
        if payload.student_overrides:
            for ov in payload.student_overrides:
                if ov.target_class_id:
                    all_class_ids.add(ov.target_class_id)

        classes_map = {
            c.id: c for c in self.db.query(SchoolClass).filter(SchoolClass.id.in_(all_class_ids)).all()
        }

        for mapping in payload.mappings:
            from_class = classes_map.get(mapping.from_class_id)
            if not from_class:
                err = f"Source class ID {mapping.from_class_id} not found."
                validation_errors.append(err)
                continue

            from_info = self._parse_class_info(from_class)
            to_class = classes_map.get(mapping.to_class_id) if mapping.to_class_id else None
            action = mapping.action.upper().strip()

            if action == "PROMOTE":
                if not to_class:
                    missing_dest_count += 1
                    err = f"Destination class is not selected for '{from_class.name}'."
                    validation_errors.append(err)
                elif from_class.id == to_class.id:
                    err = f"Source and Destination class cannot be identical ('{from_class.name}')."
                    validation_errors.append(err)
                elif to_class.status != "ACTIVE":
                    err = f"Destination class '{to_class.name}' is inactive."
                    validation_errors.append(err)

            # Fetch active enrollments in from_class for source_year
            enrollments = (
                self.db.query(StudentEnrollment)
                .filter(
                    StudentEnrollment.class_id == from_class.id,
                    self._build_year_filter(source_year),
                    StudentEnrollment.status == "ACTIVE"
                )
                .all()
            )

            # Fallback if enrollments aren't labeled with exact year string
            if not enrollments:
                enrollments = (
                    self.db.query(StudentEnrollment)
                    .filter(
                        StudentEnrollment.class_id == from_class.id,
                        StudentEnrollment.status == "ACTIVE"
                    )
                    .all()
                )

            class_valid_count = 0
            class_error_count = 0

            for enr in enrollments:
                student = enr.student
                if not student:
                    continue

                total_affected += 1
                is_valid = True
                validation_msg = None
                student_status = "READY"
                student_action = action
                resolved_target_class = to_class

                # Check if this student has an individual override
                if student.id in overrides_map:
                    ov = overrides_map[student.id]
                    student_action = ov.action.upper().strip()
                    if ov.target_class_id:
                        resolved_target_class = classes_map.get(ov.target_class_id)
                    elif student_action == "REPEAT":
                        resolved_target_class = from_class

                # Validate student status
                if student.status != "ACTIVE":
                    is_valid = False
                    student_status = "VALIDATION_ERROR"
                    validation_msg = f"Student is {student.status}, cannot be promoted."
                    class_error_count += 1
                    total_errors += 1

                # If action is PROMOTE or TRANSFER and no destination class resolved
                if is_valid and student_action in ["PROMOTE", "TRANSFER"] and not resolved_target_class:
                    is_valid = False
                    student_status = "VALIDATION_ERROR"
                    validation_msg = "Missing destination class."
                    class_error_count += 1
                    total_errors += 1

                # Check for existing enrollment in target academic year (prevent duplicates)
                if is_valid and student_action in ["PROMOTE", "REPEAT", "TRANSFER"]:
                    existing_target_enr = (
                        self.db.query(StudentEnrollment)
                        .filter(
                            StudentEnrollment.student_id == student.id,
                            self._build_year_filter(target_year)
                        )
                        .first()
                    )

                    if existing_target_enr and (source_year != target_year or existing_target_enr.id != enr.id):
                        is_valid = False
                        student_status = "ALREADY_ENROLLED"
                        tgt_name = (
                            existing_target_enr.school_class.name
                            if existing_target_enr.school_class else f"Class ID {existing_target_enr.class_id}"
                        )
                        validation_msg = f"Student already enrolled in {tgt_name} for {target_year}."
                        class_error_count += 1
                        total_errors += 1

                # Update counts
                if is_valid:
                    class_valid_count += 1
                    if student_action == "PROMOTE":
                        total_to_promote += 1
                        student_status = "READY"
                    elif student_action == "REPEAT":
                        total_to_repeat += 1
                        student_status = "REPEATING"
                    elif student_action == "GRADUATE":
                        total_to_graduate += 1
                        student_status = "GRADUATING"
                    elif student_action == "EXCLUDE":
                        total_excluded += 1
                        student_status = "EXCLUDED"
                    else:
                        student_status = "READY"

                student_previews.append(StudentPromotionPreviewItem(
                    student_id=student.id,
                    admission_number=student.admission_number,
                    student_name=student.full_name,
                    gender=student.gender,
                    education_level=from_info["division"],
                    current_class_id=from_class.id,
                    current_class_name=from_class.name,
                    current_section=from_info["section"],
                    target_class_id=resolved_target_class.id if resolved_target_class else None,
                    target_class_name=resolved_target_class.name if resolved_target_class else None,
                    target_section=resolved_target_class.section if resolved_target_class else None,
                    source_academic_year=source_year,
                    target_academic_year=target_year,
                    action=student_action,
                    status=student_status,
                    is_valid=is_valid,
                    validation_message=validation_msg
                ))

            warning_msg = None
            if class_error_count > 0:
                warning_msg = f"{class_error_count} student(s) have validation conflicts."
            elif not to_class and action == "PROMOTE":
                warning_msg = "Destination class missing."

            class_summaries.append(ClassMappingPreviewSummary(
                from_class_id=from_class.id,
                from_class_name=from_class.name,
                from_class_code=from_class.code,
                education_level=from_info["division"],
                section=from_info["section"],
                to_class_id=to_class.id if to_class else None,
                to_class_name=to_class.name if to_class else None,
                to_class_code=to_class.code if to_class else None,
                action=action,
                students_count=len(enrollments),
                valid_count=class_valid_count,
                error_count=class_error_count,
                warning_message=warning_msg
            ))

        can_execute = (
            total_errors == 0 and
            len(validation_errors) == 0 and
            missing_dest_count == 0 and
            total_affected > 0
        )

        return BulkPromotionPreviewResponse(
            source_academic_year=source_year,
            target_academic_year=target_year,
            education_level=payload.education_level,
            total_students_affected=total_affected,
            total_to_promote=total_to_promote,
            total_to_repeat=total_to_repeat,
            total_to_graduate=total_to_graduate,
            total_excluded=total_excluded,
            total_validation_errors=total_errors + len(validation_errors),
            missing_destination_classes_count=missing_dest_count,
            can_execute=can_execute,
            class_summaries=class_summaries,
            student_previews=student_previews,
            validation_errors=validation_errors
        )

    # --------------------------------------------------------------------------
    # 3. Bulk Promotion (Atomic Transaction)
    # --------------------------------------------------------------------------
    def execute_bulk_promotion(
        self,
        payload: ExecuteBulkPromotionPayload,
        admin_user: User
    ) -> PromotionBatchResponse:
        """
        Execute bulk promotion in ONE atomic database transaction.
        Preserves historical enrollment records and ensures rollbacks on any error.
        """
        source_year = payload.source_academic_year.strip()
        target_year = payload.target_academic_year.strip()
        reason = payload.reason or "Annual Bulk Class Promotion"

        batch_code = self.repo.generate_batch_code(target_year)

        overrides_map: Dict[int, StudentPromotionOverrideItem] = {}
        if payload.student_overrides:
            for ov in payload.student_overrides:
                overrides_map[ov.student_id] = ov

        try:
            # 1. Create Promotion Batch Header
            batch = ClassPromotionBatch(
                batch_code=batch_code,
                source_academic_year=source_year,
                target_academic_year=target_year,
                promotion_type="BULK_PROMOTION",
                status="COMPLETED",
                total_promoted=0,
                total_graduated=0,
                total_skipped=0,
                reason=reason,
                created_by_id=admin_user.id
            )
            self.db.add(batch)
            self.db.flush()

            total_promoted = 0
            total_graduated = 0
            total_skipped = 0

            # Pre-load class dictionary
            class_ids = set()
            for m in payload.mappings:
                class_ids.add(m.from_class_id)
                if m.to_class_id:
                    class_ids.add(m.to_class_id)
            if payload.student_overrides:
                for ov in payload.student_overrides:
                    if ov.target_class_id:
                        class_ids.add(ov.target_class_id)

            classes_map = {
                c.id: c for c in self.db.query(SchoolClass).filter(SchoolClass.id.in_(class_ids)).all()
            }

            for mapping in payload.mappings:
                from_class = classes_map.get(mapping.from_class_id)
                if not from_class:
                    raise ValueError(f"Source class ID {mapping.from_class_id} does not exist.")

                to_class = classes_map.get(mapping.to_class_id) if mapping.to_class_id else None
                action = mapping.action.upper().strip()

                if action == "PROMOTE":
                    if not to_class:
                        raise ValueError(f"Destination class required for '{from_class.name}'.")
                    if from_class.id == to_class.id:
                        raise ValueError(f"Source and Destination class cannot be identical ({from_class.name}).")
                    if to_class.status != "ACTIVE":
                        raise ValueError(f"Destination class '{to_class.name}' is not ACTIVE.")

                # Find source enrollments
                enrollments = (
                    self.db.query(StudentEnrollment)
                    .filter(
                        StudentEnrollment.class_id == from_class.id,
                        self._build_year_filter(source_year),
                        StudentEnrollment.status == "ACTIVE"
                    )
                    .all()
                )
                if not enrollments:
                    enrollments = (
                        self.db.query(StudentEnrollment)
                        .filter(
                            StudentEnrollment.class_id == from_class.id,
                            StudentEnrollment.status == "ACTIVE"
                        )
                        .all()
                    )

                for enr in enrollments:
                    student = enr.student
                    if not student:
                        continue

                    if student.status != "ACTIVE":
                        raise ValueError(
                            f"Student {student.full_name} ({student.admission_number}) is {student.status}."
                        )

                    student_action = action
                    resolved_dest_class = to_class

                    if student.id in overrides_map:
                        ov = overrides_map[student.id]
                        student_action = ov.action.upper().strip()
                        if ov.target_class_id:
                            resolved_dest_class = classes_map.get(ov.target_class_id)
                        elif student_action == "REPEAT":
                            resolved_dest_class = from_class

                    if student_action == "EXCLUDE":
                        rec = ClassPromotionRecord(
                            batch_id=batch.id,
                            student_id=student.id,
                            from_class_id=from_class.id,
                            to_class_id=None,
                            from_enrollment_id=enr.id,
                            to_enrollment_id=None,
                            source_academic_year=source_year,
                            target_academic_year=target_year,
                            action="EXCLUDED",
                            status="COMPLETED",
                            reason=overrides_map.get(student.id, StudentPromotionOverrideItem(student_id=student.id, action="EXCLUDE", reason="Excluded by administrator")).reason or "Excluded"
                        )
                        self.db.add(rec)
                        total_skipped += 1
                        continue

                    # Check duplicate target enrollment
                    if student_action in ["PROMOTE", "REPEAT", "TRANSFER"]:
                        existing = (
                            self.db.query(StudentEnrollment)
                            .filter(
                                StudentEnrollment.student_id == student.id,
                                self._build_year_filter(target_year)
                            )
                            .first()
                        )
                        if existing and (source_year != target_year or existing.id != enr.id):
                            raise ValueError(
                                f"Student {student.full_name} ({student.admission_number}) already enrolled for {target_year}."
                            )

                    if student_action in ["PROMOTE", "TRANSFER"] and resolved_dest_class:
                        if source_year == target_year and existing and existing.id == enr.id:
                            enr.class_id = resolved_dest_class.id
                            new_enr = enr
                        else:
                            # 1. Update source enrollment
                            enr.status = "PROMOTED"

                            # 2. Create new enrollment in target class
                            new_enr = StudentEnrollment(
                                student_id=student.id,
                                class_id=resolved_dest_class.id,
                                academic_year=target_year,
                                roll_number=enr.roll_number,
                                start_date=datetime.now(timezone.utc).date(),
                                status="ACTIVE"
                            )
                            self.db.add(new_enr)
                            self.db.flush()

                        # 3. Create audit record
                        rec = ClassPromotionRecord(
                            batch_id=batch.id,
                            student_id=student.id,
                            from_class_id=from_class.id,
                            to_class_id=resolved_dest_class.id,
                            from_enrollment_id=enr.id,
                            to_enrollment_id=new_enr.id,
                            source_academic_year=source_year,
                            target_academic_year=target_year,
                            action="PROMOTED" if student_action == "PROMOTE" else "TRANSFERRED",
                            status="COMPLETED",
                            reason=reason
                        )
                        self.db.add(rec)
                        total_promoted += 1

                    elif student_action == "REPEAT":
                        # Student repeats current grade level in target year
                        repeat_class = resolved_dest_class or from_class
                        enr.status = "COMPLETED"

                        new_enr = StudentEnrollment(
                            student_id=student.id,
                            class_id=repeat_class.id,
                            academic_year=target_year,
                            roll_number=enr.roll_number,
                            start_date=datetime.now(timezone.utc).date(),
                            status="ACTIVE"
                        )
                        self.db.add(new_enr)
                        self.db.flush()

                        rec = ClassPromotionRecord(
                            batch_id=batch.id,
                            student_id=student.id,
                            from_class_id=from_class.id,
                            to_class_id=repeat_class.id,
                            from_enrollment_id=enr.id,
                            to_enrollment_id=new_enr.id,
                            source_academic_year=source_year,
                            target_academic_year=target_year,
                            action="REPEATED",
                            status="COMPLETED",
                            reason=reason or "Academic Repeat"
                        )
                        self.db.add(rec)
                        total_promoted += 1

                    elif student_action == "GRADUATE":
                        student.status = "GRADUATED"
                        enr.status = "COMPLETED"

                        rec = ClassPromotionRecord(
                            batch_id=batch.id,
                            student_id=student.id,
                            from_class_id=from_class.id,
                            to_class_id=None,
                            from_enrollment_id=enr.id,
                            to_enrollment_id=None,
                            source_academic_year=source_year,
                            target_academic_year=target_year,
                            action="GRADUATED",
                            status="COMPLETED",
                            reason=reason or "Completed final class / Graduated"
                        )
                        self.db.add(rec)
                        total_graduated += 1

                    else:
                        total_skipped += 1

            batch.total_promoted = total_promoted
            batch.total_graduated = total_graduated
            batch.total_skipped = total_skipped

            self.audit_repo.log_event(
                action="BULK_CLASS_PROMOTION_EXECUTED",
                user_id=admin_user.id,
                details={
                    "batch_code": batch_code,
                    "source_year": source_year,
                    "target_year": target_year,
                    "total_promoted": total_promoted,
                    "total_graduated": total_graduated
                }
            )

            self.db.commit()
            self.db.refresh(batch)
            return self.get_batch_details(batch.id)

        except Exception as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Promotion was not completed. No students were changed. Error: {str(exc)}"
            )

    # --------------------------------------------------------------------------
    # 4. Single-Class Level Promotion
    # --------------------------------------------------------------------------
    def execute_class_level_promotion(
        self,
        payload: ClassLevelPromotionPayload,
        admin_user: User
    ) -> PromotionBatchResponse:
        """
        Promote all (or selected) eligible students in a single class to a target class.
        Affects ONLY the selected class; other classes and sections remain completely untouched.
        """
        from_class = self.class_repo.get_by_id(payload.from_class_id)
        if not from_class:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source class not found.")

        to_class = None
        if payload.to_class_id:
            to_class = self.class_repo.get_by_id(payload.to_class_id)
            if not to_class:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Destination class not found.")

        source_year = payload.source_academic_year.strip()
        target_year = payload.target_academic_year.strip()
        reason = payload.reason or f"Single Class Promotion: {from_class.name}"

        batch_code = self.repo.generate_batch_code(target_year)

        try:
            batch = ClassPromotionBatch(
                batch_code=batch_code,
                source_academic_year=source_year,
                target_academic_year=target_year,
                promotion_type="CLASS_LEVEL",
                status="COMPLETED",
                total_promoted=0,
                total_graduated=0,
                total_skipped=0,
                reason=reason,
                created_by_id=admin_user.id
            )
            self.db.add(batch)
            self.db.flush()

            # Query enrollments for from_class
            query = self.db.query(StudentEnrollment).filter(
                StudentEnrollment.class_id == from_class.id,
                self._build_year_filter(source_year),
                StudentEnrollment.status == "ACTIVE"
            )
            if payload.student_ids:
                query = query.filter(StudentEnrollment.student_id.in_(payload.student_ids))

            enrollments = query.all()
            if not enrollments:
                enrollments = self.db.query(StudentEnrollment).filter(
                    StudentEnrollment.class_id == from_class.id,
                    StudentEnrollment.status == "ACTIVE"
                ).all()

            total_promoted = 0
            total_graduated = 0
            total_skipped = 0

            overrides_map = {ov.student_id: ov for ov in (payload.student_overrides or [])}

            for enr in enrollments:
                student = enr.student
                if not student or student.status != "ACTIVE":
                    continue

                student_action = payload.action.upper().strip()
                resolved_dest = to_class

                if student.id in overrides_map:
                    ov = overrides_map[student.id]
                    student_action = ov.action.upper().strip()
                    if ov.target_class_id:
                        resolved_dest = self.class_repo.get_by_id(ov.target_class_id)

                if student_action in ["PROMOTE", "REPEAT", "TRANSFER"] and resolved_dest:
                    # Check duplicate target enrollment
                    existing = (
                        self.db.query(StudentEnrollment)
                        .filter(
                            StudentEnrollment.student_id == student.id,
                            self._build_year_filter(target_year)
                        )
                        .first()
                    )
                    if existing:
                        raise ValueError(f"Student {student.full_name} is already enrolled in {target_year}.")

                    enr.status = "PROMOTED"
                    new_enr = StudentEnrollment(
                        student_id=student.id,
                        class_id=resolved_dest.id,
                        academic_year=target_year,
                        roll_number=enr.roll_number,
                        start_date=datetime.now(timezone.utc).date(),
                        status="ACTIVE"
                    )
                    self.db.add(new_enr)
                    self.db.flush()

                    rec = ClassPromotionRecord(
                        batch_id=batch.id,
                        student_id=student.id,
                        from_class_id=from_class.id,
                        to_class_id=resolved_dest.id,
                        from_enrollment_id=enr.id,
                        to_enrollment_id=new_enr.id,
                        source_academic_year=source_year,
                        target_academic_year=target_year,
                        action=student_action,
                        status="COMPLETED",
                        reason=reason
                    )
                    self.db.add(rec)
                    total_promoted += 1

                elif student_action == "GRADUATE":
                    student.status = "GRADUATED"
                    enr.status = "COMPLETED"

                    rec = ClassPromotionRecord(
                        batch_id=batch.id,
                        student_id=student.id,
                        from_class_id=from_class.id,
                        to_class_id=None,
                        from_enrollment_id=enr.id,
                        to_enrollment_id=None,
                        source_academic_year=source_year,
                        target_academic_year=target_year,
                        action="GRADUATED",
                        status="COMPLETED",
                        reason=reason
                    )
                    self.db.add(rec)
                    total_graduated += 1

                else:
                    total_skipped += 1

            batch.total_promoted = total_promoted
            batch.total_graduated = total_graduated
            batch.total_skipped = total_skipped

            self.audit_repo.log_event(
                action="CLASS_LEVEL_PROMOTION_EXECUTED",
                user_id=admin_user.id,
                details={
                    "batch_code": batch_code,
                    "from_class": from_class.name,
                    "to_class": to_class.name if to_class else "GRADUATION",
                    "promoted": total_promoted
                }
            )

            self.db.commit()
            self.db.refresh(batch)
            return self.get_batch_details(batch.id)

        except Exception as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Single-class promotion failed. Error: {str(exc)}"
            )

    # --------------------------------------------------------------------------
    # 5. Individual Student Promotion
    # --------------------------------------------------------------------------
    def execute_individual_student_promotion(
        self,
        payload: IndividualStudentPromotionPayload,
        admin_user: User
    ) -> PromotionBatchResponse:
        """
        Promote or transition a single student to next academic year.
        Individual promotion must not accidentally promote the student's classmates.
        """
        student = self.student_repo.get_by_id(payload.student_id)
        if not student:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")

        source_year = payload.source_academic_year.strip()
        target_year = payload.target_academic_year.strip()
        action = payload.action.upper().strip()
        reason = payload.reason or "Individual Student Promotion"

        # Explicitly query source enrollment for the source academic year
        source_enr = (
            self.db.query(StudentEnrollment)
            .filter(
                StudentEnrollment.student_id == student.id,
                self._build_year_filter(source_year),
                StudentEnrollment.status == "ACTIVE"
            )
            .first()
        )
        if not source_enr:
            source_enr = student.current_enrollment

        from_class = source_enr.school_class if source_enr else None

        target_class = None
        if action in ["PROMOTE", "TRANSFER", "REPEAT"]:
            if payload.target_class_id:
                target_class = self.class_repo.get_by_id(payload.target_class_id)
                if not target_class:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target class not found.")
            elif action == "REPEAT" and from_class:
                target_class = from_class
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Target class is required.")

        # Check duplicate target enrollment
        if action in ["PROMOTE", "REPEAT", "TRANSFER"]:
            existing = (
                self.db.query(StudentEnrollment)
                .filter(
                    StudentEnrollment.student_id == student.id,
                    self._build_year_filter(target_year)
                )
                .first()
            )
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Student {student.full_name} is already enrolled in year {target_year}."
                )

        batch_code = self.repo.generate_batch_code(target_year)

        try:
            batch = ClassPromotionBatch(
                batch_code=batch_code,
                source_academic_year=source_year,
                target_academic_year=target_year,
                promotion_type="INDIVIDUAL_PROMOTION",
                status="COMPLETED",
                total_promoted=1 if action in ["PROMOTE", "REPEAT", "TRANSFER"] else 0,
                total_graduated=1 if action == "GRADUATE" else 0,
                total_skipped=1 if action == "EXCLUDE" else 0,
                reason=reason,
                created_by_id=admin_user.id
            )
            self.db.add(batch)
            self.db.flush()

            if action in ["PROMOTE", "REPEAT", "TRANSFER"] and target_class:
                if source_enr:
                    source_enr.status = "PROMOTED" if action == "PROMOTE" else "COMPLETED"

                new_enr = StudentEnrollment(
                    student_id=student.id,
                    class_id=target_class.id,
                    academic_year=target_year,
                    roll_number=source_enr.roll_number if source_enr else None,
                    start_date=datetime.now(timezone.utc).date(),
                    status="ACTIVE"
                )
                self.db.add(new_enr)
                self.db.flush()

                rec = ClassPromotionRecord(
                    batch_id=batch.id,
                    student_id=student.id,
                    from_class_id=from_class.id if from_class else None,
                    to_class_id=target_class.id,
                    from_enrollment_id=source_enr.id if source_enr else None,
                    to_enrollment_id=new_enr.id,
                    source_academic_year=source_year,
                    target_academic_year=target_year,
                    action=action,
                    status="COMPLETED",
                    reason=reason
                )
                self.db.add(rec)

            elif action == "GRADUATE":
                if source_enr:
                    source_enr.status = "COMPLETED"
                student.status = "GRADUATED"

                rec = ClassPromotionRecord(
                    batch_id=batch.id,
                    student_id=student.id,
                    from_class_id=from_class.id if from_class else None,
                    to_class_id=None,
                    from_enrollment_id=source_enr.id if source_enr else None,
                    to_enrollment_id=None,
                    source_academic_year=source_year,
                    target_academic_year=target_year,
                    action="GRADUATED",
                    status="COMPLETED",
                    reason=reason
                )
                self.db.add(rec)

            elif action == "EXCLUDE":
                rec = ClassPromotionRecord(
                    batch_id=batch.id,
                    student_id=student.id,
                    from_class_id=from_class.id if from_class else None,
                    to_class_id=None,
                    from_enrollment_id=source_enr.id if source_enr else None,
                    to_enrollment_id=None,
                    source_academic_year=source_year,
                    target_academic_year=target_year,
                    action="EXCLUDED",
                    status="COMPLETED",
                    reason=reason
                )
                self.db.add(rec)

            self.audit_repo.log_event(
                action="INDIVIDUAL_PROMOTION_EXECUTED",
                user_id=admin_user.id,
                details={
                    "batch_code": batch_code,
                    "student_id": student.id,
                    "action": action,
                    "target_class": target_class.name if target_class else None
                }
            )

            self.db.commit()
            self.db.refresh(batch)
            return self.get_batch_details(batch.id)

        except HTTPException:
            self.db.rollback()
            raise
        except Exception as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Individual promotion failed: {str(exc)}"
            )

    # --------------------------------------------------------------------------
    # 6. Search Students for Promotion
    # --------------------------------------------------------------------------
    def search_students_for_promotion(
        self,
        q: Optional[str] = None,
        class_id: Optional[int] = None,
        education_level: Optional[str] = None,
        academic_year: Optional[str] = None,
        limit: int = 50
    ) -> List[StudentSearchForPromotionItem]:
        """
        Search students by name, admission number, class, or education level.
        Suggests the next class with section preservation.
        """
        query = self.db.query(Student).filter(Student.status == "ACTIVE")

        if q:
            term = f"%{q.strip()}%"
            query = query.filter(
                or_(
                    Student.first_name.ilike(term),
                    Student.last_name.ilike(term),
                    Student.middle_name.ilike(term),
                    Student.admission_number.ilike(term)
                )
            )

        students = query.limit(limit * 2).all()
        results: List[StudentSearchForPromotionItem] = []

        all_classes = self.db.query(SchoolClass).filter(SchoolClass.status == "ACTIVE").all()
        classes_parsed = [self._parse_class_info(c) for c in all_classes]

        for s in students:
            curr_enr = s.current_enrollment
            curr_class = curr_enr.school_class if curr_enr else None

            if class_id and (not curr_class or curr_class.id != class_id):
                continue

            info = self._parse_class_info(curr_class) if curr_class else None
            div = info["division"] if info else "PRIMARY"

            if education_level and education_level.upper() in ["PRIMARY", "SECONDARY"]:
                if div != education_level.upper():
                    continue

            # Compute suggested next class
            suggested_id = None
            suggested_name = None
            is_terminal = info["is_terminal"] if info else False

            if info and not is_terminal and info["level_number"]:
                next_lvl = info["level_number"] + 1
                sec = info["section"]
                for cand in classes_parsed:
                    if (
                        cand["division"] == div and
                        cand["level_number"] == next_lvl and
                        (not sec or (cand["section"] or "").upper() == sec.upper())
                    ):
                        suggested_id = cand["class"].id
                        suggested_name = cand["class"].name
                        break

            results.append(StudentSearchForPromotionItem(
                student_id=s.id,
                admission_number=s.admission_number,
                student_name=s.full_name,
                gender=s.gender,
                current_class_id=curr_class.id if curr_class else None,
                current_class_name=curr_class.name if curr_class else "Unassigned",
                current_division=div,
                current_level=info["level_name"] if info else None,
                current_section=info["section"] if info else None,
                current_academic_year=curr_enr.academic_year if curr_enr else academic_year,
                status=s.status,
                suggested_next_class_id=suggested_id,
                suggested_next_class_name=suggested_name,
                is_terminal=is_terminal
            ))

            if len(results) >= limit:
                break

        return results

    # --------------------------------------------------------------------------
    # 7. Existing Individual Class Change (Mid-year transfer)
    # --------------------------------------------------------------------------
    def execute_individual_class_change(
        self,
        student_id: int,
        payload: IndividualClassChangePayload,
        admin_user: User
    ) -> IndividualClassChangeResponse:
        """
        Move student to new class with historical record preservation.
        """
        student = self.student_repo.get_by_id(student_id)
        if not student:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")

        new_class = self.class_repo.get_by_id(payload.new_class_id)
        if not new_class:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Destination class not found.")
        if new_class.status != "ACTIVE":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Target class is not ACTIVE.")

        academic_year = payload.academic_year.strip()
        reason = payload.reason or "Individual Class Change"

        current_enr = student.current_enrollment
        old_class_id = current_enr.class_id if current_enr else None
        old_class_name = current_enr.school_class.name if (current_enr and current_enr.school_class) else None
        old_academic_year = current_enr.academic_year if current_enr else academic_year

        existing_enr = (
            self.db.query(StudentEnrollment)
            .filter(
                StudentEnrollment.student_id == student.id,
                self._build_year_filter(academic_year)
            )
            .first()
        )

        if existing_enr and existing_enr.class_id == new_class.id and existing_enr.status == "ACTIVE":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Student is already actively enrolled in {new_class.name} for {academic_year}."
            )

        batch_code = self.repo.generate_batch_code(academic_year)

        try:
            batch = ClassPromotionBatch(
                batch_code=batch_code,
                source_academic_year=old_academic_year,
                target_academic_year=academic_year,
                promotion_type="INDIVIDUAL_CHANGE",
                status="COMPLETED",
                total_promoted=1,
                reason=reason,
                created_by_id=admin_user.id
            )
            self.db.add(batch)
            self.db.flush()

            if current_enr and current_enr.academic_year != academic_year:
                current_enr.status = "PROMOTED"
                new_enr = StudentEnrollment(
                    student_id=student.id,
                    class_id=new_class.id,
                    academic_year=academic_year,
                    start_date=datetime.now(timezone.utc).date(),
                    status="ACTIVE"
                )
                self.db.add(new_enr)
                self.db.flush()

                rec = ClassPromotionRecord(
                    batch_id=batch.id,
                    student_id=student.id,
                    from_class_id=old_class_id,
                    to_class_id=new_class.id,
                    from_enrollment_id=current_enr.id,
                    to_enrollment_id=new_enr.id,
                    source_academic_year=old_academic_year,
                    target_academic_year=academic_year,
                    action="PROMOTED" if payload.is_promotion else "CLASS_CHANGED",
                    status="COMPLETED",
                    reason=reason
                )
                self.db.add(rec)
                final_enrollment_id = new_enr.id
            else:
                if existing_enr:
                    from_cid = existing_enr.class_id
                    existing_enr.class_id = new_class.id
                    existing_enr.status = "ACTIVE"
                    self.db.flush()

                    rec = ClassPromotionRecord(
                        batch_id=batch.id,
                        student_id=student.id,
                        from_class_id=from_cid,
                        to_class_id=new_class.id,
                        from_enrollment_id=existing_enr.id,
                        to_enrollment_id=existing_enr.id,
                        source_academic_year=academic_year,
                        target_academic_year=academic_year,
                        action="CLASS_CHANGED",
                        status="COMPLETED",
                        reason=reason
                    )
                    self.db.add(rec)
                    final_enrollment_id = existing_enr.id
                else:
                    new_enr = StudentEnrollment(
                        student_id=student.id,
                        class_id=new_class.id,
                        academic_year=academic_year,
                        start_date=datetime.now(timezone.utc).date(),
                        status="ACTIVE"
                    )
                    self.db.add(new_enr)
                    self.db.flush()

                    rec = ClassPromotionRecord(
                        batch_id=batch.id,
                        student_id=student.id,
                        from_class_id=old_class_id,
                        to_class_id=new_class.id,
                        from_enrollment_id=current_enr.id if current_enr else None,
                        to_enrollment_id=new_enr.id,
                        source_academic_year=old_academic_year,
                        target_academic_year=academic_year,
                        action="CLASS_CHANGED",
                        status="COMPLETED",
                        reason=reason
                    )
                    self.db.add(rec)
                    final_enrollment_id = new_enr.id

            if student.status != "ACTIVE":
                student.status = "ACTIVE"

            self.audit_repo.log_event(
                action="STUDENT_CLASS_CHANGED",
                user_id=admin_user.id,
                details={
                    "student_id": student.id,
                    "admission_number": student.admission_number,
                    "old_class": old_class_name,
                    "new_class": new_class.name,
                    "academic_year": academic_year,
                    "reason": reason
                }
            )

            self.db.commit()

            return IndividualClassChangeResponse(
                message=f"Student successfully moved to {new_class.name}.",
                student_id=student.id,
                student_name=student.full_name,
                old_class_name=old_class_name,
                new_class_name=new_class.name,
                academic_year=academic_year,
                enrollment_id=final_enrollment_id,
                batch_code=batch_code,
                timestamp=datetime.now(timezone.utc)
            )

        except HTTPException:
            self.db.rollback()
            raise
        except Exception as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to change student class: {str(exc)}"
            )

    # --------------------------------------------------------------------------
    # 8. Promotion History and Audit
    # --------------------------------------------------------------------------
    def list_batches(
        self,
        academic_year: Optional[str] = None,
        promotion_type: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[PromotionBatchResponse], int]:
        batches, total = self.repo.list_batches(
            academic_year=academic_year,
            promotion_type=promotion_type,
            status=status,
            skip=skip,
            limit=limit
        )
        results = []
        for b in batches:
            creator_name = b.created_by.full_name if b.created_by else "System Admin"
            rec_count = len(b.records)
            results.append(PromotionBatchResponse(
                id=b.id,
                batch_code=b.batch_code,
                source_academic_year=b.source_academic_year,
                target_academic_year=b.target_academic_year,
                promotion_type=b.promotion_type,
                status=b.status,
                total_promoted=b.total_promoted,
                total_graduated=b.total_graduated,
                total_skipped=b.total_skipped,
                reason=b.reason,
                created_by_name=creator_name,
                created_at=b.created_at,
                records_count=rec_count
            ))
        return results, total

    def get_batch_details(self, batch_id: int) -> PromotionBatchResponse:
        b = self.repo.get_batch_by_id(batch_id)
        if not b:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Promotion batch not found.")

        records = (
            self.db.query(ClassPromotionRecord)
            .filter(ClassPromotionRecord.batch_id == b.id)
            .order_by(ClassPromotionRecord.id.asc())
            .all()
        )

        record_items = []
        for r in records:
            record_items.append(PromotionRecordItemResponse(
                id=r.id,
                batch_id=r.batch_id,
                student_id=r.student_id,
                student_name=r.student.full_name if r.student else "Student",
                admission_number=r.student.admission_number if r.student else "—",
                from_class_name=r.from_class.name if r.from_class else "—",
                to_class_name=r.to_class.name if r.to_class else "—",
                source_academic_year=r.source_academic_year,
                target_academic_year=r.target_academic_year,
                action=r.action,
                status=r.status,
                reason=r.reason,
                created_at=r.created_at
            ))

        creator_name = b.created_by.full_name if b.created_by else "System Admin"
        return PromotionBatchResponse(
            id=b.id,
            batch_code=b.batch_code,
            source_academic_year=b.source_academic_year,
            target_academic_year=b.target_academic_year,
            promotion_type=b.promotion_type,
            status=b.status,
            total_promoted=b.total_promoted,
            total_graduated=b.total_graduated,
            total_skipped=b.total_skipped,
            reason=b.reason,
            created_by_name=creator_name,
            created_at=b.created_at,
            records_count=len(record_items),
            records=record_items
        )

    # --------------------------------------------------------------------------
    # 9. Safe Batch Rollback
    # --------------------------------------------------------------------------
    def rollback_batch(self, batch_id: int, admin_user: User) -> BatchRollbackResponse:
        """
        Safely roll back a promotion batch by ID.
        Restores records created by this batch and reactivates historical enrollments.
        """
        batch = self.repo.get_batch_by_id(batch_id)
        if not batch:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Promotion batch not found.")

        if batch.status == "ROLLED_BACK":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Batch '{batch.batch_code}' has already been rolled back."
            )

        try:
            records = (
                self.db.query(ClassPromotionRecord)
                .filter(ClassPromotionRecord.batch_id == batch.id)
                .all()
            )

            restored_count = 0

            for rec in records:
                # 1. Delete destination enrollment created by this batch
                if rec.to_enrollment_id:
                    to_enr = (
                        self.db.query(StudentEnrollment)
                        .filter(StudentEnrollment.id == rec.to_enrollment_id)
                        .first()
                    )
                    if to_enr:
                        self.db.delete(to_enr)

                # 2. Restore source enrollment to ACTIVE
                if rec.from_enrollment_id:
                    from_enr = (
                        self.db.query(StudentEnrollment)
                        .filter(StudentEnrollment.id == rec.from_enrollment_id)
                        .first()
                    )
                    if from_enr:
                        from_enr.status = "ACTIVE"

                # 3. If graduated, restore student status to ACTIVE
                if rec.action == "GRADUATED":
                    student = self.student_repo.get_by_id(rec.student_id)
                    if student and student.status == "GRADUATED":
                        student.status = "ACTIVE"

                rec.status = "ROLLED_BACK"
                restored_count += 1

            batch.status = "ROLLED_BACK"

            self.audit_repo.log_event(
                action="PROMOTION_BATCH_ROLLED_BACK",
                user_id=admin_user.id,
                details={
                    "batch_code": batch.batch_code,
                    "batch_id": batch.id,
                    "restored_count": restored_count
                }
            )

            self.db.commit()

            return BatchRollbackResponse(
                success=True,
                message=f"Batch {batch.batch_code} successfully rolled back. {restored_count} student records restored.",
                batch_code=batch.batch_code,
                restored_students_count=restored_count
            )

        except Exception as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Rollback failed: {str(exc)}"
            )
