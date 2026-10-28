from typing import Optional, List, Tuple
from datetime import date
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.school_class import SchoolClass
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.models.teacher import Teacher
from app.models.teacher_assignment import TeacherAssignment
from app.models.subject import Subject
from app.repositories.class_repo import ClassRepository
from app.repositories.audit_repo import AuditLogRepository
from app.schemas.school_class import (
    SchoolClassCreate,
    SchoolClassUpdate,
    SchoolClassResponse,
    ClassSummary,
    ClassFullProfileResponse,
    ClassEnrollmentStudent,
    ClassTeacherAssignmentItem
)


class ClassService:
    """Service handling SchoolClass operations, capacity management, and student/teacher assignments."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = ClassRepository(db)
        self.audit_repo = AuditLogRepository(db)

    def get_summary(self) -> ClassSummary:
        return self.repo.get_summary()

    def get_class(self, class_id: int) -> SchoolClass:
        c = self.repo.get_by_id(class_id)
        if not c:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Class with ID {class_id} not found.")
        return c

    def get_full_profile(self, class_id: int) -> ClassFullProfileResponse:
        c = self.get_class(class_id)
        capacity_metrics = self.repo.get_class_capacity_metrics(c)
        students = self.repo.get_class_students(class_id)
        teachers = self.repo.get_class_teachers(class_id)
        subjects = self.repo.get_class_subjects(class_id)
        timetables = self.repo.get_class_timetables(class_id)
        exams = self.repo.get_class_exams(class_id)

        # Build response
        return ClassFullProfileResponse(
            id=c.id,
            name=c.name,
            code=c.code,
            section=c.section,
            academic_year=c.academic_year,
            capacity=c.capacity,
            description=c.description,
            status=c.status,
            created_at=c.created_at,
            updated_at=c.updated_at,
            students_count=capacity_metrics.enrolled,
            teachers_count=len(set(t.teacher_id for t in teachers)),
            subjects_count=len(subjects),
            available_seats=capacity_metrics.available_seats,
            utilization_rate=capacity_metrics.utilization_rate,
            capacity_status=capacity_metrics.capacity_status,
            capacity_metrics=capacity_metrics,
            students=students,
            teachers=teachers,
            subjects=subjects,
            timetables=timetables,
            exams=exams
        )

    VALID_PRIMARY_LEVELS = [f"Grade {i}" for i in range(1, 9)]
    VALID_SECONDARY_LEVELS = [f"Form {i}" for i in range(1, 5)]

    def _validate_division_level(self, division: str, level: str) -> Tuple[str, str]:
        div_upper = division.upper().strip()
        lvl_clean = level.strip()

        if div_upper not in ["PRIMARY", "SECONDARY"]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid academic division '{division}'. Must be 'PRIMARY' or 'SECONDARY'."
            )

        if div_upper == "PRIMARY":
            # Match Grade 1..8
            if lvl_clean not in self.VALID_PRIMARY_LEVELS:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Invalid level '{level}' for PRIMARY division. Allowed levels: {', '.join(self.VALID_PRIMARY_LEVELS)}."
                )
        elif div_upper == "SECONDARY":
            # Match Form 1..4
            if lvl_clean not in self.VALID_SECONDARY_LEVELS:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Invalid level '{level}' for SECONDARY division. Allowed levels: {', '.join(self.VALID_SECONDARY_LEVELS)}."
                )

        return div_upper, lvl_clean

    def get_active_classes_with_students(
        self,
        academic_year: Optional[str] = None,
        division: Optional[str] = None
    ) -> List[SchoolClassResponse]:
        """
        CENTRAL BUSINESS RULE: Returns only ACTIVE classes with >= 1 active student.
        Use this method for all class selectors/dropdowns throughout the system.
        """
        classes = self.repo.get_active_classes_with_students(
            academic_year=academic_year,
            division=division
        )
        response_items = []
        for c in classes:
            response_items.append(SchoolClassResponse(
                id=c.id,
                name=c.name,
                code=c.code,
                division=c.division or "PRIMARY",
                level=c.level or c.name,
                section=c.section,
                academic_year=c.academic_year,
                capacity=c.capacity,
                description=c.description,
                status=c.status,
                created_at=c.created_at,
                updated_at=c.updated_at,
                students_count=getattr(c, "students_count", 0),
                teachers_count=getattr(c, "teachers_count", 0),
                subjects_count=getattr(c, "subjects_count", 0),
                available_seats=getattr(c, "available_seats", 0),
                utilization_rate=getattr(c, "utilization_rate", 0.0),
                capacity_status=getattr(c, "capacity_status", "NORMAL")
            ))
        return response_items

    def list_classes(
        self,
        query: Optional[str] = None,
        academic_year: Optional[str] = None,
        division: Optional[str] = None,
        status_filter: Optional[str] = None,
        level: Optional[str] = None,
        section: Optional[str] = None,
        capacity_filter: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[SchoolClassResponse], int]:
        classes, total = self.repo.search_classes(
            query=query,
            academic_year=academic_year,
            division=division,
            status=status_filter,
            level=level,
            section=section,
            capacity_filter=capacity_filter,
            skip=skip,
            limit=limit
        )

        response_items = []
        for c in classes:
            response_items.append(SchoolClassResponse(
                id=c.id,
                name=c.name,
                code=c.code,
                division=c.division or "PRIMARY",
                level=c.level or c.name,
                section=c.section,
                academic_year=c.academic_year,
                capacity=c.capacity,
                description=c.description,
                status=c.status,
                created_at=c.created_at,
                updated_at=c.updated_at,
                students_count=getattr(c, "students_count", 0),
                teachers_count=getattr(c, "teachers_count", 0),
                subjects_count=getattr(c, "subjects_count", 0),
                available_seats=getattr(c, "available_seats", 0),
                utilization_rate=getattr(c, "utilization_rate", 0.0),
                capacity_status=getattr(c, "capacity_status", "NORMAL")
            ))
        return response_items, total

    def create_class(self, data: SchoolClassCreate, user_id: Optional[int] = None) -> SchoolClass:
        div_clean, lvl_clean = self._validate_division_level(data.division, data.level)
        sec_clean = data.section.strip().upper() if data.section and data.section.strip() else None
        year_clean = data.academic_year.strip()

        # Generate canonical name
        canonical_name = f"{lvl_clean} - {sec_clean}" if sec_clean else lvl_clean
        name_clean = data.name.strip() if data.name and data.name.strip() else canonical_name

        # Check duplicate by academic identity (academic_year + division + level + section)
        existing_identity = self.repo.get_by_identity(
            academic_year=year_clean,
            division=div_clean,
            level=lvl_clean,
            section=sec_clean
        )
        if existing_identity:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This class already exists for the selected academic year."
            )

        # Check duplicate by name + section + academic year
        existing_name = self.repo.get_by_name_section_year(name_clean, sec_clean, year_clean)
        if existing_name:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This class already exists for the selected academic year."
            )

        # Auto-generate code if missing
        if data.code and data.code.strip():
            code_clean = data.code.upper().strip()
        else:
            prefix = lvl_clean.replace("Grade ", "G").replace("Form ", "F").replace(" ", "")
            sec_part = sec_clean if sec_clean else "GEN"
            yr_part = year_clean.split("/")[0].split("-")[0]
            code_clean = f"{prefix}-{sec_part}-{yr_part}"

        # If code conflicts, make unique with random suffix
        if self.repo.get_by_code(code_clean):
            import random
            code_clean = f"{code_clean}-{random.randint(100, 999)}"

        new_class = SchoolClass(
            name=canonical_name,
            code=code_clean,
            division=div_clean,
            level=lvl_clean,
            section=sec_clean,
            academic_year=year_clean,
            capacity=data.capacity,
            description=data.description.strip() if data.description else None,
            status=data.status.upper().strip() if data.status else "ACTIVE"
        )
        created = self.repo.create(new_class)
        self.audit_repo.log_event(
            action="CLASS_CREATED",
            user_id=user_id,
            details={
                "class_id": created.id,
                "name": created.name,
                "code": created.code,
                "division": created.division,
                "level": created.level,
                "section": created.section
            }
        )
        return created

    def update_class(self, class_id: int, data: SchoolClassUpdate, user_id: Optional[int] = None) -> SchoolClass:
        c = self.get_class(class_id)

        div_to_check = (data.division.upper().strip() if data.division is not None else c.division) or "PRIMARY"
        lvl_to_check = (data.level.strip() if data.level is not None else c.level) or c.name
        sec_to_check = data.section.strip().upper() if data.section is not None and data.section.strip() else (c.section if data.section is None else None)
        year_to_check = data.academic_year.strip() if data.academic_year is not None else c.academic_year

        div_clean, lvl_clean = self._validate_division_level(div_to_check, lvl_to_check)

        # Check duplicate identity
        dup_identity = self.repo.get_by_identity(
            academic_year=year_to_check,
            division=div_clean,
            level=lvl_clean,
            section=sec_to_check,
            exclude_id=class_id
        )
        if dup_identity:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This class already exists for the selected academic year."
            )

        if data.code is not None and data.code.strip():
            code_clean = data.code.upper().strip()
            if code_clean != c.code:
                existing = self.repo.get_by_code(code_clean)
                if existing and existing.id != class_id:
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Class code '{code_clean}' is already in use.")
                c.code = code_clean

        c.division = div_clean
        c.level = lvl_clean
        c.section = sec_to_check
        c.name = f"{lvl_clean} - {sec_to_check}" if sec_to_check else lvl_clean
        c.academic_year = year_to_check

        if data.capacity is not None:
            c.capacity = data.capacity
        if data.description is not None:
            c.description = data.description.strip() if data.description.strip() else None
        if data.status is not None:
            c.status = data.status.upper().strip()

        updated = self.repo.update(c)
        self.audit_repo.log_event(
            action="CLASS_UPDATED",
            user_id=user_id,
            details={"class_id": updated.id, "name": updated.name, "division": updated.division}
        )
        return updated

    def update_status(self, class_id: int, new_status: str, reason: Optional[str] = None, user_id: Optional[int] = None) -> SchoolClass:
        c = self.get_class(class_id)
        allowed_statuses = ["ACTIVE", "INACTIVE", "ARCHIVED"]
        status_clean = new_status.upper().strip()
        if status_clean not in allowed_statuses:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid status '{new_status}'. Allowed: {allowed_statuses}")

        c.status = status_clean
        updated = self.repo.update(c)
        self.audit_repo.log_event(
            action="CLASS_STATUS_CHANGED",
            user_id=user_id,
            details={"class_id": c.id, "status": status_clean, "reason": reason}
        )
        return updated

    def delete_class(self, class_id: int, user_id: Optional[int] = None) -> None:
        c = self.get_class(class_id)
        c.status = "INACTIVE"
        self.repo.update(c)
        self.audit_repo.log_event(
            action="CLASS_DEACTIVATED",
            user_id=user_id,
            details={"class_id": class_id, "name": c.name}
        )

    def enroll_student(
        self,
        class_id: int,
        student_id: int,
        academic_year: str,
        enrollment_date: Optional[date] = None,
        user_id: Optional[int] = None
    ) -> StudentEnrollment:
        school_class = self.get_class(class_id)

        # Check student exists
        student = self.db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Student with ID {student_id} not found.")

        # Check existing active enrollment for same student and academic year
        existing = (
            self.db.query(StudentEnrollment)
            .filter(
                StudentEnrollment.student_id == student_id,
                StudentEnrollment.academic_year == academic_year.strip(),
                StudentEnrollment.status == "ACTIVE"
            )
            .first()
        )
        if existing:
            if existing.class_id == class_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Student {student.full_name} is already actively enrolled in this class ({school_class.name})."
                )
            else:
                other_class = self.db.query(SchoolClass).filter(SchoolClass.id == existing.class_id).first()
                other_name = other_class.name if other_class else f"Class #{existing.class_id}"
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Student {student.full_name} is already enrolled in '{other_name}' for academic year {academic_year}."
                )

        # Capacity check
        current_enrolled = (
            self.db.query(StudentEnrollment)
            .filter(
                StudentEnrollment.class_id == class_id,
                StudentEnrollment.status == "ACTIVE"
            )
            .count()
        )
        if current_enrolled >= school_class.capacity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Class {school_class.name} has reached maximum capacity ({school_class.capacity} students)."
            )

        enrollment = StudentEnrollment(
            student_id=student_id,
            class_id=class_id,
            academic_year=academic_year.strip(),
            start_date=enrollment_date or date.today(),
            status="ACTIVE"
        )
        self.db.add(enrollment)
        self.db.commit()
        self.db.refresh(enrollment)

        self.audit_repo.log_event(
            action="STUDENT_ENROLLED_IN_CLASS",
            user_id=user_id,
            details={"class_id": class_id, "student_id": student_id, "academic_year": academic_year}
        )
        return enrollment

    def remove_student_enrollment(self, class_id: int, student_id: int, user_id: Optional[int] = None) -> None:
        enrollment = (
            self.db.query(StudentEnrollment)
            .filter(
                StudentEnrollment.class_id == class_id,
                StudentEnrollment.student_id == student_id,
                StudentEnrollment.status == "ACTIVE"
            )
            .first()
        )
        if not enrollment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active enrollment not found for this student in this class.")

        enrollment.status = "TRANSFERRED"
        enrollment.end_date = date.today()
        self.db.commit()

        self.audit_repo.log_event(
            action="STUDENT_REMOVED_FROM_CLASS",
            user_id=user_id,
            details={"class_id": class_id, "student_id": student_id}
        )

    def assign_teacher_subject(
        self,
        class_id: int,
        teacher_id: int,
        subject_id: int,
        academic_year: str,
        user_id: Optional[int] = None
    ) -> TeacherAssignment:
        school_class = self.get_class(class_id)

        teacher = self.db.query(Teacher).filter(Teacher.id == teacher_id).first()
        if not teacher:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Teacher with ID {teacher_id} not found.")

        subject = self.db.query(Subject).filter(Subject.id == subject_id).first()
        if not subject:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Subject with ID {subject_id} not found.")

        # Validate curriculum isolation: Division & Applicable Levels
        if subject.division and subject.division.upper() != "ALL":
            if subject.division.upper() != (school_class.division or "PRIMARY").upper():
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Subject '{subject.name}' ({subject.division}) cannot be assigned to {school_class.division} class '{school_class.name}'."
                )

        if subject.applicable_levels and subject.applicable_levels.strip():
            allowed_levels = [lvl.strip().lower() for lvl in subject.applicable_levels.split(",") if lvl.strip()]
            class_lvl = (school_class.level or school_class.name).strip().lower()
            if class_lvl not in allowed_levels and school_class.name.strip().lower() not in allowed_levels:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Subject '{subject.name}' is only configured for levels ({subject.applicable_levels}), not for '{school_class.name}'."
                )

        # Check duplicate
        existing = (
            self.db.query(TeacherAssignment)
            .filter(
                TeacherAssignment.class_id == class_id,
                TeacherAssignment.teacher_id == teacher_id,
                TeacherAssignment.subject_id == subject_id,
                TeacherAssignment.academic_year == academic_year.strip(),
                TeacherAssignment.status == "ACTIVE"
            )
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Teacher {teacher.full_name} is already assigned to {subject.name} for {school_class.name} ({academic_year})."
            )

        assignment = TeacherAssignment(
            teacher_id=teacher_id,
            class_id=class_id,
            subject_id=subject_id,
            academic_year=academic_year.strip(),
            status="ACTIVE"
        )
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)

        self.audit_repo.log_event(
            action="TEACHER_ASSIGNED_TO_CLASS",
            user_id=user_id,
            details={"class_id": class_id, "teacher_id": teacher_id, "subject_id": subject_id}
        )
        return assignment

    def remove_teacher_assignment(self, class_id: int, assignment_id: int, user_id: Optional[int] = None) -> None:
        assignment = (
            self.db.query(TeacherAssignment)
            .filter(
                TeacherAssignment.id == assignment_id,
                TeacherAssignment.class_id == class_id
            )
            .first()
        )
        if not assignment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher assignment not found for this class.")

        self.db.delete(assignment)
        self.db.commit()

        self.audit_repo.log_event(
            action="TEACHER_REMOVED_FROM_CLASS",
            user_id=user_id,
            details={"class_id": class_id, "assignment_id": assignment_id}
        )
