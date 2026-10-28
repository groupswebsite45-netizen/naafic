import re
from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.models.user import User
from app.core.security import get_password_hash
from app.repositories.student_repo import StudentRepository
from app.repositories.user_repo import UserRepository
from app.repositories.role_repo import RoleRepository
from app.repositories.class_repo import ClassRepository
from app.repositories.audit_repo import AuditLogRepository
from app.schemas.student import (
    StudentCreate,
    StudentUpdate,
    StudentEnrollmentCreate,
    StudentSummaryMetrics,
)


class StudentService:
    """Service handling Student records, profile summaries, and enrollment operations."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = StudentRepository(db)
        self.user_repo = UserRepository(db)
        self.role_repo = RoleRepository(db)
        self.class_repo = ClassRepository(db)
        self.audit_repo = AuditLogRepository(db)

    def get_summary_metrics(self, academic_year: Optional[str] = None) -> StudentSummaryMetrics:
        metrics = self.repo.get_summary_metrics(academic_year=academic_year)
        return StudentSummaryMetrics(**metrics)

    def get_student(self, student_id: int) -> Student:
        s = self.repo.get_by_id(student_id)
        if not s:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")
        s.has_portal_access = s.user_id is not None
        if s.user:
            s.portal_username = s.user.username
        return s

    def get_full_profile(self, student_id: int) -> Dict[str, Any]:
        student = self.get_student(student_id)
        fin_summary = self.repo.get_student_financial_summary(student_id)
        fees = self.repo.get_student_fees(student_id)
        exams = self.repo.get_student_exam_results(student_id)

        return {
            "id": student.id,
            "user_id": student.user_id,
            "admission_number": student.admission_number,
            "first_name": student.first_name,
            "middle_name": student.middle_name,
            "last_name": student.last_name,
            "gender": student.gender,
            "date_of_birth": student.date_of_birth,
            "phone": student.phone,
            "address": student.address,
            "guardian_name": student.guardian_name,
            "guardian_phone": student.guardian_phone,
            "guardian_email": student.guardian_email,
            "guardian_relationship": student.guardian_relationship,
            "admission_date": student.admission_date,
            "status": student.status,
            "full_name": student.full_name,
            "has_portal_access": student.has_portal_access,
            "portal_username": student.portal_username,
            "created_at": student.created_at,
            "updated_at": student.updated_at,
            "current_class": student.current_class,
            "enrollments": student.enrollments,
            "financial_summary": fin_summary,
            "fees": fees,
            "exam_results": exams,
        }

    def list_students(
        self,
        query: Optional[str] = None,
        class_id: Optional[int] = None,
        academic_year: Optional[str] = None,
        gender: Optional[str] = None,
        status_filter: Optional[str] = None,
        has_portal: Optional[bool] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[Student], int]:
        if class_id is not None:
            c = self.class_repo.get_by_id(class_id)
            if not c:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Class with ID {class_id} was not found in the system."
                )
            if c.status != "ACTIVE":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Class '{c.name}' is currently {c.status} and cannot be used for active student filtering."
                )
            if academic_year and academic_year.strip() and c.academic_year != academic_year.strip():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Class '{c.name}' belongs to academic year '{c.academic_year}', not '{academic_year}'."
                )

        return self.repo.search_students(
            query=query,
            class_id=class_id,
            academic_year=academic_year,
            gender=gender,
            status=status_filter,
            has_portal=has_portal,
            skip=skip,
            limit=limit
        )

    def create_student(self, data: StudentCreate, creator_user_id: Optional[int] = None) -> Student:
        # Check admission number uniqueness
        if self.repo.get_by_admission_number(data.admission_number):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Admission number '{data.admission_number}' already exists in the system."
            )

        portal_user: Optional[User] = None
        if data.create_portal_account:
            username = data.portal_username or data.admission_number.lower()
            password = data.portal_password or "Student@Hawlwadaag2026"
            email = f"{username}@student.hawlwadaagschool.edu.so"

            if self.user_repo.get_by_username(username):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Portal username already exists.")

            portal_user = User(
                email=email,
                username=username.lower().strip(),
                hashed_password=get_password_hash(password),
                full_name=f"{data.first_name} {data.last_name}".strip(),
                phone_number=data.phone,
                is_active=True,
                is_superuser=False
            )
            self.user_repo.create(portal_user)

            # Assign STUDENT role
            student_role = self.role_repo.get_or_create("STUDENT", "Enrolled student account")
            self.user_repo.add_role_to_user(portal_user, student_role, assigned_by_id=creator_user_id)

        student = Student(
            user_id=portal_user.id if portal_user else None,
            admission_number=data.admission_number.upper().strip(),
            first_name=data.first_name.strip(),
            middle_name=data.middle_name.strip() if data.middle_name else None,
            last_name=data.last_name.strip(),
            gender=data.gender.strip(),
            date_of_birth=data.date_of_birth,
            phone=data.phone.strip() if data.phone else None,
            address=data.address.strip() if data.address else None,
            guardian_name=data.guardian_name.strip() if data.guardian_name else None,
            guardian_phone=data.guardian_phone.strip() if data.guardian_phone else None,
            guardian_email=data.guardian_email.lower().strip() if data.guardian_email else None,
            guardian_relationship=data.guardian_relationship.strip() if data.guardian_relationship else None,
            admission_date=data.admission_date,
            status=data.status.upper().strip()
        )
        created = self.repo.create(student)
        created.has_portal_access = portal_user is not None
        if portal_user:
            created.portal_username = portal_user.username

        # Initial class enrollment if specified
        if data.initial_class_id:
            c = self.class_repo.get_by_id(data.initial_class_id)
            if c:
                academic_year = data.academic_year or c.academic_year
                self.repo.enroll_student(
                    student_id=created.id,
                    class_id=c.id,
                    academic_year=academic_year,
                    start_date=data.admission_date
                )

        self.audit_repo.log_event(
            action="STUDENT_REGISTERED",
            user_id=creator_user_id,
            details={"student_id": created.id, "admission_number": created.admission_number, "class_id": data.initial_class_id}
        )
        return created

    def update_student(self, student_id: int, data: StudentUpdate, user_id: Optional[int] = None) -> Student:
        s = self.get_student(student_id)
        if data.first_name is not None:
            s.first_name = data.first_name.strip()
        if data.middle_name is not None:
            s.middle_name = data.middle_name.strip() if data.middle_name else None
        if data.last_name is not None:
            s.last_name = data.last_name.strip()
        if data.gender is not None:
            s.gender = data.gender.strip()
        if data.date_of_birth is not None:
            s.date_of_birth = data.date_of_birth
        if data.phone is not None:
            s.phone = data.phone.strip() if data.phone else None
        if data.address is not None:
            s.address = data.address.strip() if data.address else None
        if data.guardian_name is not None:
            s.guardian_name = data.guardian_name.strip() if data.guardian_name else None
        if data.guardian_phone is not None:
            s.guardian_phone = data.guardian_phone.strip() if data.guardian_phone else None
        if data.guardian_email is not None:
            s.guardian_email = data.guardian_email.lower().strip() if data.guardian_email else None
        if data.guardian_relationship is not None:
            s.guardian_relationship = data.guardian_relationship.strip() if data.guardian_relationship else None
        if data.admission_date is not None:
            s.admission_date = data.admission_date
        if data.status is not None:
            s.status = data.status.upper().strip()

        updated = self.repo.update(s)
        self.audit_repo.log_event(
            action="STUDENT_UPDATED",
            user_id=user_id,
            details={"student_id": updated.id, "name": updated.full_name}
        )
        return updated

    def update_status(self, student_id: int, new_status: str, reason: Optional[str] = None, user_id: Optional[int] = None) -> Student:
        s = self.get_student(student_id)
        old_status = s.status
        s.status = new_status.upper().strip()
        updated = self.repo.update(s)

        self.audit_repo.log_event(
            action="STUDENT_STATUS_CHANGED",
            user_id=user_id,
            details={
                "student_id": updated.id,
                "admission_number": updated.admission_number,
                "old_status": old_status,
                "new_status": updated.status,
                "reason": reason
            }
        )
        return updated

    def suggest_portal_username(self, student_id: int) -> str:
        """Automatically suggest a valid unique username (min 3 chars) for student portal."""
        student = self.get_student(student_id)
        fn = re.sub(r"[^a-zA-Z0-9]", "", student.first_name.lower().strip()) if student.first_name else "student"
        if len(fn) < 2:
            fn = "student"

        adm_raw = student.admission_number.lower().replace("adm-", "").replace("adm", "").strip()
        adm_clean = re.sub(r"[^a-zA-Z0-9]", "", adm_raw)

        base = f"{fn}{adm_clean}"
        if len(base) < 3:
            base = f"{fn}{str(student.id).zfill(3)}"

        candidate = base
        counter = 2
        while self.user_repo.get_by_username(candidate):
            candidate = f"{base}_{counter}"
            counter += 1

        return candidate

    def create_portal_account(self, student_id: int, username: str, password: str, creator_id: Optional[int] = None) -> User:
        student = self.get_student(student_id)
        if student.user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Student already has a portal login account.")

        if student.status != "ACTIVE":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot activate portal account for an inactive student.")

        clean_username = username.lower().strip()
        if len(clean_username) < 3:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Username must be at least 3 characters.")
        if len(clean_username) > 50:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Username cannot exceed 50 characters.")
        if not re.match(r"^[a-zA-Z0-9._-]+$", clean_username):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Username may only contain letters, numbers, underscores, dots, and hyphens.")

        if not password or len(password) < 6:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Password must be at least 6 characters.")

        if self.user_repo.get_by_username(clean_username):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists.")

        email = f"{clean_username}@student.hawlwadaagschool.edu.so"
        user = User(
            email=email,
            username=clean_username,
            hashed_password=get_password_hash(password),
            full_name=student.full_name,
            phone_number=student.phone,
            is_active=True,
            is_superuser=False
        )
        self.user_repo.create(user)

        student_role = self.role_repo.get_or_create("STUDENT", "Enrolled student account")
        self.user_repo.add_role_to_user(user, student_role, assigned_by_id=creator_id)

        student.user_id = user.id
        self.repo.update(student)

        self.audit_repo.log_event(
            action="STUDENT_PORTAL_ACCOUNT_CREATED",
            user_id=creator_id,
            details={"student_id": student.id, "username": user.username}
        )
        return user

    def reset_portal_password(self, student_id: int, new_password: str, creator_id: Optional[int] = None) -> User:
        student = self.get_student(student_id)
        if not student.user_id or not student.user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Student does not have a portal login account.")

        if not new_password or len(new_password) < 6:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Password must be at least 6 characters.")

        student.user.hashed_password = get_password_hash(new_password)
        self.user_repo.update(student.user)

        self.audit_repo.log_event(
            action="STUDENT_PORTAL_PASSWORD_RESET",
            user_id=creator_id,
            details={"student_id": student.id, "username": student.user.username}
        )
        return student.user

    def toggle_portal_access(self, student_id: int, is_active: bool, creator_id: Optional[int] = None) -> User:
        student = self.get_student(student_id)
        if not student.user_id or not student.user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Student does not have a portal login account.")

        student.user.is_active = is_active
        self.user_repo.update(student.user)

        self.audit_repo.log_event(
            action="STUDENT_PORTAL_STATUS_CHANGED",
            user_id=creator_id,
            details={"student_id": student.id, "username": student.user.username, "is_active": is_active}
        )
        return student.user

    def change_portal_username(self, student_id: int, new_username: str, creator_id: Optional[int] = None) -> User:
        student = self.get_student(student_id)
        if not student.user_id or not student.user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Student does not have a portal login account.")

        clean_username = new_username.lower().strip()
        if len(clean_username) < 3:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Username must be at least 3 characters.")
        if len(clean_username) > 50:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Username cannot exceed 50 characters.")
        if not re.match(r"^[a-zA-Z0-9._-]+$", clean_username):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Username may only contain letters, numbers, underscores, dots, and hyphens.")

        existing = self.user_repo.get_by_username(clean_username)
        if existing and existing.id != student.user_id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists.")

        student.user.username = clean_username
        student.user.email = f"{clean_username}@student.hawlwadaagschool.edu.so"
        self.user_repo.update(student.user)

        self.audit_repo.log_event(
            action="STUDENT_PORTAL_USERNAME_CHANGED",
            user_id=creator_id,
            details={"student_id": student.id, "new_username": clean_username}
        )
        return student.user

    def enroll_student_to_class(self, student_id: int, data: StudentEnrollmentCreate, user_id: Optional[int] = None) -> StudentEnrollment:
        student = self.get_student(student_id)
        c = self.class_repo.get_by_id(data.class_id)
        if not c:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class not found.")

        # Check existing active enrollment for student & year
        existing = (
            self.db.query(StudentEnrollment)
            .filter(
                StudentEnrollment.student_id == student_id,
                StudentEnrollment.academic_year == data.academic_year.strip(),
                StudentEnrollment.status == "ACTIVE"
            )
            .first()
        )
        if existing:
            if existing.class_id == data.class_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Student is already enrolled in this class for this academic year."
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Student is already enrolled in another active class for this academic year."
                )

        enrollment = StudentEnrollment(
            student_id=student_id,
            class_id=data.class_id,
            academic_year=data.academic_year.strip(),
            roll_number=data.roll_number,
            start_date=data.start_date,
            status="ACTIVE"
        )
        self.db.add(enrollment)
        self.db.commit()
        self.db.refresh(enrollment)

        self.audit_repo.log_event(
            action="STUDENT_ENROLLED",
            user_id=user_id,
            details={"student_id": student_id, "class_id": data.class_id, "academic_year": data.academic_year}
        )
        return enrollment
