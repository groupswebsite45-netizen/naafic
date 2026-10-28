from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class Inquiry(Base, TimestampMixin):
    __tablename__ = "inquiries"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False)
    school_name = Column(String(200), nullable=False, index=True)
    email = Column(String(150), nullable=False, index=True)
    phone = Column(String(50), nullable=False)
    plan = Column(String(120), nullable=True)
    message = Column(Text, nullable=False)

    # Status: UNREAD, READ, IN_REVIEW, CONTACTED, CONVERTED, ARCHIVED
    status = Column(String(30), default="UNREAD", nullable=False, index=True)

    # Priority: LOW, NORMAL, HIGH, URGENT
    priority = Column(String(20), default="NORMAL", nullable=False)

    # Internal admin management notes and contact channel preference
    admin_notes = Column(Text, nullable=True)
    contacted_by = Column(String(100), nullable=True)
    preferred_channel = Column(String(50), nullable=True)  # WhatsApp, Email, Phone, Meeting

    # Public source
    source = Column(String(50), default="PUBLIC_LANDING_PAGE", nullable=False)

    # When converted to an active tenant school/academy
    converted_institution_id = Column(Integer, ForeignKey("institutions.id", ondelete="SET NULL"), nullable=True)

    converted_institution = relationship("Institution", foreign_keys=[converted_institution_id], lazy="joined")
