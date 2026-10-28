from datetime import datetime, date, timezone
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_, and_, desc
from app.models.notification import Notification, NotificationDelivery, NotificationTemplate
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.models.school_class import SchoolClass


class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, notification_id: int) -> Optional[Notification]:
        return (
            self.db.query(Notification)
            .options(
                joinedload(Notification.student),
                joinedload(Notification.school_class),
                joinedload(Notification.deliveries),
                joinedload(Notification.created_by),
            )
            .filter(Notification.id == notification_id)
            .first()
        )

    def get_by_idempotency_key(self, key: str) -> Optional[Notification]:
        if not key:
            return None
        return (
            self.db.query(Notification)
            .filter(Notification.idempotency_key == key)
            .first()
        )

    def get_paginated(
        self,
        page: int = 1,
        limit: int = 20,
        status: Optional[str] = None,
        notification_type: Optional[str] = None,
        channel: Optional[str] = None,
        class_id: Optional[int] = None,
        student_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        search: Optional[str] = None,
        academic_year: Optional[str] = None,
    ) -> Tuple[List[Notification], int]:
        query = (
            self.db.query(Notification)
            .outerjoin(Student, Notification.student_id == Student.id)
            .outerjoin(SchoolClass, Notification.class_id == SchoolClass.id)
            .options(
                joinedload(Notification.student),
                joinedload(Notification.school_class),
            )
        )

        if status and status.upper() != "ALL":
            query = query.filter(Notification.status == status.upper())

        if notification_type and notification_type.upper() != "ALL":
            query = query.filter(Notification.notification_type == notification_type.upper())

        if channel and channel.upper() != "ALL":
            query = query.filter(Notification.channel == channel.upper())

        if class_id:
            query = query.filter(Notification.class_id == class_id)

        if student_id:
            query = query.filter(Notification.student_id == student_id)

        if academic_year:
            query = query.filter(Notification.academic_year == academic_year)

        if start_date:
            start_dt = datetime.combine(start_date, datetime.min.time(), tzinfo=timezone.utc)
            query = query.filter(Notification.created_at >= start_dt)

        if end_date:
            end_dt = datetime.combine(end_date, datetime.max.time(), tzinfo=timezone.utc)
            query = query.filter(Notification.created_at <= end_dt)

        if search and search.strip():
            s = f"%{search.strip()}%"
            # Support search by notification ID if numeric
            id_filter = None
            if search.strip().isdigit():
                id_filter = (Notification.id == int(search.strip()))

            text_filter = or_(
                Notification.title.ilike(s),
                Notification.message.ilike(s),
                Notification.guardian_name.ilike(s),
                Notification.guardian_phone.ilike(s),
                Notification.guardian_email.ilike(s),
                Student.first_name.ilike(s),
                Student.last_name.ilike(s),
                Student.admission_number.ilike(s),
            )
            if id_filter is not None:
                query = query.filter(or_(id_filter, text_filter))
            else:
                query = query.filter(text_filter)

        total = query.count()
        offset = (page - 1) * limit
        items = query.order_by(desc(Notification.created_at)).offset(offset).limit(limit).all()

        return items, total

    def get_summary_stats(self) -> Dict[str, Any]:
        today_start = datetime.combine(date.today(), datetime.min.time(), tzinfo=timezone.utc)

        total_notifications = self.db.query(func.count(Notification.id)).scalar() or 0
        delivered_count = self.db.query(func.count(Notification.id)).filter(Notification.status == "DELIVERED").scalar() or 0
        pending_count = self.db.query(func.count(Notification.id)).filter(Notification.status.in_(["PENDING", "QUEUED", "SENT"])).scalar() or 0
        failed_count = self.db.query(func.count(Notification.id)).filter(Notification.status == "FAILED").scalar() or 0
        not_sent_count = self.db.query(func.count(Notification.id)).filter(Notification.status == "NOT_SENT").scalar() or 0
        not_configured_count = self.db.query(func.count(Notification.id)).filter(Notification.status == "NOT_CONFIGURED").scalar() or 0
        read_count = self.db.query(func.count(Notification.id)).filter(Notification.status == "READ").scalar() or 0

        sms_count = self.db.query(func.count(Notification.id)).filter(Notification.channel == "SMS").scalar() or 0
        email_count = self.db.query(func.count(Notification.id)).filter(Notification.channel == "EMAIL").scalar() or 0
        in_app_count = self.db.query(func.count(Notification.id)).filter(Notification.channel == "IN_APP").scalar() or 0

        today_count = self.db.query(func.count(Notification.id)).filter(Notification.created_at >= today_start).scalar() or 0

        # Count active students missing phone or guardian name
        missing_contact_students = self.db.query(func.count(Student.id)).filter(
            Student.status == "ACTIVE",
            or_(
                Student.guardian_phone.is_(None),
                Student.guardian_phone == "",
                Student.guardian_name.is_(None),
                Student.guardian_name == ""
            )
        ).scalar() or 0

        return {
            "total_notifications": total_notifications,
            "delivered_count": delivered_count,
            "pending_count": pending_count,
            "failed_count": failed_count,
            "not_sent_count": not_sent_count,
            "not_configured_count": not_configured_count,
            "read_count": read_count,
            "sms_count": sms_count,
            "email_count": email_count,
            "in_app_count": in_app_count,
            "today_count": today_count,
            "missing_contact_students": missing_contact_students,
        }

    def get_templates(self, active_only: bool = True) -> List[NotificationTemplate]:
        query = self.db.query(NotificationTemplate)
        if active_only:
            query = query.filter(NotificationTemplate.is_active.is_(True))
        return query.order_by(NotificationTemplate.category, NotificationTemplate.name).all()

    def get_template_by_code(self, code: str) -> Optional[NotificationTemplate]:
        return self.db.query(NotificationTemplate).filter(NotificationTemplate.code == code).first()

    def get_students_missing_contact(
        self,
        class_id: Optional[int] = None,
        academic_year: Optional[str] = None
    ) -> List[Student]:
        query = (
            self.db.query(Student)
            .filter(
                Student.status == "ACTIVE",
                or_(
                    Student.guardian_phone.is_(None),
                    Student.guardian_phone == "",
                    Student.guardian_email.is_(None),
                    Student.guardian_email == ""
                )
            )
        )
        if class_id:
            query = query.join(StudentEnrollment, Student.id == StudentEnrollment.student_id).filter(
                StudentEnrollment.class_id == class_id,
                StudentEnrollment.status == "ACTIVE"
            )
            if academic_year:
                query = query.filter(StudentEnrollment.academic_year == academic_year)

        return query.order_by(Student.last_name, Student.first_name).all()

    def create_notification(self, notification: Notification) -> Notification:
        self.db.add(notification)
        self.db.flush()
        return notification

    def create_delivery(self, delivery: NotificationDelivery) -> NotificationDelivery:
        self.db.add(delivery)
        self.db.flush()
        return delivery
