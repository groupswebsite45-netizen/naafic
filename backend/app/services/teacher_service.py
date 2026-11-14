from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.teacher import Teacher
from app.models.teacher_assignment import TeacherAssignment
from app.models.school_class import SchoolClass
from app.models.subject import Subject
from app.models.user import User
from app.core.security import get_password_hash
from app.repositories.teacher_repo import TeacherRepository
from app.repositories.user_repo import UserRepository
from app.repositories.role_repo import RoleRepository
from app.repositories.audit_repo import AuditLogRepository
from app.schemas.teacher import (
    TeacherCreate,
    TeacherUpdate,
    TeacherAssignmentCreate,
    TeacherAssignmentUpdate,
    TeacherBulkAssignmentItem,
    TeacherSummary,
    TeacherFullProfile,
    TeacherTimetableSlot
)


class TeacherService:
    """Service handling Teacher operations, assignments, and portal account creation."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = TeacherRepository(db)
        self.user_repo = UserRepository(db)
        self.role_repo = RoleRepository(db)
        self.audit_repo = AuditLogRepository(db)

    def get_teacher(self, teacher_id: int) -> Teacher:
        t = self.repo.get_by_id(teacher_id)
        if not t:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found.")
        t.has_portal_access = t.user_id is not None
        return t

    def get_summary(self) -> TeacherSummary:
        return self.repo.get_summary()

    def get_full_profile(self, teacher_id: int) -> TeacherFullProfile:
        teacher = self.get_teacher(teacher_id)
        portal_user = self.user_repo.get_by_id(teacher.user_id) if teacher.user_id else None
        timetables = self.repo.get_teacher_timetables(teacher_id)

        # Filter active assignments referencing active classes and subjects
        active_assignments = [
            a for a in (teacher.assignments or [])
            if a.status == "ACTIVE"
            and a.school_class and a.school_class.status == "ACTIVE"
            and a.subject and a.subject.status == "ACTIVE"
        ]
        assigned_classes_count = len(set(a.class_id for a in active_assignments))
        teaching_subjects_count = len(set(a.subject_id for a in active_assignments))
        teaching_assignments_count = len(active_assignments)

        # Build Full Profile
        return TeacherFullProfile(
            id=teacher.id,
            teacher_number=teacher.teacher_number,
            first_name=teacher.first_name,
            middle_name=teacher.middle_name,
            last_name=teacher.last_name,
            gender=teacher.gender,
            date_of_birth=teacher.date_of_birth,
            phone=teacher.phone,
            email=teacher.email,
            address=teacher.address,
            qualification=teacher.qualification,
            hire_date=teacher.hire_date,
            status=teacher.status,
            user_id=teacher.user_id,
            full_name=teacher.full_name,
            has_portal_access=portal_user is not None,
            portal_username=portal_user.username if portal_user else None,
            portal_email=portal_user.email if portal_user else None,
            created_at=teacher.created_at,
            updated_at=teacher.updated_at,
            assignments=active_assignments,
            assigned_classes_count=assigned_classes_count,
            teaching_subjects_count=teaching_subjects_count,
            teaching_assignments_count=teaching_assignments_count,
            timetables=[TeacherTimetableSlot.model_validate(tt) for tt in timetables]
        )

    def list_teachers(
        self,
        query: Optional[str] = None,
        status_filter: Optional[str] = None,
        class_id: Optional[int] = None,
        subject_id: Optional[int] = None,
        has_portal: Optional[bool] = None,
        academic_year: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[Teacher], int]:
        return self.repo.search_teachers(
            query=query,
            status=status_filter,
            class_id=class_id,
            subject_id=subject_id,
            has_portal=has_portal,
            academic_year=academic_year,
            skip=skip,
            limit=limit
        )

    def create_teacher(self, data: TeacherCreate, creator_user_id: Optional[int] = None) -> Teacher:
        # Check uniqueness
        if self.repo.get_by_number(data.teacher_number):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Teacher number '{data.teacher_number}' is already in use.")
        if self.repo.get_by_email(data.email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Teacher email '{data.email}' is already registered.")

        portal_user: Optional[User] = None
        if data.create_portal_account:
            username = data.portal_username or data.teacher_number.lower()
            password = data.portal_password or "Teacher@Hawlwadaag2026"

            # Check if user already exists
            if self.user_repo.get_by_username(username) or self.user_repo.get_by_email(data.email):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Portal username or email already exists in users database.")

            # Create User with TEACHER role
            portal_user = User(
                email=data.email.lower().strip(),
                username=username.lower().strip(),
                hashed_password=get_password_hash(password),
                full_name=f"{data.first_name} {data.last_name}".strip(),
                phone_number=data.phone,
                is_active=True,
                is_superuser=False
            )
            self.user_repo.create(portal_user)

            # Assign TEACHER role
            teacher_role = self.role_repo.get_or_create("TEACHER", "School faculty member")
            self.user_repo.add_role_to_user(portal_user, teacher_role, assigned_by_id=creator_user_id)

        teacher = Teacher(
            user_id=portal_user.id if portal_user else None,
            teacher_number=data.teacher_number.upper().strip(),
            first_name=data.first_name.strip(),
            middle_name=data.middle_name.strip() if data.middle_name else None,
            last_name=data.last_name.strip(),
            gender=data.gender.strip(),
            date_of_birth=data.date_of_birth,
            phone=data.phone.strip() if data.phone else None,
            email=data.email.lower().strip(),
            address=data.address.strip() if data.address else None,
            qualification=data.qualification.strip() if data.qualification else None,
            hire_date=data.hire_date,
            status=data.status.upper().strip()
        )
        created = self.repo.create(teacher)
        created.has_portal_access = portal_user is not None

        self.audit_repo.log_event(
            action="TEACHER_CREATED",
            user_id=creator_user_id,
            details={"teacher_id": created.id, "teacher_number": created.teacher_number, "has_portal": created.has_portal_access}
        )
        return created

    def update_teacher(self, teacher_id: int, data: TeacherUpdate, user_id: Optional[int] = None) -> Teacher:
        t = self.get_teacher(teacher_id)
        if data.first_name is not None:
            t.first_name = data.first_name.strip()
        if data.middle_name is not None:
            t.middle_name = data.middle_name.strip()
        if data.last_name is not None:
            t.last_name = data.last_name.strip()
        if data.gender is not None:
            t.gender = data.gender.strip()
        if data.date_of_birth is not None:
            t.date_of_birth = data.date_of_birth
        if data.phone is not None:
            t.phone = data.phone.strip()
        if data.email is not None:
            email_lower = data.email.lower().strip()
            if email_lower != t.email:
                existing = self.repo.get_by_email(email_lower)
                if existing and existing.id != t.id:
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already used by another teacher.")
                t.email = email_lower
        if data.address is not None:
            t.address = data.address.strip()
        if data.qualification is not None:
            t.qualification = data.qualification.strip()
        if data.hire_date is not None:
            t.hire_date = data.hire_date
        if data.status is not None:
            t.status = data.status.upper().strip()

        updated = self.repo.update(t)
        self.audit_repo.log_event(
            action="TEACHER_UPDATED",
            user_id=user_id,
            details={"teacher_id": updated.id, "name": updated.full_name}
        )
        return updated

    def update_status(self, teacher_id: int, new_status: str, reason: Optional[str] = None, user_id: Optional[int] = None) -> Teacher:
        teacher = self.get_teacher(teacher_id)
        teacher.status = new_status.upper().strip()
        updated = self.repo.update(teacher)

        # If deactivating, also toggle portal user if active
        if teacher.user_id:
            user = self.user_repo.get_by_id(teacher.user_id)
            if user:
                user.is_active = (new_status.upper() == "ACTIVE")
                self.user_repo.update(user)

        self.audit_repo.log_event(
            action="TEACHER_STATUS_CHANGED",
            user_id=user_id,
            details={"teacher_id": teacher.id, "new_status": new_status, "reason": reason}
        )
        return updated

    def create_portal_account(self, teacher_id: int, username: str, password: str, creator_id: Optional[int] = None) -> User:
        teacher = self.get_teacher(teacher_id)
        if teacher.user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Teacher already has a portal login account.")

        if self.user_repo.get_by_username(username) or self.user_repo.get_by_email(teacher.email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username or email already exists.")

        user = User(
            email=teacher.email,
            username=username.lower().strip(),
            hashed_password=get_password_hash(password),
            full_name=teacher.full_name,
            phone_number=teacher.phone,
            is_active=True,
            is_superuser=False
        )
        self.user_repo.create(user)

        teacher_role = self.role_repo.get_or_create("TEACHER", "School faculty member")
        self.user_repo.add_role_to_user(user, teacher_role, assigned_by_id=creator_id)

        teacher.user_id = user.id
        self.repo.update(teacher)

        self.audit_repo.log_event(
            action="TEACHER_PORTAL_ACCOUNT_CREATED",
            user_id=creator_id,
            details={"teacher_id": teacher.id, "username": user.username}
        )
        return user

    def assign_class_subject(self, teacher_id: int, data: TeacherAssignmentCreate, user_id: Optional[int] = None) -> TeacherAssignment:
        self.get_teacher(teacher_id)

        # Validate class exists
        school_class = self.db.query(SchoolClass).filter(SchoolClass.id == data.class_id).first()
        if not school_class:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Class with ID {data.class_id} not found.")

        # Validate subject exists
        subject = self.db.query(Subject).filter(Subject.id == data.subject_id).first()
        if not subject:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Subject with ID {data.subject_id} not found.")

        # Validate curriculum isolation: Division & Applicable Levels (if configured)
        if subject.division and subject.division.upper() != "ALL":
            if subject.division.upper() != (school_class.division or "PRIMARY").upper():
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Subject '{subject.name}' ({subject.division}) cannot be assigned to {school_class.division} class '{school_class.name}'."
                )

        year_str = (data.academic_year or school_class.academic_year or "2026/2027").strip()
        year_variants = {year_str, year_str.replace('/', '-'), year_str.replace('-', '/')}

        # Check whether the selected class, subject and academic year already have an assigned teacher
        existing = self.db.query(TeacherAssignment).filter(
            TeacherAssignment.class_id == data.class_id,
            TeacherAssignment.subject_id == data.subject_id,
            TeacherAssignment.academic_year.in_(year_variants),
            TeacherAssignment.status == "ACTIVE"
        ).first()

        if existing:
            if existing.teacher_id != teacher_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="This subject is already assigned to another teacher in this class."
                )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This teacher is already assigned to this subject and class for this academic year."
            )

        try:
            assignment = self.repo.assign_to_class_subject(
                teacher_id=teacher_id,
                class_id=data.class_id,
                subject_id=data.subject_id,
                academic_year=year_str
            )
            self.audit_repo.log_event(
                action="TEACHER_ASSIGNMENT_CREATED",
                user_id=user_id,
                details={"teacher_id": teacher_id, "class_id": data.class_id, "subject_id": data.subject_id, "academic_year": year_str}
            )
            return assignment
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This subject is already assigned to another teacher in this class."
            )

    def check_assignment_availability(
        self,
        class_id: int,
        subject_id: int,
        academic_year: str,
        teacher_id: Optional[int] = None,
        exclude_assignment_id: Optional[int] = None
    ) -> dict:
        year_str = (academic_year or "2026/2027").strip()
        year_variants = {year_str, year_str.replace('/', '-'), year_str.replace('-', '/')}
        q = self.db.query(TeacherAssignment).filter(
            TeacherAssignment.class_id == class_id,
            TeacherAssignment.subject_id == subject_id,
            TeacherAssignment.academic_year.in_(year_variants),
            TeacherAssignment.status == "ACTIVE"
        )
        if exclude_assignment_id:
            q = q.filter(TeacherAssignment.id != exclude_assignment_id)
        existing = q.first()

        if existing:
            if teacher_id is not None and existing.teacher_id == teacher_id:
                return {
                    "is_assigned": True,
                    "is_same_teacher": True,
                    "available": True,
                    "message": "Teacher already has this assignment.",
                    "assignment_id": existing.id,
                    "teacher_id": existing.teacher_id,
                    "teacher_name": existing.teacher_name
                }
            return {
                "is_assigned": True,
                "is_same_teacher": False,
                "available": False,
                "message": "This subject is already assigned to another teacher in this class.",
                "assignment_id": existing.id,
                "teacher_id": existing.teacher_id,
                "teacher_name": existing.teacher_name
            }
        return {
            "is_assigned": False,
            "is_same_teacher": False,
            "available": True,
            "message": "Available",
            "assignment_id": None,
            "teacher_id": None,
            "teacher_name": None
        }

    def update_assignment(
        self,
        assignment_id: int,
        data: TeacherAssignmentUpdate,
        user_id: Optional[int] = None
    ) -> TeacherAssignment:
        assignment = self.db.query(TeacherAssignment).filter(TeacherAssignment.id == assignment_id).first()
        if not assignment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found.")

        target_teacher_id = data.teacher_id if data.teacher_id is not None else assignment.teacher_id
        target_class_id = data.class_id if data.class_id is not None else assignment.class_id
        target_subject_id = data.subject_id if data.subject_id is not None else assignment.subject_id
        target_year = (data.academic_year or assignment.academic_year).strip()

        # Validate existence
        if data.teacher_id is not None:
            self.get_teacher(target_teacher_id)
        if data.class_id is not None:
            school_class = self.db.query(SchoolClass).filter(SchoolClass.id == target_class_id).first()
            if not school_class:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Class with ID {target_class_id} not found.")
        if data.subject_id is not None:
            subject = self.db.query(Subject).filter(Subject.id == target_subject_id).first()
            if not subject:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Subject with ID {target_subject_id} not found.")

        year_variants = {target_year, target_year.replace('/', '-'), target_year.replace('-', '/')}

        # Check whether another teacher is already assigned to target class, subject, and academic year
        existing = self.db.query(TeacherAssignment).filter(
            TeacherAssignment.class_id == target_class_id,
            TeacherAssignment.subject_id == target_subject_id,
            TeacherAssignment.academic_year.in_(year_variants),
            TeacherAssignment.status == "ACTIVE",
            TeacherAssignment.id != assignment_id
        ).first()

        if existing:
            if existing.teacher_id != target_teacher_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="This subject is already assigned to another teacher in this class."
                )

        assignment.teacher_id = target_teacher_id
        assignment.class_id = target_class_id
        assignment.subject_id = target_subject_id
        assignment.academic_year = target_year
        if data.status:
            assignment.status = data.status

        try:
            self.db.commit()
            self.db.refresh(assignment)
            self.audit_repo.log_event(
                action="TEACHER_ASSIGNMENT_UPDATED",
                user_id=user_id,
                details={"assignment_id": assignment_id, "teacher_id": target_teacher_id, "class_id": target_class_id, "subject_id": target_subject_id}
            )
            return assignment
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This subject is already assigned to another teacher in this class."
            )

    def bulk_assign(
        self,
        items: List[TeacherBulkAssignmentItem],
        teacher_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> List[TeacherAssignment]:
        if not items:
            return []

        # 1. Intra-batch duplicate check
        seen = {}
        for idx, item in enumerate(items):
            t_id = item.teacher_id or teacher_id
            if not t_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Teacher ID missing for assignment item {idx + 1}.")
            y_norm = item.academic_year.strip().replace('/', '-')
            key = (item.class_id, item.subject_id, y_norm)
            if key in seen:
                if seen[key] != t_id:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="This subject is already assigned to another teacher in this class."
                    )
            else:
                seen[key] = t_id

        # 2. Database check for each item
        results = []
        for item in items:
            t_id = item.teacher_id or teacher_id
            self.get_teacher(t_id)
            school_class = self.db.query(SchoolClass).filter(SchoolClass.id == item.class_id).first()
            if not school_class:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Class with ID {item.class_id} not found.")
            subject = self.db.query(Subject).filter(Subject.id == item.subject_id).first()
            if not subject:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Subject with ID {item.subject_id} not found.")

            year_str = item.academic_year.strip()
            year_variants = {year_str, year_str.replace('/', '-'), year_str.replace('-', '/')}

            existing = self.db.query(TeacherAssignment).filter(
                TeacherAssignment.class_id == item.class_id,
                TeacherAssignment.subject_id == item.subject_id,
                TeacherAssignment.academic_year.in_(year_variants),
                TeacherAssignment.status == "ACTIVE"
            ).first()

            if existing:
                if existing.teacher_id != t_id:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="This subject is already assigned to another teacher in this class."
                    )
                # Same teacher retains their own assignment
                results.append(existing)
            else:
                new_assignment = TeacherAssignment(
                    teacher_id=t_id,
                    class_id=item.class_id,
                    subject_id=item.subject_id,
                    academic_year=year_str,
                    status=item.status or "ACTIVE"
                )
                self.db.add(new_assignment)
                results.append(new_assignment)

        try:
            self.db.commit()
            for r in results:
                self.db.refresh(r)
            self.audit_repo.log_event(
                action="TEACHER_BULK_ASSIGNMENTS_CREATED",
                user_id=user_id,
                details={"count": len(results)}
            )
            return results
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This subject is already assigned to another teacher in this class."
            )

    def remove_assignment(self, assignment_id: int, user_id: Optional[int] = None) -> None:
        deleted = self.repo.remove_assignment(assignment_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found.")
        self.audit_repo.log_event(
            action="TEACHER_ASSIGNMENT_REMOVED",
            user_id=user_id,
            details={"assignment_id": assignment_id}
        )
