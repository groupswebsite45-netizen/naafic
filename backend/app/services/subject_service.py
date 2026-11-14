from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.subject import Subject
from app.models.school_class import SchoolClass
from app.models.teacher import Teacher
from app.models.teacher_assignment import TeacherAssignment
from app.repositories.subject_repo import SubjectRepository
from app.repositories.audit_repo import AuditLogRepository
from app.schemas.subject import (
    SubjectCreate,
    SubjectUpdate,
    SubjectResponse,
    SubjectSummary,
    SubjectFullProfileResponse,
    SubjectClassAssignmentItem,
    SubjectTeacherAssignmentItem,
    SubjectAssignClassPayload,
    SubjectAssignTeacherPayload
)


class SubjectService:
    """Service handling Subject operations, curriculum associations, and class/teacher assignments."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = SubjectRepository(db)
        self.audit_repo = AuditLogRepository(db)

    def get_summary(self) -> SubjectSummary:
        return self.repo.get_summary()

    def get_departments(self) -> List[str]:
        return self.repo.get_distinct_departments()

    def get_subject(self, subject_id: int) -> Subject:
        s = self.repo.get_by_id(subject_id)
        if not s:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Subject with ID {subject_id} not found.")
        return s

    def get_full_profile(self, subject_id: int) -> SubjectFullProfileResponse:
        s = self.get_subject(subject_id)
        classes = self.repo.get_subject_classes(subject_id)
        teachers = self.repo.get_subject_teachers(subject_id)
        timetables = self.repo.get_subject_timetables(subject_id)
        exams = self.repo.get_subject_exams(subject_id)

        return SubjectFullProfileResponse(
            id=s.id,
            name=s.name,
            code=s.code,
            department=s.department,
            description=s.description,
            status=s.status,
            created_at=s.created_at,
            updated_at=s.updated_at,
            classes_count=len(set(c.class_id for c in classes)),
            teachers_count=len(set(t.teacher_id for t in teachers)),
            timetables_count=len(timetables),
            exams_count=len(exams),
            classes=classes,
            teachers=teachers,
            timetables=timetables,
            exams=exams
        )

    def list_subjects(
        self,
        query: Optional[str] = None,
        division: Optional[str] = None,
        level: Optional[str] = None,
        class_id: Optional[int] = None,
        department: Optional[str] = None,
        status_filter: Optional[str] = None,
        assigned_filter: Optional[str] = None,
        academic_year: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[SubjectResponse], int]:
        subjects, total = self.repo.search_subjects(
            query=query,
            division=division,
            level=level,
            class_id=class_id,
            department=department,
            status=status_filter,
            assigned_filter=assigned_filter,
            academic_year=academic_year,
            skip=skip,
            limit=limit
        )

        response_items = []
        for s in subjects:
            response_items.append(SubjectResponse(
                id=s.id,
                name=s.name,
                code=s.code,
                division=s.division or "ALL",
                applicable_levels=s.applicable_levels,
                department=s.department,
                description=s.description,
                status=s.status,
                created_at=s.created_at,
                updated_at=s.updated_at,
                classes_count=getattr(s, "classes_count", 0),
                teachers_count=getattr(s, "teachers_count", 0),
                timetables_count=getattr(s, "timetables_count", 0),
                exams_count=getattr(s, "exams_count", 0)
            ))
        return response_items, total

    def create_subject(self, data: SubjectCreate, user_id: Optional[int] = None) -> Subject:
        code_upper = data.code.upper().strip()
        existing = self.repo.get_by_code(code_upper)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Subject code '{code_upper}' is already registered.")

        new_subject = Subject(
            name=data.name.strip(),
            code=code_upper,
            division=(data.division or "ALL").upper().strip(),
            applicable_levels=data.applicable_levels.strip() if data.applicable_levels and data.applicable_levels.strip() else None,
            department=data.department.strip() if data.department and data.department.strip() else None,
            description=data.description.strip() if data.description and data.description.strip() else None,
            status=data.status.upper().strip() if data.status else "ACTIVE"
        )
        created = self.repo.create(new_subject)
        self.audit_repo.log_event(
            action="SUBJECT_CREATED",
            user_id=user_id,
            details={"subject_id": created.id, "name": created.name, "code": created.code, "division": created.division}
        )
        return created

    def update_subject(self, subject_id: int, data: SubjectUpdate, user_id: Optional[int] = None) -> Subject:
        s = self.get_subject(subject_id)

        if data.code is not None and data.code.strip():
            code_upper = data.code.upper().strip()
            if code_upper != s.code:
                existing = self.repo.get_by_code(code_upper)
                if existing and existing.id != subject_id:
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Subject code '{code_upper}' is already in use.")
                s.code = code_upper

        if data.name is not None:
            s.name = data.name.strip()
        if data.division is not None:
            s.division = data.division.upper().strip()
        if data.applicable_levels is not None:
            s.applicable_levels = data.applicable_levels.strip() if data.applicable_levels.strip() else None
        if data.department is not None:
            s.department = data.department.strip() if data.department.strip() else None
        if data.description is not None:
            s.description = data.description.strip() if data.description.strip() else None
        if data.status is not None:
            s.status = data.status.upper().strip()

        updated = self.repo.update(s)
        self.audit_repo.log_event(
            action="SUBJECT_UPDATED",
            user_id=user_id,
            details={"subject_id": updated.id, "name": updated.name, "division": updated.division}
        )
        return updated

    def update_status(self, subject_id: int, new_status: str, reason: Optional[str] = None, user_id: Optional[int] = None) -> Subject:
        s = self.get_subject(subject_id)
        allowed_statuses = ["ACTIVE", "INACTIVE", "ARCHIVED"]
        status_clean = new_status.upper().strip()
        if status_clean not in allowed_statuses:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid status '{new_status}'. Allowed: {allowed_statuses}")

        s.status = status_clean
        updated = self.repo.update(s)
        self.audit_repo.log_event(
            action="SUBJECT_STATUS_CHANGED",
            user_id=user_id,
            details={"subject_id": s.id, "status": status_clean, "reason": reason}
        )
        return updated

    def delete_subject(self, subject_id: int, user_id: Optional[int] = None) -> None:
        s = self.get_subject(subject_id)
        s.status = "INACTIVE"
        self.repo.update(s)
        self.audit_repo.log_event(
            action="SUBJECT_DEACTIVATED",
            user_id=user_id,
            details={"subject_id": subject_id, "name": s.name}
        )

    def _validate_subject_class_compatibility(self, subject: Subject, school_class: SchoolClass) -> None:
        # Division validation
        if subject.division and subject.division.upper() != "ALL":
            if subject.division.upper() != (school_class.division or "PRIMARY").upper():
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Subject '{subject.name}' ({subject.division}) cannot be assigned to {school_class.division} class '{school_class.name}'."
                )

        # Level validation
        if subject.applicable_levels and subject.applicable_levels.strip():
            allowed_levels = [lvl.strip().lower() for lvl in subject.applicable_levels.split(",") if lvl.strip()]
            class_lvl = (school_class.level or school_class.name).strip().lower()
            if class_lvl not in allowed_levels and school_class.name.strip().lower() not in allowed_levels:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Subject '{subject.name}' is only configured for levels ({subject.applicable_levels}), not for '{school_class.name}'."
                )

    def assign_to_class(
        self,
        subject_id: int,
        data: SubjectAssignClassPayload,
        user_id: Optional[int] = None
    ) -> TeacherAssignment:
        subject = self.get_subject(subject_id)

        # Validate class exists
        school_class = self.db.query(SchoolClass).filter(SchoolClass.id == data.class_id).first()
        if not school_class:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Class with ID {data.class_id} not found.")

        # Check curriculum compatibility
        self._validate_subject_class_compatibility(subject, school_class)

        # If teacher_id provided, validate teacher exists
        teacher: Optional[Teacher] = None
        if data.teacher_id:
            teacher = self.db.query(Teacher).filter(Teacher.id == data.teacher_id).first()
            if not teacher:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Teacher with ID {data.teacher_id} not found.")

        # Check duplicate
        year_str = data.academic_year.strip()
        year_variants = {year_str, year_str.replace('/', '-'), year_str.replace('-', '/')}
        existing = self.db.query(TeacherAssignment).filter(
            TeacherAssignment.subject_id == subject_id,
            TeacherAssignment.class_id == data.class_id,
            TeacherAssignment.academic_year.in_(year_variants),
            TeacherAssignment.status == "ACTIVE"
        ).first()

        if existing:
            if data.teacher_id and existing.teacher_id != data.teacher_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="This subject is already assigned to another teacher in this class."
                )
            return existing

        # If no teacher specified, assign to the first available active teacher or create assignment
        target_teacher_id = data.teacher_id
        if not target_teacher_id:
            first_teacher = self.db.query(Teacher).filter(Teacher.status == "ACTIVE").first()
            if first_teacher:
                target_teacher_id = first_teacher.id
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active teachers available to allocate for this subject.")

        assignment = TeacherAssignment(
            teacher_id=target_teacher_id,
            class_id=data.class_id,
            subject_id=subject_id,
            academic_year=year_str,
            status="ACTIVE"
        )
        try:
            self.db.add(assignment)
            self.db.commit()
            self.db.refresh(assignment)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This subject is already assigned to another teacher in this class."
            )

        self.audit_repo.log_event(
            action="SUBJECT_ASSIGNED_TO_CLASS",
            user_id=user_id,
            details={"subject_id": subject_id, "class_id": data.class_id, "academic_year": data.academic_year}
        )
        return assignment

    def remove_class_assignment(self, subject_id: int, assignment_id: int, user_id: Optional[int] = None) -> None:
        assignment = (
            self.db.query(TeacherAssignment)
            .filter(
                TeacherAssignment.id == assignment_id,
                TeacherAssignment.subject_id == subject_id
            )
            .first()
        )
        if not assignment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found for this subject.")

        self.db.delete(assignment)
        self.db.commit()

        self.audit_repo.log_event(
            action="SUBJECT_CLASS_ASSIGNMENT_REMOVED",
            user_id=user_id,
            details={"subject_id": subject_id, "assignment_id": assignment_id}
        )

    def assign_teacher(
        self,
        subject_id: int,
        data: SubjectAssignTeacherPayload,
        user_id: Optional[int] = None
    ) -> TeacherAssignment:
        subject = self.get_subject(subject_id)

        teacher = self.db.query(Teacher).filter(Teacher.id == data.teacher_id).first()
        if not teacher:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Teacher with ID {data.teacher_id} not found.")

        school_class = self.db.query(SchoolClass).filter(SchoolClass.id == data.class_id).first()
        if not school_class:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Class with ID {data.class_id} not found.")

        # Check curriculum compatibility
        self._validate_subject_class_compatibility(subject, school_class)

        # Check duplicate
        year_str = data.academic_year.strip()
        year_variants = {year_str, year_str.replace('/', '-'), year_str.replace('-', '/')}
        existing = (
            self.db.query(TeacherAssignment)
            .filter(
                TeacherAssignment.subject_id == subject_id,
                TeacherAssignment.class_id == data.class_id,
                TeacherAssignment.academic_year.in_(year_variants),
                TeacherAssignment.status == "ACTIVE"
            )
            .first()
        )
        if existing:
            if existing.teacher_id != data.teacher_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="This subject is already assigned to another teacher in this class."
                )
            return existing

        assignment = TeacherAssignment(
            teacher_id=data.teacher_id,
            class_id=data.class_id,
            subject_id=subject_id,
            academic_year=year_str,
            status="ACTIVE"
        )
        try:
            self.db.add(assignment)
            self.db.commit()
            self.db.refresh(assignment)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This subject is already assigned to another teacher in this class."
            )

        self.audit_repo.log_event(
            action="SUBJECT_TEACHER_ASSIGNED",
            user_id=user_id,
            details={"subject_id": subject_id, "teacher_id": data.teacher_id, "class_id": data.class_id}
        )
        return assignment

    def remove_teacher_assignment(self, subject_id: int, assignment_id: int, user_id: Optional[int] = None) -> None:
        assignment = (
            self.db.query(TeacherAssignment)
            .filter(
                TeacherAssignment.id == assignment_id,
                TeacherAssignment.subject_id == subject_id
            )
            .first()
        )
        if not assignment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher assignment not found for this subject.")

        self.db.delete(assignment)
        self.db.commit()

        self.audit_repo.log_event(
            action="SUBJECT_TEACHER_ASSIGNMENT_REMOVED",
            user_id=user_id,
            details={"subject_id": subject_id, "assignment_id": assignment_id}
        )

    def update_teacher_assignment(
        self,
        subject_id: int,
        assignment_id: int,
        teacher_id: int,
        class_id: int,
        academic_year: str,
        user_id: Optional[int] = None
    ) -> TeacherAssignment:
        assignment = (
            self.db.query(TeacherAssignment)
            .filter(
                TeacherAssignment.id == assignment_id,
                TeacherAssignment.subject_id == subject_id
            )
            .first()
        )
        if not assignment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher assignment not found for this subject.")

        year_str = academic_year.strip()
        year_variants = {year_str, year_str.replace('/', '-'), year_str.replace('-', '/')}

        existing = (
            self.db.query(TeacherAssignment)
            .filter(
                TeacherAssignment.subject_id == subject_id,
                TeacherAssignment.class_id == class_id,
                TeacherAssignment.academic_year.in_(year_variants),
                TeacherAssignment.status == "ACTIVE",
                TeacherAssignment.id != assignment_id
            )
            .first()
        )
        if existing:
            if existing.teacher_id != teacher_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="This subject is already assigned to another teacher in this class."
                )

        assignment.teacher_id = teacher_id
        assignment.class_id = class_id
        assignment.academic_year = year_str
        try:
            self.db.commit()
            self.db.refresh(assignment)
            return assignment
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This subject is already assigned to another teacher in this class."
            )
