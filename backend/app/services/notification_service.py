import re
from datetime import datetime, date, timezone
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_, and_
from fastapi import HTTPException, status

from app.models.user import User
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.models.school_class import SchoolClass
from app.models.attendance import Attendance
from app.models.exam import Exam, ExamResult
from app.models.result_release import ResultReleaseBatch
from app.models.system_setting import SystemSetting
from app.models.notification import Notification, NotificationDelivery, NotificationTemplate
from app.repositories.notification_repo import NotificationRepository
from app.services.providers.sms_provider import SMSProvider
from app.services.providers.email_provider import EmailProvider
from app.services.providers.in_app_provider import InAppProvider
from app.schemas.notification import (
    SingleNotificationCreate,
    BulkNotificationCreate,
    BulkNotificationResponse,
    NotificationResponse,
    NotificationDetailResponse,
    NotificationListResponse,
    NotificationSummaryStats,
    NotificationCountersResponse,
    MissingContactsResponse,
    MissingContactStudentItem,
    ChannelConfigResponse,
    ChannelConfigItem,
    NotificationTemplateResponse,
    NotificationTemplateUpdate,
    AttendanceAlertsResponse,
    AttendanceAlertClassGroup,
    AttendanceAlertStudentItem,
    AttendanceAlertNotifyRequest,
    AttendanceAlertNotifyResponse,
    ResultAlertsResponse,
    ResultAlertGroup,
    ResultAlertStudentItem,
    ResultAlertNotifyRequest,
    ResultAlertNotifyResponse,
    MessagePreviewResponse,
    MessagePreviewItem,
)
from app.utils.logger import logger


DEFAULT_TEMPLATES = [
    {
        "code": "ATTENDANCE_ABSENT",
        "name": "Student Absence Alert (Somali)",
        "title_template": "Ogeysiis Maqnaansho - {{student_name}}",
        "body_template": "Asc {{guardian_name}}, waxaan ku ogeysiinaynaa in ardaygaaga {{student_name}} maanta uusan imaan dugsiga. Fadlan la soco xaalkiisa. — {{school_name}}",
        "category": "ATTENDANCE",
    },
    {
        "code": "RESULT_RELEASED",
        "name": "Exam Results Release Notice (Somali)",
        "title_template": "Natiijada Imtixaanka - {{student_name}}",
        "body_template": "Asc {{guardian_name}}, waxaan ku ogeysiinaynaa in natiijada {{student_name}} ee {{exam_name}} la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — {{school_name}}",
        "category": "EXAMS",
    },
    {
        "code": "FEE_REMINDER",
        "name": "Tuition & Fee Balance Reminder (Somali)",
        "title_template": "Xasuusin Lacagta Dugsiga - {{student_name}}",
        "body_template": "Asc {{guardian_name}}, waxaan ku xasuusinaynaa in ardaygaaga {{student_name}} uu leeyahay lacag dugsi oo dhan {{fee_balance}} oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — {{school_name}}",
        "category": "FINANCE",
    },
    {
        "code": "GENERAL_ANNOUNCEMENT",
        "name": "General School Announcement (Somali)",
        "title_template": "Ogeysiis Muhiim ah - {{school_name}}",
        "body_template": "Asc {{guardian_name}}, waxaa jira ogeysiis cusub oo ka yimid {{school_name}}. Fadlan gal Student Portal si aad u akhrido faahfaahinta ogeysiiska.",
        "category": "GENERAL",
    },
]


