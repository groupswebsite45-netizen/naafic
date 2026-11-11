from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.models.teacher import Teacher
from app.models.student import Student
from app.repositories.base_repo import BaseRepository


class UserRepository(BaseRepository[User]):
    """User repository for database operations."""

    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(func.lower(User.email) == email.lower().strip()).first()

    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(func.lower(User.username) == username.lower().strip()).first()

    def get_by_identifier(self, identifier: str) -> Optional[User]:
        """Find user by email, username, teacher number, student admission number, or common aliases."""
        clean_id = identifier.lower().strip()

        # 1. Direct match on User email or username
        user = self.db.query(User).filter(
            or_(
                func.lower(User.email) == clean_id,
                func.lower(User.username) == clean_id
            )
        ).first()
        if user:
            return user

        # 2. Known developer / documentation convenience aliases
        alias_map = {
            "teacher": "teacher.ali",
            "teacher_math": "teacher.ali",
            "teacher-math": "teacher.ali",
            "teacher.math": "teacher.ali",
            "teacher_ahmed": "teacher.ahmed.12s",
            "teacher_ali": "teacher.ali",
            "teacher_english": "teacher.ali",
            "teacher_science": "teacher.ali",
            "teacher_islamic": "teacher.ali",
            "teacher_ict": "teacher.ali",
            "std_farhan": "std_12s_001",
            "student_farhan": "std_12s_001",
            "student": "std_12s_001",
            "tch-1001": "tch-ali-01",
            "tch-001": "tch-ali-01",
        }
        if clean_id in alias_map:
            target = alias_map[clean_id]
            user = self.db.query(User).filter(func.lower(User.username) == target).first()
            if user:
                return user
            clean_id = target

        # 3. Match by Teacher Number (e.g. TCH-001, TCH-2026-001)
        teacher = self.db.query(Teacher).filter(
            func.lower(Teacher.teacher_number) == clean_id
        ).first()
        if teacher and teacher.user_id:
            return self.get_by_id(teacher.user_id)

        # 3b. Match by Teacher Email or Email Prefix (e.g. fadumo.warsame, fadumo)
        teacher_match = self.db.query(Teacher).filter(
            or_(
                func.lower(Teacher.email) == clean_id,
                func.lower(Teacher.email).like(f"{clean_id}@%"),
                func.lower(Teacher.first_name) == clean_id
            )
        ).first()
        if teacher_match and teacher_match.user_id:
            return self.get_by_id(teacher_match.user_id)

        # 4. Match by Student Admission Number (e.g. ADM-2026-001)
        student = self.db.query(Student).filter(
            func.lower(Student.admission_number) == clean_id
        ).first()
        if student and student.user_id:
            return self.get_by_id(student.user_id)

        return None

    def update_last_login(self, user_id: int) -> None:
        user = self.get_by_id(user_id)
        if user:
            user.last_login_at = datetime.now(timezone.utc)
            self.db.commit()

    def add_role_to_user(self, user: User, role: Role, assigned_by_id: Optional[int] = None) -> UserRole:
        user_role = self.db.query(UserRole).filter(
            UserRole.user_id == user.id,
            UserRole.role_id == role.id
        ).first()
        if not user_role:
            from datetime import datetime, timezone
            user_role = UserRole(
                user_id=user.id,
                role_id=role.id,
                assigned_at=datetime.now(timezone.utc),
                assigned_by=assigned_by_id
            )
            self.db.add(user_role)
            self.db.commit()
            self.db.refresh(user)
        return user_role
