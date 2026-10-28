from datetime import datetime, timezone
from typing import Dict, Any, Optional
from app.services.providers.base_provider import BaseNotificationProvider, DeliveryResult


class InAppProvider(BaseNotificationProvider):
    """
    In-App Notification Provider.
    Always active and configured as messages are delivered directly to the portal database.
    """

    def __init__(self):
        self.provider_name = "Hawlwadaag In-App Notification System"

    def is_configured(self) -> bool:
        return True

    def get_status_info(self) -> Dict[str, Any]:
        return {
            "channel": "IN_APP",
            "name": self.provider_name,
            "is_configured": True,
            "status_label": "Active & Ready",
            "details": "Direct portal delivery to student & parent accounts.",
        }

    def send(
        self,
        recipient: str,
        message: str,
        title: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> DeliveryResult:
        now = datetime.now(timezone.utc)
        return DeliveryResult(
            status="DELIVERED",
            provider_name=self.provider_name,
            provider_message_id=f"INAPP-{int(now.timestamp())}",
            sent_at=now,
            delivered_at=now,
        )
