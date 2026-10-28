from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class User(Base, TimestampMixin):
    """User model representing all system actors."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(200), nullable=False)
    phone_number = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user_roles = relationship(
        "UserRole",
        back_populates="user",
        foreign_keys="[UserRole.user_id]",
        cascade="all, delete-orphan",
        lazy="joined"
    )
    sessions = relationship("SessionModel", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")

    @property
    def roles(self):
        """Helper property to access list of Role objects."""
        return [ur.role for ur in self.user_roles if ur.role is not None]

    @property
    def role_names(self):
        """Helper property to access role names."""
        return [ur.role.name for ur in self.user_roles if ur.role is not None]

    def has_role(self, role_name: str) -> bool:
        """Check if user has a specific role."""
        if self.is_superuser:
            return True
        return role_name.upper() in [r.upper() for r in self.role_names]

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
