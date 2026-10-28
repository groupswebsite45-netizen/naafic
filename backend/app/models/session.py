from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class SessionModel(Base, TimestampMixin):
    """User active session and refresh token model."""
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    refresh_token = Column(Text, nullable=False, unique=True, index=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    is_revoked = Column(Boolean, default=False, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    # Relationships
    user = relationship("User", back_populates="sessions")

    def is_valid(self) -> bool:
        """Check if session is active and not expired."""
        if self.is_revoked:
            return False
        return datetime.now(timezone.utc) < self.expires_at

    def __repr__(self) -> str:
        return f"<Session(id={self.id}, user_id={self.user_id}, is_revoked={self.is_revoked})>"
