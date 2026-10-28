from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime


class DeliveryResult:
    def __init__(
        self,
        status: str,
        provider_name: str,
        provider_message_id: Optional[str] = None,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
        delivered_at: Optional[datetime] = None,
        sent_at: Optional[datetime] = None,
        raw_response: Optional[Dict[str, Any]] = None,
    ):
        self.status = status  # QUEUED, PENDING, SENT, DELIVERED, READ, FAILED, NOT_CONFIGURED, NOT_SENT
        self.provider_name = provider_name
        self.provider_message_id = provider_message_id
        self.error_code = error_code
        self.error_message = error_message
        self.delivered_at = delivered_at
        self.sent_at = sent_at
        self.raw_response = raw_response or {}


class BaseNotificationProvider(ABC):
    """Abstract interface for all notification dispatch channels."""

    @abstractmethod
    def is_configured(self) -> bool:
        """Check if provider credentials/configurations are present and active."""
        pass

    @abstractmethod
    def get_status_info(self) -> Dict[str, Any]:
        """Return provider configuration status."""
        pass

    @abstractmethod
    def send(self, recipient: str, message: str, title: Optional[str] = None, extra_data: Optional[Dict[str, Any]] = None) -> DeliveryResult:
        """Dispatch notification to destination recipient."""
        pass
