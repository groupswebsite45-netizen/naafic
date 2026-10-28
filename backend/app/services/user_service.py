from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.repositories.audit_repo import AuditLogRepository
from app.schemas.user import UserProfileUpdate


class UserService:
    """Service handling user profile updates and user management."""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.audit_repo = AuditLogRepository(db)

    def update_profile(
        self,
        user: User,
        data: UserProfileUpdate,
        ip_address: Optional[str] = None
    ) -> User:
        """Update authenticated user's profile information."""
        if data.full_name is not None:
            user.full_name = data.full_name.strip()
        if data.phone_number is not None:
            user.phone_number = data.phone_number.strip()

        updated_user = self.user_repo.update(user)

        self.audit_repo.log_event(
            action="PROFILE_UPDATED",
            status="SUCCESS",
            user_id=user.id,
            ip_address=ip_address,
            details={"full_name": updated_user.full_name}
        )
        return updated_user