class NotificationService:
    """
    Centralized Notification Service for Education Management System.
    Enforces single source of truth in PostgreSQL, provider validation, idempotency,
    and automated triggers for attendance and result releases.
    """

    def __init__(self, db: Session):
        self.db = db
        self.repo = NotificationRepository(db)
        self.sms_provider = SMSProvider()
        self.email_provider = EmailProvider()
        self.in_app_provider = InAppProvider()
        self._ensure_default_templates()

    def _ensure_default_templates(self):
        """Seed or synchronize default Somali templates in PostgreSQL."""
        try:
            for tmpl in DEFAULT_TEMPLATES:
                existing = self.db.query(NotificationTemplate).filter(NotificationTemplate.code == tmpl["code"]).first()
                if not existing:
                    new_tmpl = NotificationTemplate(
                        code=tmpl["code"],
                        name=tmpl["name"],
                        title_template=tmpl["title_template"],
                        body_template=tmpl["body_template"],
                        category=tmpl["category"],
                        is_active=True,
                        is_system=True,
                    )
                    self.db.add(new_tmpl)
                else:
                    existing.name = tmpl["name"]
                    existing.title_template = tmpl["title_template"]
                    existing.body_template = tmpl["body_template"]
                    existing.category = tmpl["category"]
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.warning(f"Could not auto-seed notification templates: {e}")

    # =========================================================================
    # SETTINGS & CONFIGURATION
    # =========================================================================

    def get_setting(self, key: str, default: str = "true") -> str:
        s = self.db.query(SystemSetting).filter(SystemSetting.key == key).first()
        return s.value if s else default

    def set_setting(self, key: str, value: str, description: Optional[str] = None):
        s = self.db.query(SystemSetting).filter(SystemSetting.key == key).first()
        if s:
            s.value = value
            if description:
                s.description = description
        else:
            s = SystemSetting(key=key, value=value, description=description, is_public=False)
            self.db.add(s)
        self.db.commit()

    def get_notification_settings(self) -> Dict[str, Any]:
        return {
            "notify_attendance_absent_enabled": self.get_setting("notify_attendance_absent_enabled", "true").lower() in ("true", "1", "yes"),
            "notify_result_release_enabled": self.get_setting("notify_result_release_enabled", "true").lower() in ("true", "1", "yes"),
            "allow_manual_notifications": self.get_setting("allow_manual_notifications", "true").lower() in ("true", "1", "yes"),
            "default_channel": self.get_setting("notification_default_channel", "SMS"),
            "school_name": self.get_setting("school_name", "Education Management System"),
            "sms_sender_id": self.get_setting("sms_sender_id", "HAWLWADAAG"),
        }

    def update_notification_settings(self, settings_data: Dict[str, Any]) -> Dict[str, Any]:
        if "notify_attendance_absent_enabled" in settings_data:
            val = "true" if settings_data["notify_attendance_absent_enabled"] else "false"
            self.set_setting("notify_attendance_absent_enabled", val, "Automatic attendance absence SMS alerts")

        if "notify_result_release_enabled" in settings_data:
            val = "true" if settings_data["notify_result_release_enabled"] else "false"
            self.set_setting("notify_result_release_enabled", val, "Automatic result release SMS alerts")

        if "allow_manual_notifications" in settings_data:
            val = "true" if settings_data["allow_manual_notifications"] else "false"
            self.set_setting("allow_manual_notifications", val, "Allow manual admin guardian notifications")

        if "default_channel" in settings_data:
            self.set_setting("notification_default_channel", str(settings_data["default_channel"]), "Default notification channel")

        if "school_name" in settings_data:
            self.set_setting("school_name", str(settings_data["school_name"]), "School Name for branding")

        if "sms_sender_id" in settings_data:
            self.set_setting("sms_sender_id", str(settings_data["sms_sender_id"]), "SMS Sender ID header")

        return self.get_notification_settings()

    def get_channel_configs(self) -> ChannelConfigResponse:
        return ChannelConfigResponse(
            channels=[
                ChannelConfigItem(**self.sms_provider.get_status_info()),
                ChannelConfigItem(**self.email_provider.get_status_info()),
                ChannelConfigItem(**self.in_app_provider.get_status_info()),
            ]
        )

    def update_template(self, code: str, data: NotificationTemplateUpdate) -> NotificationTemplate:
        tmpl = self.repo.get_template_by_code(code)
        if not tmpl:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template '{code}' not found."
            )
        if data.name is not None:
            tmpl.name = data.name
        if data.title_template is not None:
            tmpl.title_template = data.title_template
        if data.body_template is not None:
            tmpl.body_template = data.body_template
        if data.is_active is not None:
            tmpl.is_active = data.is_active

        self.db.commit()
        return tmpl

    # =========================================================================
    # TEMPLATE ENGINE & COUNTERS
    # =========================================================================

    def render_template(
        self,
        template_str: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Safely replace supported placeholders:
        {{student_name}}, {{guardian_name}}, {{class_name}}, {{exam_name}}, {{date}}, {{school_name}}, {{academic_year}}, {{message}}
        """
        result = template_str
        for key, val in context.items():
            placeholder = f"{{{{{key}}}}}"
            result = result.replace(placeholder, str(val) if val is not None else "")
        return result

    def _resolve_student_fee_balance(self, student_id: int) -> str:
        """Calculate outstanding student fee balance from PostgreSQL."""
        try:
            from app.models.fee import StudentFee
            fees = self.db.query(StudentFee).filter(
                StudentFee.student_id == student_id,
                StudentFee.status.in_(["PENDING", "PARTIALLY_PAID", "OVERDUE"])
            ).all()
            total_bal = sum(f.balance_remaining for f in fees)
            if total_bal > 0:
                return f"${total_bal:,.2f}"
            return "$0.00"
        except Exception:
            return "$0.00"

    def _validate_phone_number(self, phone: Optional[str]) -> bool:
        if not phone:
            return False
        return self.sms_provider.normalize_phone(phone) is not None

    def get_notification_counters(self) -> NotificationCountersResponse:
        today = date.today()
        # 1. Unnotified absent students today
        today_absents = self.db.query(Attendance).filter(
            Attendance.date == today,
            Attendance.status == "ABSENT"
        ).all()

        unnotified_absent = 0
        for att in today_absents:
            key = f"attendance:{att.id}:student:{att.student_id}:date:{att.date.isoformat()}"
            if not self.repo.get_by_idempotency_key(key):
                unnotified_absent += 1

        # 2. Unnotified released results
        released_batches = self.db.query(ResultReleaseBatch).filter(ResultReleaseBatch.status == "RELEASED").all()
        unnotified_results = 0
        for b in released_batches:
            results = self.db.query(ExamResult.student_id).filter(
                ExamResult.release_batch_id == b.id,
                ExamResult.status == "RELEASED"
            ).distinct().all()
            for r in results:
                key = f"result_release:{r[0]}:batch:{b.id}"
                if not self.repo.get_by_idempotency_key(key):
                    unnotified_results += 1

        # 3. Aggregated counts
        total_failed = self.db.query(func.count(Notification.id)).filter(Notification.status == "FAILED").scalar() or 0
        total_pending = self.db.query(func.count(Notification.id)).filter(Notification.status.in_(["PENDING", "QUEUED", "NOT_CONFIGURED"])).scalar() or 0
        total_delivered = self.db.query(func.count(Notification.id)).filter(Notification.status.in_(["DELIVERED", "SENT"])).scalar() or 0
        total_all = self.db.query(func.count(Notification.id)).scalar() or 0

        return NotificationCountersResponse(
            new_attendance_absent_count=unnotified_absent,
            new_result_release_count=unnotified_results,
            total_failed_count=total_failed,
            total_pending_count=total_pending,
            total_delivered_count=total_delivered,
            total_notifications=total_all,
        )

    # =========================================================================
    # CORE NOTIFICATION DISPATCH
    # =========================================================================

    def _dispatch_channel(
        self,
        notification: Notification,
        recipient: str,
    ) -> NotificationDelivery:
        """Dispatch via appropriate provider and record delivery attempt."""
        channel = notification.channel.upper()
        now = datetime.now(timezone.utc)
        
        # If channel is SMS, normalize recipient phone number
        dispatch_recipient = recipient
        if channel == "SMS":
            norm = self.sms_provider.normalize_phone(recipient)
            if norm:
                dispatch_recipient = norm

        delivery = NotificationDelivery(
            notification_id=notification.id,
            channel=channel,
            recipient=dispatch_recipient,
            attempt_number=notification.attempt_count + 1,
            created_at=now,
        )

        notification.attempt_count += 1

        # Prepare extra data including unique reference ID
        extra_data = notification.extra_data.copy() if notification.extra_data else {}
        extra_data.setdefault("refid", f"HAWL-NOTIF-{notification.id}")
        extra_data.setdefault("notification_id", notification.id)

        if channel == "SMS":
            result = self.sms_provider.send(
                recipient=dispatch_recipient,
                message=notification.message,
                title=notification.title,
                extra_data=extra_data,
            )
        elif channel == "EMAIL":
            result = self.email_provider.send(
                recipient=recipient,
                message=notification.message,
                title=notification.title,
                extra_data=extra_data,
            )
        elif channel == "IN_APP":
            result = self.in_app_provider.send(
                recipient=recipient,
                message=notification.message,
                title=notification.title,
                extra_data=extra_data,
            )
        else:
            from app.services.providers.base_provider import DeliveryResult
            result = DeliveryResult(
                status="FAILED",
                provider_name="Unknown",
                error_code="UNSUPPORTED_CHANNEL",
                error_message=f"Channel {channel} is not supported.",
            )

        delivery.status = result.status
        delivery.provider_name = result.provider_name
        delivery.provider_message_id = result.provider_message_id
        delivery.error_code = result.error_code
        delivery.error_message = result.error_message
        delivery.sent_at = result.sent_at
        delivery.delivered_at = result.delivered_at

        # Update notification overall status based on delivery outcome
        notification.status = result.status
        if result.status == "DELIVERED":
            notification.delivered_at = result.delivered_at or now
            notification.sent_at = result.sent_at or now
            notification.failure_reason = None
        elif result.status == "SENT":
            notification.sent_at = result.sent_at or now
            notification.failure_reason = None
        elif result.status == "NOT_CONFIGURED":
            notification.failure_reason = "PROVIDER_NOT_CONFIGURED"
        elif result.status == "FAILED":
            notification.failure_reason = result.error_code or "DISPATCH_FAILED"

        self.db.add(delivery)
        self.db.flush()
        return delivery

    # =========================================================================
    # HORMUUD SMS PROVIDER METHODS
    # =========================================================================

    def get_hormuud_status(self) -> Dict[str, Any]:
        """Return safe status metadata for Hormuud SMS Gateway."""
        return self.sms_provider.get_status_info()

    def test_hormuud_connection(self) -> Dict[str, Any]:
        """Run safe connection diagnostics with Hormuud SMS API."""
        return self.sms_provider.test_connection()

    def get_hormuud_balance(self) -> Dict[str, Any]:
        """Query account balance from Hormuud SMS API."""
        return self.sms_provider.check_balance()

    def get_hormuud_delivery(self, message_id: str, ref_id: Optional[str] = None) -> Dict[str, Any]:
        """Query delivery status directly from Hormuud (POST /api/GetDelivery)."""
        return self.sms_provider.get_delivery(message_id=message_id, ref_id=ref_id)

    def handle_hormuud_delivery_report(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming delivery webhook callback from Hormuud."""
        parsed = self.sms_provider.process_delivery_report(payload)
        ref_id = parsed.get("ref_id")
        msg_id = parsed.get("provider_message_id")
        mapped_status = parsed.get("mapped_status", "SENT")
        delivered_at = parsed.get("delivered_at")
        err_msg = parsed.get("error_message")

        delivery = None
        if msg_id:
            delivery = self.db.query(NotificationDelivery).filter(
                NotificationDelivery.provider_message_id == str(msg_id)
            ).first()

        if not delivery and ref_id:
            if str(ref_id).startswith("HAWL-NOTIF-"):
                try:
                    notif_id = int(str(ref_id).replace("HAWL-NOTIF-", ""))
                    delivery = self.db.query(NotificationDelivery).filter(
                        NotificationDelivery.notification_id == notif_id
                    ).order_by(NotificationDelivery.id.desc()).first()
                except Exception:
                    pass

            if not delivery:
                delivery = self.db.query(NotificationDelivery).filter(
                    NotificationDelivery.provider_message_id == str(ref_id)
                ).first()

        if delivery:
            delivery.status = mapped_status
            if mapped_status == "DELIVERED":
                delivery.delivered_at = delivered_at or datetime.now(timezone.utc)
                delivery.error_message = None
            elif mapped_status == "FAILED":
                delivery.error_message = err_msg or "Hormuud reported delivery failure."

            notif = delivery.notification
            if notif:
                notif.status = mapped_status
                if mapped_status == "DELIVERED":
                    notif.delivered_at = delivery.delivered_at
                    notif.failure_reason = None
                elif mapped_status == "FAILED":
                    notif.failure_reason = delivery.error_message or "PROVIDER_DELIVERY_FAILED"

            self.db.commit()
            return {
                "success": True,
                "matched": True,
                "notification_id": delivery.notification_id,
                "status": mapped_status,
                "message": f"Updated delivery status for notification {delivery.notification_id} to {mapped_status}."
            }

        return {
            "success": True,
            "matched": False,
            "status": mapped_status,
            "message": f"Webhook received for msg_id '{msg_id}' / ref_id '{ref_id}' but no matching delivery record was found."
        }

    # =========================================================================
    # ATTENDANCE ALERTS CENTER
    # =========================================================================

    def get_attendance_alerts(self, target_date: Optional[date] = None) -> AttendanceAlertsResponse:
        t_date = target_date or date.today()
        school_name = self.get_setting("school_name", "Education Management System")
        tmpl = self.repo.get_template_by_code("ATTENDANCE_ABSENT")
        body_tmpl = tmpl.body_template if tmpl else "Asc {{guardian_name}}, ardaygaaga {{student_name}} maanta ma uusan imaan dugsiga. Fadlan la soco xaalkiisa. — {{school_name}}"

        # Fetch all absent attendance records for date
        records = (
            self.db.query(Attendance)
            .options(
                joinedload(Attendance.student),
                joinedload(Attendance.school_class),
                joinedload(Attendance.subject),
            )
            .filter(
                Attendance.date == t_date,
                Attendance.status == "ABSENT"
            )
            .order_by(Attendance.class_id, Attendance.student_id)
            .all()
        )

        total_absent = len(records)
        total_unnotified = 0
        total_notified = 0
        total_missing = 0

        # Group by Class
        class_map: Dict[int, Dict[str, Any]] = {}

        for rec in records:
            c_id = rec.class_id
            if c_id not in class_map:
                c_name = rec.school_class.name if rec.school_class else f"Class {c_id}"
                c_code = rec.school_class.code if rec.school_class else f"C-{c_id}"
                class_map[c_id] = {
                    "class_id": c_id,
                    "class_name": c_name,
                    "class_code": c_code,
                    "students": [],
                    "total_absent": 0,
                    "unnotified_count": 0,
                    "missing_contact_count": 0,
                }

            student = rec.student
            has_phone = bool(student and student.guardian_phone and student.guardian_phone.strip())
            has_email = bool(student and student.guardian_email and student.guardian_email.strip())
            has_contact = has_phone or has_email

            # Check idempotency / notification status
            idempotency_key = f"attendance:{rec.id}:student:{rec.student_id}:date:{rec.date.isoformat()}"
            existing_notif = self.repo.get_by_idempotency_key(idempotency_key)
            
            # Also check legacy key format
            if not existing_notif:
                legacy_key = f"ATT_ABSENT_{rec.student_id}_{rec.date.isoformat()}_{rec.period or 0}_{rec.subject_id}"
                existing_notif = self.repo.get_by_idempotency_key(legacy_key)

            is_notified = existing_notif is not None
            notif_status = existing_notif.status if existing_notif else None

            if is_notified:
                total_notified += 1
            else:
                total_unnotified += 1
                class_map[c_id]["unnotified_count"] += 1

            if not has_contact:
                total_missing += 1
                class_map[c_id]["missing_contact_count"] += 1

            class_map[c_id]["total_absent"] += 1

            # Generate personalized message preview
            context = {
                "guardian_name": student.guardian_name if student and student.guardian_name else "Waalidka",
                "student_name": student.full_name if student else "Ardayga",
                "class_name": rec.school_class.name if rec.school_class else "",
                "date": rec.date.isoformat(),
                "school_name": school_name,
            }
            preview_msg = self.render_template(body_tmpl, context)

            student_item = AttendanceAlertStudentItem(
                attendance_id=rec.id,
                student_id=rec.student_id,
                student_name=student.full_name if student else f"Student #{rec.student_id}",
                admission_number=student.admission_number if student else "N/A",
                class_id=c_id,
                class_name=rec.school_class.name if rec.school_class else "",
                date=rec.date.isoformat(),
                period=str(rec.period) if rec.period else None,
                subject_name=rec.subject.name if rec.subject else None,
                guardian_name=student.guardian_name if student else None,
                guardian_phone=student.guardian_phone if student else None,
                guardian_email=student.guardian_email if student else None,
                guardian_relationship=student.guardian_relationship if student else "Guardian",
                has_contact=has_contact,
                is_notified=is_notified,
                notification_status=notif_status,
                personalized_preview=preview_msg,
            )
            class_map[c_id]["students"].append(student_item)

        class_groups = [
            AttendanceAlertClassGroup(
                class_id=grp["class_id"],
                class_name=grp["class_name"],
                class_code=grp["class_code"],
                total_absent=grp["total_absent"],
                unnotified_count=grp["unnotified_count"],
                missing_contact_count=grp["missing_contact_count"],
                students=grp["students"],
            )
            for grp in class_map.values()
        ]

        return AttendanceAlertsResponse(
            date=t_date.isoformat(),
            total_absent_students=total_absent,
            total_unnotified=total_unnotified,
            total_notified=total_notified,
            total_missing_contacts=total_missing,
            classes=class_groups,
        )

    def preview_attendance_alerts(self, payload: AttendanceAlertNotifyRequest) -> MessagePreviewResponse:
        t_date = date.fromisoformat(payload.date) if payload.date else date.today()
        school_name = self.get_setting("school_name", "Education Management System")
        tmpl = self.repo.get_template_by_code("ATTENDANCE_ABSENT")
        body_tmpl = payload.custom_message_template or (tmpl.body_template if tmpl else "Asc {{guardian_name}}, ardaygaaga {{student_name}} maanta ma uusan imaan dugsiga. Fadlan la soco xaalkiisa. — {{school_name}}")
        title_tmpl = tmpl.title_template if tmpl else "Hawlwadaag School: Maqnaansho Arday"

        q = self.db.query(Attendance).options(
            joinedload(Attendance.student),
            joinedload(Attendance.school_class)
        ).filter(
            Attendance.date == t_date,
            Attendance.status == "ABSENT"
        )

        if payload.target_type == "CLASS" and payload.class_id:
            q = q.filter(Attendance.class_id == payload.class_id)
        elif payload.target_type == "SELECTED_ATTENDANCES" and payload.attendance_ids:
            q = q.filter(Attendance.id.in_(payload.attendance_ids))

        records = q.all()
        previews = []
        valid_count = 0
        missing_count = 0
        already_notified = 0

        for rec in records:
            student = rec.student
            has_phone = bool(student and student.guardian_phone and student.guardian_phone.strip())
            recipient = student.guardian_phone if student and student.guardian_phone else "Missing Contact"
            if has_phone:
                valid_count += 1
            else:
                missing_count += 1

            idempotency_key = f"attendance:{rec.id}:student:{rec.student_id}:date:{rec.date.isoformat()}"
            is_done = self.repo.get_by_idempotency_key(idempotency_key) is not None
            if is_done:
                already_notified += 1

            context = {
                "guardian_name": student.guardian_name if student and student.guardian_name else "Waalidka",
                "student_name": student.full_name if student else "Ardayga",
                "class_name": rec.school_class.name if rec.school_class else "",
                "date": rec.date.isoformat(),
                "school_name": school_name,
            }
            rendered_msg = self.render_template(body_tmpl, context)
            rendered_title = self.render_template(title_tmpl, context)

            previews.append(
                MessagePreviewItem(
                    student_id=rec.student_id,
                    student_name=student.full_name if student else f"Student #{rec.student_id}",
                    guardian_name=student.guardian_name if student and student.guardian_name else "Guardian",
                    recipient_contact=recipient,
                    channel=payload.channel.upper(),
                    title=rendered_title,
                    message=rendered_msg,
                    has_contact=has_phone,
                    is_already_notified=is_done,
                )
            )

        return MessagePreviewResponse(
            total_recipients=len(records),
            valid_contacts_count=valid_count,
            missing_contacts_count=missing_count,
            already_notified_count=already_notified,
            previews=previews,
        )

    def notify_attendance_alerts(
        self,
        admin_user: User,
        payload: AttendanceAlertNotifyRequest
    ) -> AttendanceAlertNotifyResponse:
        t_date = date.fromisoformat(payload.date) if payload.date else date.today()
        school_name = self.get_setting("school_name", "Education Management System")
        tmpl = self.repo.get_template_by_code("ATTENDANCE_ABSENT")
        body_tmpl = payload.custom_message_template or (tmpl.body_template if tmpl else "Asc {{guardian_name}}, ardaygaaga {{student_name}} maanta ma uusan imaan dugsiga. Fadlan la soco xaalkiisa. — {{school_name}}")
        title_tmpl = tmpl.title_template if tmpl else "Hawlwadaag School: Maqnaansho Arday"

        q = self.db.query(Attendance).options(
            joinedload(Attendance.student),
            joinedload(Attendance.school_class)
        ).filter(
            Attendance.date == t_date,
            Attendance.status == "ABSENT"
        )

        if payload.target_type == "CLASS" and payload.class_id:
            q = q.filter(Attendance.class_id == payload.class_id)
        elif payload.target_type == "SELECTED_ATTENDANCES" and payload.attendance_ids:
            q = q.filter(Attendance.id.in_(payload.attendance_ids))

        records = q.all()
        total_targeted = len(records)
        sent_or_queued = 0
        already_notified = 0
        missing_contacts = 0
        failed_count = 0
        now = datetime.now(timezone.utc)
        channel = payload.channel.upper()

        for rec in records:
            idempotency_key = f"attendance:{rec.id}:student:{rec.student_id}:date:{rec.date.isoformat()}"
            if self.repo.get_by_idempotency_key(idempotency_key):
                already_notified += 1
                continue

            student = rec.student
            if not student:
                continue

            context = {
                "guardian_name": student.guardian_name or "Waalidka",
                "student_name": student.full_name,
                "class_name": rec.school_class.name if rec.school_class else "",
                "date": rec.date.isoformat(),
                "school_name": school_name,
            }
            rendered_title = self.render_template(title_tmpl, context)
            rendered_body = self.render_template(body_tmpl, context)

            notif = Notification(
                notification_type="ATTENDANCE_ABSENT",
                title=rendered_title,
                message=rendered_body,
                channel=channel,
                student_id=student.id,
                guardian_name=student.guardian_name or "Parent/Guardian",
                guardian_phone=student.guardian_phone,
                guardian_email=student.guardian_email,
                guardian_relationship=student.guardian_relationship or "Guardian",
                class_id=rec.class_id,
                academic_year=rec.academic_year,
                related_attendance_id=rec.id,
                idempotency_key=idempotency_key,
                created_by_id=admin_user.id,
                created_at=now,
                attempt_count=0,
            )

            if not student.guardian_phone or not student.guardian_phone.strip():
                notif.status = "NOT_SENT"
                notif.failure_reason = "MISSING_CONTACT"
                self.db.add(notif)
                missing_contacts += 1
            elif not self._validate_phone_number(student.guardian_phone):
                notif.status = "FAILED"
                notif.failure_reason = "INVALID_CONTACT"
                self.db.add(notif)
                failed_count += 1
            else:
                self.db.add(notif)
                self.db.flush()
                self._dispatch_channel(notif, student.guardian_phone)
                sent_or_queued += 1

        self.db.commit()

        msg = f"Processed {total_targeted} records. {sent_or_queued} sent/queued, {already_notified} already notified, {missing_contacts} missing contact."
        return AttendanceAlertNotifyResponse(
            success=True,
            message=msg,
            total_targeted=total_targeted,
            sent_or_queued_count=sent_or_queued,
            already_notified_count=already_notified,
            missing_contact_count=missing_contacts,
            failed_count=failed_count,
        )

    # =========================================================================
    # RESULT RELEASE ALERTS CENTER
    # =========================================================================

    def get_result_alerts(self, academic_year: Optional[str] = None) -> ResultAlertsResponse:
        school_name = self.get_setting("school_name", "Education Management System")
        tmpl = self.repo.get_template_by_code("RESULT_RELEASED")
        body_tmpl = tmpl.body_template if tmpl else "Asc {{guardian_name}}, natiijada {{student_name}} ee {{exam_name}} waa la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — {{school_name}}"

        q = self.db.query(ResultReleaseBatch).options(
            joinedload(ResultReleaseBatch.school_class)
        ).filter(ResultReleaseBatch.status == "RELEASED")

        if academic_year:
            q = q.filter(ResultReleaseBatch.academic_year == academic_year)

        batches = q.order_by(ResultReleaseBatch.id.desc()).all()
        groups = []
        total_unnotified_results = 0

        for b in batches:
            results = (
                self.db.query(ExamResult)
                .options(joinedload(ExamResult.student))
                .filter(
                    ExamResult.release_batch_id == b.id,
                    ExamResult.status == "RELEASED"
                )
                .all()
            )

            # Deduplicate by student
            seen_students = set()
            student_items = []
            batch_unnotified = 0

            for res in results:
                if res.student_id in seen_students:
                    continue
                seen_students.add(res.student_id)

                student = res.student
                has_phone = bool(student and student.guardian_phone and student.guardian_phone.strip())
                idempotency_key = f"result_release:{res.student_id}:batch:{b.id}"
                is_notified = self.repo.get_by_idempotency_key(idempotency_key) is not None

                if not is_notified:
                    batch_unnotified += 1
                    total_unnotified_results += 1

                context = {
                    "guardian_name": student.guardian_name if student and student.guardian_name else "Waalidka",
                    "student_name": student.full_name if student else "Ardayga",
                    "class_name": b.school_class.name if b.school_class else "",
                    "exam_name": b.exam_name,
                    "academic_year": b.academic_year,
                    "school_name": school_name,
                }
                preview_msg = self.render_template(body_tmpl, context)

                student_items.append(
                    ResultAlertStudentItem(
                        result_id=res.id,
                        student_id=res.student_id,
                        student_name=student.full_name if student else f"Student #{res.student_id}",
                        admission_number=student.admission_number if student else "N/A",
                        class_id=b.class_id,
                        class_name=b.school_class.name if b.school_class else "",
                        exam_name=b.exam_name,
                        academic_year=b.academic_year,
                        guardian_name=student.guardian_name if student else None,
                        guardian_phone=student.guardian_phone if student else None,
                        has_contact=has_phone,
                        is_notified=is_notified,
                        personalized_preview=preview_msg,
                    )
                )

            groups.append(
                ResultAlertGroup(
                    release_batch_id=b.id,
                    batch_code=b.batch_code,
                    exam_name=b.exam_name,
                    academic_year=b.academic_year,
                    class_id=b.class_id,
                    class_name=b.school_class.name if b.school_class else "",
                    released_at=b.released_at.isoformat() if b.released_at else b.created_at.isoformat(),
                    total_students=len(seen_students),
                    unnotified_count=batch_unnotified,
                    students=student_items,
                )
            )

        return ResultAlertsResponse(
            total_unnotified_results=total_unnotified_results,
            groups=groups,
        )

    def preview_result_alerts(self, payload: ResultAlertNotifyRequest) -> MessagePreviewResponse:
        school_name = self.get_setting("school_name", "Education Management System")
        tmpl = self.repo.get_template_by_code("RESULT_RELEASED")
        body_tmpl = payload.custom_message_template or (tmpl.body_template if tmpl else "Asc {{guardian_name}}, natiijada {{student_name}} ee {{exam_name}} waa la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — {{school_name}}")
        title_tmpl = tmpl.title_template if tmpl else "Hawlwadaag School: Natiijada Imtixaanka"

        q = self.db.query(ResultReleaseBatch).options(
            joinedload(ResultReleaseBatch.school_class)
        ).filter(ResultReleaseBatch.status == "RELEASED")

        if payload.release_batch_id:
            q = q.filter(ResultReleaseBatch.id == payload.release_batch_id)

        batches = q.all()
        previews = []
        valid_count = 0
        missing_count = 0
        already_notified = 0

        for b in batches:
            results_q = self.db.query(ExamResult).options(joinedload(ExamResult.student)).filter(
                ExamResult.release_batch_id == b.id,
                ExamResult.status == "RELEASED"
            )
            if payload.student_ids:
                results_q = results_q.filter(ExamResult.student_id.in_(payload.student_ids))

            results = results_q.all()
            seen_students = set()

            for res in results:
                if res.student_id in seen_students:
                    continue
                seen_students.add(res.student_id)

                student = res.student
                has_phone = bool(student and student.guardian_phone and student.guardian_phone.strip())
                recipient = student.guardian_phone if has_phone else "Missing Contact"
                if has_phone:
                    valid_count += 1
                else:
                    missing_count += 1

                idempotency_key = f"result_release:{res.student_id}:batch:{b.id}"
                is_done = self.repo.get_by_idempotency_key(idempotency_key) is not None
                if is_done:
                    already_notified += 1

                context = {
                    "guardian_name": student.guardian_name if student and student.guardian_name else "Waalidka",
                    "student_name": student.full_name if student else "Ardayga",
                    "class_name": b.school_class.name if b.school_class else "",
                    "exam_name": b.exam_name,
                    "academic_year": b.academic_year,
                    "school_name": school_name,
                }
                rendered_msg = self.render_template(body_tmpl, context)
                rendered_title = self.render_template(title_tmpl, context)

                previews.append(
                    MessagePreviewItem(
                        student_id=res.student_id,
                        student_name=student.full_name if student else f"Student #{res.student_id}",
                        guardian_name=student.guardian_name if student and student.guardian_name else "Guardian",
                        recipient_contact=recipient,
                        channel=payload.channel.upper(),
                        title=rendered_title,
                        message=rendered_msg,
                        has_contact=has_phone,
                        is_already_notified=is_done,
                    )
                )

        return MessagePreviewResponse(
            total_recipients=len(previews),
            valid_contacts_count=valid_count,
            missing_contacts_count=missing_count,
            already_notified_count=already_notified,
            previews=previews,
        )

    def notify_result_alerts(
        self,
        admin_user: User,
        payload: ResultAlertNotifyRequest
    ) -> ResultAlertNotifyResponse:
        school_name = self.get_setting("school_name", "Education Management System")
        tmpl = self.repo.get_template_by_code("RESULT_RELEASED")
        body_tmpl = payload.custom_message_template or (tmpl.body_template if tmpl else "Asc {{guardian_name}}, natiijada {{student_name}} ee {{exam_name}} waa la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — {{school_name}}")
        title_tmpl = tmpl.title_template if tmpl else "Hawlwadaag School: Natiijada Imtixaanka"

        q = self.db.query(ResultReleaseBatch).options(
            joinedload(ResultReleaseBatch.school_class)
        ).filter(ResultReleaseBatch.status == "RELEASED")

        if payload.release_batch_id:
            q = q.filter(ResultReleaseBatch.id == payload.release_batch_id)

        batches = q.all()
        total_targeted = 0
        sent_or_queued = 0
        already_notified = 0
        missing_contacts = 0
        failed_count = 0
        now = datetime.now(timezone.utc)
        channel = payload.channel.upper()

        for b in batches:
            results_q = self.db.query(ExamResult).options(joinedload(ExamResult.student)).filter(
                ExamResult.release_batch_id == b.id,
                ExamResult.status == "RELEASED"
            )
            if payload.student_ids:
                results_q = results_q.filter(ExamResult.student_id.in_(payload.student_ids))

            results = results_q.all()
            seen_students = set()

            for res in results:
                if res.student_id in seen_students:
                    continue
                seen_students.add(res.student_id)
                total_targeted += 1

                idempotency_key = f"result_release:{res.student_id}:batch:{b.id}"
                if self.repo.get_by_idempotency_key(idempotency_key):
                    already_notified += 1
                    continue

                student = res.student
                if not student:
                    continue

                context = {
                    "guardian_name": student.guardian_name or "Waalidka",
                    "student_name": student.full_name,
                    "class_name": b.school_class.name if b.school_class else "",
                    "exam_name": b.exam_name,
                    "academic_year": b.academic_year,
                    "school_name": school_name,
                }
                rendered_title = self.render_template(title_tmpl, context)
                rendered_body = self.render_template(body_tmpl, context)

                notif = Notification(
                    notification_type="RESULT_RELEASED",
                    title=rendered_title,
                    message=rendered_body,
                    channel=channel,
                    student_id=student.id,
                    guardian_name=student.guardian_name or "Parent/Guardian",
                    guardian_phone=student.guardian_phone,
                    guardian_email=student.guardian_email,
                    guardian_relationship=student.guardian_relationship or "Guardian",
                    class_id=b.class_id,
                    academic_year=b.academic_year,
                    related_release_batch_id=b.id,
                    idempotency_key=idempotency_key,
                    created_by_id=admin_user.id,
                    created_at=now,
                    attempt_count=0,
                )

                if not student.guardian_phone or not student.guardian_phone.strip():
                    notif.status = "NOT_SENT"
                    notif.failure_reason = "MISSING_CONTACT"
                    self.db.add(notif)
                    missing_contacts += 1
                elif not self._validate_phone_number(student.guardian_phone):
                    notif.status = "FAILED"
                    notif.failure_reason = "INVALID_CONTACT"
                    self.db.add(notif)
                    failed_count += 1
                else:
                    self.db.add(notif)
                    self.db.flush()
                    self._dispatch_channel(notif, student.guardian_phone)
                    sent_or_queued += 1

        self.db.commit()

        msg = f"Processed {total_targeted} student results. {sent_or_queued} sent/queued, {already_notified} already notified, {missing_contacts} missing contact."
        return ResultAlertNotifyResponse(
            success=True,
            message=msg,
            total_targeted=total_targeted,
            sent_or_queued_count=sent_or_queued,
            already_notified_count=already_notified,
            missing_contact_count=missing_contacts,
            failed_count=failed_count,
        )

    # =========================================================================
    # SINGLE NOTIFICATION DISPATCH (ADMIN)
    # =========================================================================

    def send_single_notification(
        self,
        admin_user: User,
        payload: SingleNotificationCreate
    ) -> Notification:
        student = self.db.query(Student).filter(Student.id == payload.student_id).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student ID {payload.student_id} not found."
            )

        enrollment = self.db.query(StudentEnrollment).filter(
            StudentEnrollment.student_id == student.id,
            StudentEnrollment.status == "ACTIVE"
        ).order_by(StudentEnrollment.id.desc()).first()

        class_id = enrollment.class_id if enrollment else (student.current_class.id if student.current_class else None)
        class_name = enrollment.school_class.name if enrollment and enrollment.school_class else (student.current_class.name if student.current_class else "")
        academic_year = enrollment.academic_year if enrollment else (student.current_class.academic_year if student.current_class else None)

        guardian_phone = payload.custom_guardian_phone or student.guardian_phone
        guardian_email = payload.custom_guardian_email or student.guardian_email
        guardian_name = student.guardian_name or "Parent/Guardian"
        guardian_relationship = student.guardian_relationship or "Guardian"

        channel = payload.channel.upper()
        now = datetime.now(timezone.utc)
        school_name = self.get_setting("school_name", "Education Management System")

        fee_bal = self._resolve_student_fee_balance(student.id)
        context = {
            "student_name": student.full_name,
            "guardian_name": guardian_name,
            "class_name": class_name,
            "date": date.today().isoformat(),
            "school_name": school_name,
            "fee_balance": fee_bal,
            "message": payload.message,
        }

        rendered_title = self.render_template(payload.title, context)
        rendered_message = self.render_template(payload.message, context)

        notification = Notification(
            notification_type=payload.notification_type,
            title=rendered_title,
            message=rendered_message,
            channel=channel,
            student_id=student.id,
            guardian_name=guardian_name,
            guardian_phone=guardian_phone,
            guardian_email=guardian_email,
            guardian_relationship=guardian_relationship,
            class_id=class_id,
            academic_year=academic_year,
            created_by_id=admin_user.id,
            created_at=now,
            attempt_count=0,
            status="PENDING",
        )

        recipient = ""
        if channel == "SMS":
            recipient = guardian_phone or ""
        elif channel == "EMAIL":
            recipient = guardian_email or ""
        elif channel == "IN_APP":
            recipient = f"USER-{student.user_id}" if student.user_id else f"STD-{student.id}"

        if channel == "SMS":
            if not guardian_phone or not guardian_phone.strip():
                notification.status = "NOT_SENT"
                notification.failure_reason = "MISSING_CONTACT"
                self.db.add(notification)
                self.db.commit()
                return notification
            elif not self._validate_phone_number(guardian_phone):
                notification.status = "FAILED"
                notification.failure_reason = "INVALID_CONTACT"
                self.db.add(notification)
                self.db.commit()
                return notification
        elif channel == "EMAIL":
            if not guardian_email or not guardian_email.strip():
                notification.status = "NOT_SENT"
                notification.failure_reason = "MISSING_CONTACT"
                self.db.add(notification)
                self.db.commit()
                return notification

        self.db.add(notification)
        self.db.flush()

        self._dispatch_channel(notification, recipient)
        self.db.commit()
        return notification

    # =========================================================================
    # BULK NOTIFICATION DISPATCH (ADMIN)
    # =========================================================================

    def send_bulk_notifications(
        self,
        admin_user: User,
        payload: BulkNotificationCreate
    ) -> BulkNotificationResponse:
        query = self.db.query(Student).filter(Student.status == "ACTIVE")

        if payload.target_type == "CLASS":
            if not payload.class_id:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="class_id is required when target_type is CLASS."
                )
            query = query.join(StudentEnrollment, Student.id == StudentEnrollment.student_id).filter(
                StudentEnrollment.class_id == payload.class_id,
                StudentEnrollment.status == "ACTIVE"
            )
            if payload.academic_year:
                query = query.filter(StudentEnrollment.academic_year == payload.academic_year)

        elif payload.target_type == "SELECTED_STUDENTS":
            if not payload.student_ids:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="student_ids array is required when target_type is SELECTED_STUDENTS."
                )
            query = query.filter(Student.id.in_(payload.student_ids))

        students = query.all()
        total_targeted = len(students)
        eligible_count = 0
        missing_contact_count = 0
        created_count = 0
        skipped_duplicates_count = 0
        created_notifications: List[Notification] = []

        channel = payload.channel.upper()
        now = datetime.now(timezone.utc)
        school_name = self.get_setting("school_name", "Education Management System")

        for student in students:
            has_contact = True
            recipient = ""
            if channel == "SMS":
                recipient = student.guardian_phone or ""
                if not recipient or not recipient.strip():
                    has_contact = False
            elif channel == "EMAIL":
                recipient = student.guardian_email or ""
                if not recipient or not recipient.strip():
                    has_contact = False
            elif channel == "IN_APP":
                recipient = f"USER-{student.user_id}" if student.user_id else f"STD-{student.id}"

            if not has_contact:
                missing_contact_count += 1
                notif = Notification(
                    notification_type=payload.notification_type,
                    title=payload.title,
                    message=payload.message,
                    channel=channel,
                    status="NOT_SENT",
                    failure_reason="MISSING_CONTACT",
                    student_id=student.id,
                    guardian_name=student.guardian_name or "Parent/Guardian",
                    guardian_phone=student.guardian_phone,
                    guardian_email=student.guardian_email,
                    guardian_relationship=student.guardian_relationship,
                    class_id=student.current_class_id,
                    created_by_id=admin_user.id,
                    created_at=now,
                )
                self.db.add(notif)
                created_notifications.append(notif)
                continue

            eligible_count += 1

            class_name = student.current_class.name if student.current_class else ""
            fee_bal = self._resolve_student_fee_balance(student.id)
            context = {
                "student_name": student.full_name,
                "guardian_name": student.guardian_name or "Parent/Guardian",
                "class_name": class_name,
                "date": date.today().isoformat(),
                "school_name": school_name,
                "fee_balance": fee_bal,
                "message": payload.message,
            }
            rendered_title = self.render_template(payload.title, context)
            rendered_msg = self.render_template(payload.message, context)

            notif = Notification(
                notification_type=payload.notification_type,
                title=rendered_title,
                message=rendered_msg,
                channel=channel,
                status="PENDING",
                student_id=student.id,
                guardian_name=student.guardian_name or "Parent/Guardian",
                guardian_phone=student.guardian_phone,
                guardian_email=student.guardian_email,
                guardian_relationship=student.guardian_relationship,
                class_id=student.current_class_id,
                created_by_id=admin_user.id,
                created_at=now,
            )
            self.db.add(notif)
            self.db.flush()

            self._dispatch_channel(notif, recipient)
            created_notifications.append(notif)
            created_count += 1

        self.db.commit()

        return BulkNotificationResponse(
            success=True,
            message=f"Bulk dispatch processed. {created_count} sent/queued, {missing_contact_count} missing contacts.",
            target_type=payload.target_type,
            total_targeted=total_targeted,
            eligible_count=eligible_count,
            missing_contact_count=missing_contact_count,
            created_count=created_count + missing_contact_count,
            skipped_duplicates_count=skipped_duplicates_count,
            notifications=[NotificationResponse.model_validate(n) for n in created_notifications],
        )

    # =========================================================================
    # AUTOMATIC EVENT TRIGGER: ATTENDANCE ABSENCE
    # =========================================================================

    def trigger_attendance_absence_notifications(
        self,
        class_id: int,
        subject_id: int,
        attendance_date: date,
        period: Optional[Any],
        recorded_by_id: Optional[int] = None
    ) -> List[Notification]:
        if not self.get_setting("notify_attendance_absent_enabled", "true").lower() in ("true", "1", "yes"):
            logger.info("Automatic attendance absence notification is disabled in system settings.")
            return []

        q = self.db.query(Attendance).filter(
            Attendance.class_id == class_id,
            Attendance.subject_id == subject_id,
            Attendance.date == attendance_date,
            Attendance.status == "ABSENT"
        )
        if period is not None:
            q = q.filter(Attendance.period == str(period))
        else:
            q = q.filter(Attendance.period.is_(None))

        absent_records = q.all()
        if not absent_records:
            return []

        school_name = self.get_setting("school_name", "Education Management System")
        tmpl = self.repo.get_template_by_code("ATTENDANCE_ABSENT")
        title_tmpl = tmpl.title_template if tmpl else "Hawlwadaag School: Maqnaansho Arday"
        body_tmpl = tmpl.body_template if tmpl else "Asc {{guardian_name}}, ardaygaaga {{student_name}} maanta ma uusan imaan dugsiga. Fadlan la soco xaalkiisa. — {{school_name}}"

        created_notifications: List[Notification] = []
        now = datetime.now(timezone.utc)

        for rec in absent_records:
            idempotency_key = f"attendance:{rec.id}:student:{rec.student_id}:date:{rec.date.isoformat()}"
            existing = self.repo.get_by_idempotency_key(idempotency_key)
            if existing:
                logger.info(f"Skipping duplicate absence notification for key: {idempotency_key}")
                continue

            student = self.db.query(Student).filter(Student.id == rec.student_id).first()
            if not student:
                continue

            class_name = rec.school_class.name if rec.school_class else ""
            context = {
                "student_name": student.full_name,
                "guardian_name": student.guardian_name or "Waalidka",
                "class_name": class_name,
                "date": rec.date.isoformat(),
                "school_name": school_name,
            }

            rendered_title = self.render_template(title_tmpl, context)
            rendered_body = self.render_template(body_tmpl, context)

            notif = Notification(
                notification_type="ATTENDANCE_ABSENT",
                title=rendered_title,
                message=rendered_body,
                channel="SMS",
                student_id=student.id,
                guardian_name=student.guardian_name or "Parent/Guardian",
                guardian_phone=student.guardian_phone,
                guardian_email=student.guardian_email,
                guardian_relationship=student.guardian_relationship,
                class_id=rec.class_id,
                academic_year=rec.academic_year,
                related_attendance_id=rec.id,
                idempotency_key=idempotency_key,
                created_by_id=recorded_by_id,
                created_at=now,
                attempt_count=0,
            )

            if not student.guardian_phone or not student.guardian_phone.strip():
                notif.status = "NOT_SENT"
                notif.failure_reason = "MISSING_CONTACT"
                self.db.add(notif)
            elif not self._validate_phone_number(student.guardian_phone):
                notif.status = "FAILED"
                notif.failure_reason = "INVALID_CONTACT"
                self.db.add(notif)
            else:
                self.db.add(notif)
                self.db.flush()
                self._dispatch_channel(notif, student.guardian_phone)

            created_notifications.append(notif)

        self.db.commit()
        return created_notifications

    # =========================================================================
    # AUTOMATIC EVENT TRIGGER: RESULT RELEASE
    # =========================================================================

    def trigger_result_release_notifications(
        self,
        release_batch_id: int,
        admin_user_id: Optional[int] = None
    ) -> List[Notification]:
        if not self.get_setting("notify_result_release_enabled", "true").lower() in ("true", "1", "yes"):
            logger.info("Automatic result release notification is disabled in system settings.")
            return []

        batch = self.db.query(ResultReleaseBatch).filter(ResultReleaseBatch.id == release_batch_id).first()
        if not batch:
            logger.warning(f"ResultReleaseBatch {release_batch_id} not found.")
            return []

        exam_results = self.db.query(ExamResult).filter(
            ExamResult.release_batch_id == release_batch_id,
            ExamResult.status == "RELEASED"
        ).all()

        student_ids = list(set(r.student_id for r in exam_results))
        if not student_ids:
            return []

        school_name = self.get_setting("school_name", "Education Management System")
        tmpl = self.repo.get_template_by_code("RESULT_RELEASED")
        title_tmpl = tmpl.title_template if tmpl else "Hawlwadaag School: Natiijada Imtixaanka"
        body_tmpl = tmpl.body_template if tmpl else "Asc {{guardian_name}}, natiijada {{student_name}} ee {{exam_name}} waa la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — {{school_name}}"

        created_notifications: List[Notification] = []
        now = datetime.now(timezone.utc)
        class_name = batch.school_class.name if batch.school_class else ""

        for s_id in student_ids:
            idempotency_key = f"result_release:{s_id}:batch:{batch.id}"
            existing = self.repo.get_by_idempotency_key(idempotency_key)
            if existing:
                logger.info(f"Skipping duplicate result release notification for key: {idempotency_key}")
                continue

            student = self.db.query(Student).filter(Student.id == s_id).first()
            if not student:
                continue

            context = {
                "student_name": student.full_name,
                "guardian_name": student.guardian_name or "Waalidka",
                "class_name": class_name,
                "exam_name": batch.exam_name,
                "academic_year": batch.academic_year,
                "date": date.today().isoformat(),
                "school_name": school_name,
            }

            rendered_title = self.render_template(title_tmpl, context)
            rendered_body = self.render_template(body_tmpl, context)

            notif = Notification(
                notification_type="RESULT_RELEASED",
                title=rendered_title,
                message=rendered_body,
                channel="SMS",
                student_id=student.id,
                guardian_name=student.guardian_name or "Parent/Guardian",
                guardian_phone=student.guardian_phone,
                guardian_email=student.guardian_email,
                guardian_relationship=student.guardian_relationship,
                class_id=batch.class_id,
                academic_year=batch.academic_year,
                related_release_batch_id=batch.id,
                idempotency_key=idempotency_key,
                created_by_id=admin_user_id,
                created_at=now,
                attempt_count=0,
            )

            if not student.guardian_phone or not student.guardian_phone.strip():
                notif.status = "NOT_SENT"
                notif.failure_reason = "MISSING_CONTACT"
                self.db.add(notif)
            elif not self._validate_phone_number(student.guardian_phone):
                notif.status = "FAILED"
                notif.failure_reason = "INVALID_CONTACT"
                self.db.add(notif)
            else:
                self.db.add(notif)
                self.db.flush()
                self._dispatch_channel(notif, student.guardian_phone)

            created_notifications.append(notif)

        self.db.commit()
        return created_notifications

    # =========================================================================
    # RETRY FUNCTIONALITY
    # =========================================================================

    def retry_notification(self, notification_id: int) -> Notification:
        notif = self.repo.get_by_id(notification_id)
        if not notif:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Notification ID {notification_id} not found."
            )

        channel = notif.channel.upper()
        recipient = ""
        if channel == "SMS":
            recipient = notif.guardian_phone or ""
        elif channel == "EMAIL":
            recipient = notif.guardian_email or ""
        elif channel == "IN_APP":
            recipient = f"STD-{notif.student_id}"

        if not recipient:
            notif.status = "NOT_SENT"
            notif.failure_reason = "MISSING_CONTACT"
            self.db.commit()
            return notif

        self._dispatch_channel(notif, recipient)
        self.db.commit()
        return notif

    def retry_all_failed(self) -> Dict[str, Any]:
        failed_notifs = (
            self.db.query(Notification)
            .filter(Notification.status.in_(["FAILED", "NOT_CONFIGURED"]))
            .all()
        )

        retried_count = 0
        for notif in failed_notifs:
            recipient = ""
            if notif.channel.upper() == "SMS":
                recipient = notif.guardian_phone or ""
            elif notif.channel.upper() == "EMAIL":
                recipient = notif.guardian_email or ""
            elif notif.channel.upper() == "IN_APP":
                recipient = f"STD-{notif.student_id}"

            if recipient:
                self._dispatch_channel(notif, recipient)
                retried_count += 1

        self.db.commit()
        return {
            "success": True,
            "total_retried": retried_count,
            "message": f"Retried {retried_count} failed notifications."
        }

    # =========================================================================
    # MISSING CONTACTS AUDIT
    # =========================================================================

    def get_missing_contacts(
        self,
        class_id: Optional[int] = None,
        academic_year: Optional[str] = None
    ) -> MissingContactsResponse:
        students = self.repo.get_students_missing_contact(class_id, academic_year)
        items = []
        for s in students:
            items.append(
                MissingContactStudentItem(
                    student_id=s.id,
                    admission_number=s.admission_number,
                    full_name=s.full_name,
                    class_name=s.current_class.name if s.current_class else None,
                    guardian_name=s.guardian_name,
                    guardian_relationship=s.guardian_relationship,
                    has_phone=bool(s.guardian_phone and s.guardian_phone.strip()),
                    has_email=bool(s.guardian_email and s.guardian_email.strip()),
                    status=s.status,
                )
            )
        return MissingContactsResponse(
            total_missing=len(items),
            class_id=class_id,
            students=items,
        )

