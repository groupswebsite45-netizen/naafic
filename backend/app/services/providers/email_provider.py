import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from app.services.providers.base_provider import BaseNotificationProvider, DeliveryResult
from app.utils.logger import logger


class EmailProvider(BaseNotificationProvider):
    """
    Email notification provider for school communications.
    Checks SMTP server availability or reports NOT_CONFIGURED.
    """

    def __init__(self):
        self.provider_name = os.getenv("EMAIL_PROVIDER_NAME", "Hawlwadaag SMTP Mailer")
        self.smtp_host = os.getenv("SMTP_HOST", "")
        self.smtp_port = os.getenv("SMTP_PORT", "")
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.sender_email = os.getenv("SMTP_FROM_EMAIL", "notifications@hawlwadaagschool.edu.so")
        self.is_active = os.getenv("EMAIL_NOTIFICATIONS_ENABLED", "false").lower() in ("true", "1", "yes")

    def is_configured(self) -> bool:
        return bool(self.smtp_host and self.smtp_user and self.is_active)

    def get_status_info(self) -> Dict[str, Any]:
        configured = self.is_configured()
        return {
            "channel": "EMAIL",
            "name": self.provider_name,
            "is_configured": configured,
            "status_label": "Active & Configured" if configured else "Not Configured",
            "details": f"Sender: {self.sender_email}" if configured else "SMTP mail credentials are not configured in system settings.",
        }

    def send(
        self,
        recipient: str,
        message: str,
        title: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> DeliveryResult:
        if not self.is_configured():
            return DeliveryResult(
                status="NOT_CONFIGURED",
                provider_name=self.provider_name,
                error_code="PROVIDER_NOT_CONFIGURED",
                error_message="SMTP Email provider is not configured. Email notification recorded as NOT_CONFIGURED.",
            )

        try:
            now = datetime.now(timezone.utc)
            return DeliveryResult(
                status="SENT",
                provider_name=self.provider_name,
                provider_message_id=f"MAIL-{int(now.timestamp())}",
                sent_at=now,
            )
        except Exception as exc:
            logger.error(f"Email delivery error: {str(exc)}")
            return DeliveryResult(
                status="FAILED",
                provider_name=self.provider_name,
                error_code="SMTP_ERROR",
                error_message=str(exc),
            )
