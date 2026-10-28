from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
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

        # Check duplicate assignment
        existing = self.db.query(TeacherAssignment).filter(
            TeacherAssignment.teacher_id == teacher_id,
            TeacherAssignment.class_id == data.class_id,
            TeacherAssignment.subject_id == data.subject_id,
            TeacherAssignment.academic_year == data.academic_year.strip(),
            TeacherAssignment.status == "ACTIVE"
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Teacher is already actively assigned to {school_class.name} for {subject.name} ({data.academic_year})."
            )

        assignment = self.repo.assign_to_class_subject(
            teacher_id=teacher_id,
            class_id=data.class_id,
            subject_id=data.subject_id,
            academic_year=data.academic_year
        )
        self.audit_repo.log_event(
            action="TEACHER_ASSIGNMENT_CREATED",
            user_id=user_id,
            details={"teacher_id": teacher_id, "class_id": data.class_id, "subject_id": data.subject_id}
        )
        return assignment

    def remove_assignment(self, assignment_id: int, user_id: Optional[int] = None) -> None:
        deleted = self.repo.remove_assignment(assignment_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found.")
        self.audit_repo.log_event(
            action="TEACHER_ASSIGNMENT_REMOVED",
            user_id=user_id,
            details={"assignment_id": assignment_id}
        )
