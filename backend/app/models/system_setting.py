from sqlalchemy import Column, Integer, String, Boolean, Text
from app.core.database import Base
from app.models.base import TimestampMixin


class SystemSetting(Base, TimestampMixin):
    """Key-value system configuration settings."""
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)
    description = Column(String(255), nullable=True)
    is_public = Column(Boolean, default=False, nullable=False)

    def __repr__(self) -> str:
        return f"<SystemSetting(key='{self.key}')>"
