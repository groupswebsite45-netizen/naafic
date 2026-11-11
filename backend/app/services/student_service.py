import os
import io
import re
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile
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
from app.utils.logger import logger

UPLOAD_STUDENT_PHOTOS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "uploads",
    "student_photos"
)
ALLOWED_PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_PHOTO_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_PHOTO_SIZE = 5 * 1024 * 1024  # 5 MB


def validate_image_bytes(contents: bytes, filename: str) -> str:
    """
    Validates file size, extension, magic bytes, and image structure.
    Returns normalized mime type or raises HTTPException.
    """
    if len(contents) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded photo file is empty."
        )
    if len(contents) > MAX_PHOTO_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Photo size exceeds maximum allowed limit of {MAX_PHOTO_SIZE // (1024 * 1024)}MB."
        )

    _, ext = os.path.splitext(filename.lower())
    if ext not in ALLOWED_PHOTO_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension '{ext}'. Allowed extensions are: JPG, JPEG, PNG, WEBP."
        )

    # Magic byte inspection
    is_jpeg = contents.startswith(b"\xff\xd8\xff")
    is_png = contents.startswith(b"\x89PNG\r\n\x1a\n")
    is_webp = contents.startswith(b"RIFF") and len(contents) > 12 and contents[8:12] == b"WEBP"

    if not (is_jpeg or is_png or is_webp):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image format. The file content does not match a valid JPG, PNG, or WEBP image."
        )

    # Deep verification with PIL to ensure not executable or corrupted
    try:
        from PIL import Image
        image = Image.open(io.BytesIO(contents))
        image.verify()
        format_name = (image.format or "").upper()
        if format_name not in {"JPEG", "PNG", "WEBP"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported internal image format '{format_name}'."
            )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Corrupted or invalid image file. Verification failed."
        )

    if is_jpeg:
        return "image/jpeg"
    elif is_png:
        return "image/png"
    else:
        return "image/webp"



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
            "photo_path": student.photo_path,
            "photo_url": student.photo_url,
            "photo_filename": student.photo_filename,
            "photo_mime_type": student.photo_mime_type,
            "photo_size": student.photo_size,
            "photo_uploaded_at": student.photo_uploaded_at,
            "photo_updated_at": student.photo_updated_at,
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

    def batch_enable_portals(self, payload: Any, creator_id: Optional[int] = None) -> Dict[str, Any]:
        """
        One-click batch enablement of student portal access.
        Provisions user accounts for students without one using clean username generation and default password.
        Reactivates inactive accounts.
        """
        academic_year = getattr(payload, "academic_year", None)
        class_id = getattr(payload, "class_id", None)
        student_ids = getattr(payload, "student_ids", None)
        default_pwd = getattr(payload, "default_password", None) or "Student@123"

        query = self.db.query(Student).filter(Student.status == "ACTIVE")
        if student_ids:
            query = query.filter(Student.id.in_(student_ids))
        else:
            if class_id or academic_year:
                enr_filters = [StudentEnrollment.status == "ACTIVE"]
                if class_id:
                    enr_filters.append(StudentEnrollment.class_id == class_id)
                if academic_year:
                    cleaned = academic_year.strip()
                    variants = list({cleaned, cleaned.replace("-", "/"), cleaned.replace("/", "-")})
                    enr_filters.append(StudentEnrollment.academic_year.in_(variants))
                query = query.join(StudentEnrollment).filter(and_(*enr_filters))

        students = query.order_by(Student.id.asc()).all()

        student_role = self.role_repo.get_or_create("STUDENT", "Enrolled student account")
        results_list = []
        created_count = 0
        activated_count = 0
        already_active_count = 0

        for st in students:
            if st.user_id and st.user:
                if not st.user.is_active:
                    st.user.is_active = True
                    self.user_repo.update(st.user)
                    activated_count += 1
                    status_str = "ACTIVATED"
                else:
                    already_active_count += 1
                    status_str = "ALREADY_ACTIVE"
                # Ensure student role is assigned
                self.user_repo.add_role_to_user(st.user, student_role, assigned_by_id=creator_id)
                results_list.append({
                    "student_id": st.id,
                    "student_name": st.full_name,
                    "admission_number": st.admission_number,
                    "username": st.user.username,
                    "status": status_str
                })
            else:
                # Need to provision fresh portal account
                username = self.suggest_portal_username(st.id)
                email = f"{username}@student.somroyal.edu.so"
                user = User(
                    email=email,
                    username=username,
                    hashed_password=get_password_hash(default_pwd),
                    full_name=st.full_name,
                    phone_number=st.phone,
                    is_active=True,
                    is_superuser=False
                )
                self.user_repo.create(user)
                self.user_repo.add_role_to_user(user, student_role, assigned_by_id=creator_id)
                st.user_id = user.id
                self.repo.update(st)
                created_count += 1
                results_list.append({
                    "student_id": st.id,
                    "student_name": st.full_name,
                    "admission_number": st.admission_number,
                    "username": username,
                    "status": "CREATED"
                })

        self.db.commit()

        self.audit_repo.log_event(
            action="BATCH_STUDENT_PORTALS_ENABLED",
            user_id=creator_id,
            details={
                "total": len(students),
                "created": created_count,
                "activated": activated_count,
                "already_active": already_active_count
            }
        )

        return {
            "success": True,
            "message": f"Successfully processed {len(students)} student portals: {created_count} created, {activated_count} activated, {already_active_count} already active.",
            "total_processed": len(students),
            "enabled_count": created_count + activated_count,
            "already_active_count": already_active_count,
            "default_password": default_pwd,
            "students": results_list
        }

    def toggle_portal_quick(self, student_id: int, is_active: Optional[bool] = None, default_password: str = "Student@123", creator_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Quick one-click toggle of student portal access.
        If no portal user account exists and action is enable (or toggle), provisions account with default password.
        If account exists, sets or inverts is_active.
        """
        student = self.get_student(student_id)
        student_role = self.role_repo.get_or_create("STUDENT", "Enrolled student account")

        if not student.user_id or not student.user:
            if is_active is False:
                return {
                    "student_id": student.id,
                    "has_portal_access": False,
                    "portal_username": None,
                    "portal_is_active": False,
                    "message": f"Portal access is already disabled for {student.full_name}."
                }
            username = self.suggest_portal_username(student.id)
            email = f"{username}@student.somroyal.edu.so"
            user = User(
                email=email,
                username=username,
                hashed_password=get_password_hash(default_password),
                full_name=student.full_name,
                phone_number=student.phone,
                is_active=True,
                is_superuser=False
            )
            self.user_repo.create(user)
            self.user_repo.add_role_to_user(user, student_role, assigned_by_id=creator_id)
            student.user_id = user.id
            self.repo.update(student)
            self.db.commit()

            self.audit_repo.log_event(
                action="STUDENT_PORTAL_ACCOUNT_CREATED",
                user_id=creator_id,
                details={"student_id": student.id, "username": username}
            )

            return {
                "student_id": student.id,
                "has_portal_access": True,
                "portal_username": username,
                "portal_is_active": True,
                "message": f"Portal login enabled for {student.full_name} (Username: {username}, Password: {default_password})."
            }
        else:
            new_status = not student.user.is_active if is_active is None else is_active
            student.user.is_active = new_status
            self.user_repo.update(student.user)
            self.db.commit()

            self.audit_repo.log_event(
                action="STUDENT_PORTAL_STATUS_CHANGED",
                user_id=creator_id,
                details={"student_id": student.id, "username": student.user.username, "is_active": new_status}
            )

            return {
                "student_id": student.id,
                "has_portal_access": new_status,
                "portal_username": student.user.username,
                "portal_is_active": new_status,
                "message": f"Portal access {'enabled' if new_status else 'disabled'} for {student.full_name}."
            }

    def get_student_portal_token(self, student_id: int, admin_user: User) -> Dict[str, Any]:
        """
        Generate authentic student access token allowing admin to seamlessly log into or view any student's portal.
        Auto-provisions portal account if student does not have one yet.
        """
        student = self.get_student(student_id)
        if not student.user_id or not student.user:
            self.toggle_portal_quick(student_id, is_active=True, creator_id=admin_user.id)
            student = self.get_student(student_id)

        user = student.user
        if not user.is_active:
            user.is_active = True
            self.user_repo.update(user)
            self.db.commit()

        from app.core.tenant_context import get_default_database_name
        from app.core.security import create_access_token
        from datetime import timedelta

        default_db = get_default_database_name()
        db_name = default_db
        if self.db and hasattr(self.db, "bind") and self.db.bind:
            db_name = self.db.bind.url.database or default_db

        institution_id = None
        institution_code = None
        try:
            from app.core.tenant_context import get_central_sessionmaker
            from app.models.institution import Institution
            with get_central_sessionmaker()() as cs:
                inst = cs.query(Institution).filter(Institution.database_name == db_name).first()
                if inst:
                    institution_id = inst.id
                    institution_code = inst.code
        except Exception:
            pass

        token_claims = {
            "email": user.email,
            "username": user.username,
            "roles": ["STUDENT"],
            "is_superuser": False,
            "database_name": db_name,
            "institution_code": institution_code,
            "institution_id": institution_id,
        }

        access_token = create_access_token(
            subject=user.id,
            claims=token_claims,
            expires_delta=timedelta(hours=4)
        )

        self.audit_repo.log_event(
            action="ADMIN_IMPERSONATE_STUDENT_PORTAL",
            user_id=admin_user.id,
            details={"student_id": student.id, "student_username": user.username}
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "student_id": student.id,
            "student_name": student.full_name,
            "username": user.username,
            "portal_url": "/student/exams"
        }

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

    async def upload_student_photo(self, student_id: int, file: UploadFile, user_id: Optional[int] = None) -> Student:
        """
        Permanently save and associate student profile photograph.
        Performs magic bytes & PIL structure validation, safe unique filename generation,
        and safe cleanup of previous photo file if replacing.
        """
        student = self.get_student(student_id)
        os.makedirs(UPLOAD_STUDENT_PHOTOS_DIR, exist_ok=True)

        contents = await file.read()
        mime_type = validate_image_bytes(contents, file.filename or "photo.jpg")

        ext = ".jpg" if mime_type == "image/jpeg" else (".png" if mime_type == "image/png" else ".webp")
        safe_filename = f"student_{student.id}_{uuid.uuid4().hex[:12]}{ext}"
        relative_path = f"student_photos/{safe_filename}"
        full_path = os.path.join(UPLOAD_STUDENT_PHOTOS_DIR, safe_filename)

        # Safely remove existing photo file to prevent storage leaks
        if student.photo_path:
            old_full_path = os.path.join(
                os.path.dirname(UPLOAD_STUDENT_PHOTOS_DIR),
                student.photo_path.replace("/", os.sep).replace("\\", os.sep)
            )
            if os.path.exists(old_full_path) and os.path.isfile(old_full_path):
                try:
                    os.remove(old_full_path)
                except Exception as ex:
                    logger.warning(f"Could not remove old student photo: {ex}")

        with open(full_path, "wb") as f:
            f.write(contents)

        now = datetime.now(timezone.utc)
        student.photo_path = relative_path
        student.photo_filename = file.filename or safe_filename
        student.photo_mime_type = mime_type
        student.photo_size = len(contents)
        if not student.photo_uploaded_at:
            student.photo_uploaded_at = now
        student.photo_updated_at = now

        updated = self.repo.update(student)
        self.audit_repo.log_event(
            action="STUDENT_PHOTO_UPLOADED",
            user_id=user_id,
            details={
                "student_id": student.id,
                "admission_number": student.admission_number,
                "photo_filename": student.photo_filename,
                "photo_size": student.photo_size,
                "photo_mime_type": student.photo_mime_type
            }
        )
        return updated

    def delete_student_photo(self, student_id: int, user_id: Optional[int] = None) -> Student:
        """Remove student profile photo file and reset database references."""
        student = self.get_student(student_id)
        if not student.photo_path:
            return student

        old_full_path = os.path.join(
            os.path.dirname(UPLOAD_STUDENT_PHOTOS_DIR),
            student.photo_path.replace("/", os.sep).replace("\\", os.sep)
        )
        if os.path.exists(old_full_path) and os.path.isfile(old_full_path):
            try:
                os.remove(old_full_path)
            except Exception as ex:
                logger.warning(f"Could not delete student photo file: {ex}")

        student.photo_path = None
        student.photo_filename = None
        student.photo_mime_type = None
        student.photo_size = None
        student.photo_updated_at = datetime.now(timezone.utc)

        updated = self.repo.update(student)
        self.audit_repo.log_event(
            action="STUDENT_PHOTO_REMOVED",
            user_id=user_id,
            details={"student_id": student.id, "admission_number": student.admission_number}
        )
        return updated

    def get_student_photo_file(self, student_id: int) -> Dict[str, Any]:
        """Retrieve stored file details for student photo."""
        student = self.get_student(student_id)
        if not student.photo_path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No photo found for this student."
            )
        full_path = os.path.join(
            os.path.dirname(UPLOAD_STUDENT_PHOTOS_DIR),
            student.photo_path.replace("/", os.sep).replace("\\", os.sep)
        )
        if not os.path.exists(full_path) or not os.path.isfile(full_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Stored student photo file was not found on server."
            )
        return {
            "full_path": full_path,
            "filename": student.photo_filename or f"student_{student.id}.jpg",
            "mime_type": student.photo_mime_type or "image/jpeg",
            "size": student.photo_size or os.path.getsize(full_path),
        }
