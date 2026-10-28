from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class NotificationTemplate(Base, TimestampMixin):
    """Reusable notification message templates with placeholder support."""
    __tablename__ = "notification_templates"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(100), unique=True, nullable=False, index=True)  # e.g., "ATTENDANCE_ABSENT", "RESULT_RELEASED"
    name = Column(String(200), nullable=False)
    title_template = Column(String(255), nullable=False)
    body_template = Column(Text, nullable=False)
    category = Column(String(50), default="GENERAL", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_system = Column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<NotificationTemplate(code='{self.code}', name='{self.name}')>"


class Notification(Base, TimestampMixin):
    """
    Main notification communication record.
    Represents an individualized notification message sent to a guardian, student, or staff.
    """
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    notification_type = Column(String(50), nullable=False, index=True)  # ATTENDANCE_ABSENT, RESULT_RELEASED, FEE_REMINDER, GENERAL_ANNOUNCEMENT, CUSTOM
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    channel = Column(String(50), default="SMS", nullable=False, index=True)  # SMS, EMAIL, IN_APP, WHATSAPP
    status = Column(String(50), default="PENDING", nullable=False, index=True)  # QUEUED, PENDING, SENT, DELIVERED, READ, FAILED, NOT_SENT, NOT_CONFIGURED
    failure_reason = Column(String(255), nullable=True)  # MISSING_CONTACT, INVALID_CONTACT, PROVIDER_UNAVAILABLE, PROVIDER_NOT_CONFIGURED

    # Recipient & Student Association
    student_id = Column(Integer, ForeignKey("students.id", ondelete="SET NULL"), nullable=True, index=True)
    guardian_name = Column(String(200), nullable=True)
    guardian_phone = Column(String(50), nullable=True)
    guardian_email = Column(String(255), nullable=True)
    guardian_relationship = Column(String(50), nullable=True)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="SET NULL"), nullable=True, index=True)
    academic_year = Column(String(50), nullable=True)

    # Related Entities Linkage
    related_attendance_id = Column(Integer, ForeignKey("attendances.id", ondelete="SET NULL"), nullable=True)
    related_exam_id = Column(Integer, ForeignKey("exams.id", ondelete="SET NULL"), nullable=True)
    related_result_id = Column(Integer, ForeignKey("exam_results.id", ondelete="SET NULL"), nullable=True)
    related_release_batch_id = Column(Integer, ForeignKey("result_release_batches.id", ondelete="SET NULL"), nullable=True)

    # Idempotency / Deduplication Unique Key
    idempotency_key = Column(String(255), unique=True, nullable=True, index=True)

    # Audit & Delivery Metadata
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    attempt_count = Column(Integer, default=0, nullable=False)
    extra_data = Column(JSON, nullable=True)

    # Relationships
    student = relationship("Student", foreign_keys=[student_id], lazy="joined")
    school_class = relationship("SchoolClass", foreign_keys=[class_id], lazy="joined")
    created_by = relationship("User", foreign_keys=[created_by_id])
    deliveries = relationship("NotificationDelivery", back_populates="notification", cascade="all, delete-orphan", lazy="selectin")
    attendance = relationship("Attendance", foreign_keys=[related_attendance_id])
    exam = relationship("Exam", foreign_keys=[related_exam_id])
    result = relationship("ExamResult", foreign_keys=[related_result_id])
    release_batch = relationship("ResultReleaseBatch", foreign_keys=[related_release_batch_id])

    @property
    def student_name(self) -> str:
        return self.student.full_name if self.student else ""

    @property
    def student_admission_number(self) -> str:
        return self.student.admission_number if self.student else ""

    @property
    def class_name(self) -> str:
        return self.school_class.name if self.school_class else ""

    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, type='{self.notification_type}', status='{self.status}', recipient='{self.guardian_phone or self.guardian_email}')>"


class NotificationDelivery(Base):
    """Specific delivery attempt per channel for a notification."""
    __tablename__ = "notification_deliveries"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    notification_id = Column(Integer, ForeignKey("notifications.id", ondelete="CASCADE"), nullable=False, index=True)
    channel = Column(String(50), nullable=False)
    recipient = Column(String(255), nullable=False)
    provider_name = Column(String(100), nullable=True)
    provider_message_id = Column(String(255), nullable=True)
    status = Column(String(50), default="PENDING", nullable=False, index=True)
    error_code = Column(String(100), nullable=True)
    error_message = Column(Text, nullable=True)
    attempt_number = Column(Integer, default=1, nullable=False)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    notification = relationship("Notification", back_populates="deliveries")

    def __repr__(self) -> str:
        return f"<NotificationDelivery(id={self.id}, notification_id={self.notification_id}, channel='{self.channel}', status='{self.status}')>"
