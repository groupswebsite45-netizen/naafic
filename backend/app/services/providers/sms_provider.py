import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from app.services.providers.base_provider import BaseNotificationProvider, DeliveryResult
from app.services.providers.hormuud_sms_provider import HormuudSmsProvider, hormuud_token_manager
from app.utils.logger import logger


class SMSProvider(BaseNotificationProvider):
    """
    SMS Notification Provider Adapter for Hawlwadaag School.
    Integrates the official Hormuud SMS REST API provider as the primary gateway,
    supporting token caching, Somalia phone normalization, balance checking,
    and connection diagnostics.
    """

    def __init__(self, hormuud_provider: Optional[HormuudSmsProvider] = None):
        self.hormuud_provider = hormuud_provider or HormuudSmsProvider()
        self.provider_name = self.hormuud_provider.provider_name
        self.sender_id = self.hormuud_provider.sender_id

    def is_configured(self) -> bool:
        """Check if SMS gateway (Hormuud) is enabled and configured."""
        return self.hormuud_provider.is_configured()

    def get_status_info(self) -> Dict[str, Any]:
        """Return provider configuration status metadata."""
        return self.hormuud_provider.get_status_info()

    def normalize_phone(self, phone: Optional[str]) -> Optional[str]:
        """Normalize Somalia phone number."""
        return self.hormuud_provider.normalize_somalia_phone(phone)

    def send(
        self,
        recipient: str,
        message: str,
        title: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None,
    ) -> DeliveryResult:
        """Dispatch SMS via Hormuud SMS REST API."""
        return self.hormuud_provider.send(
            recipient=recipient,
            message=message,
            title=title,
            extra_data=extra_data,
        )

    def send_bulk(
        self,
        messages: List[Dict[str, Any]],
    ) -> List[DeliveryResult]:
        """Dispatch a batch of personalized SMS messages."""
        return self.hormuud_provider.send_bulk(messages)

    def check_balance(self) -> Dict[str, Any]:
        """Check SMS balance from Hormuud API."""
        return self.hormuud_provider.check_balance()

    def test_connection(self) -> Dict[str, Any]:
        """Test Hormuud SMS gateway connection and authentication."""
        return self.hormuud_provider.test_connection()

    def process_delivery_report(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process DLR callback from Hormuud."""
        return self.hormuud_provider.process_delivery_report(payload)

    def get_delivery(self, message_id: str, ref_id: Optional[str] = None) -> Dict[str, Any]:
        """Query Hormuud POST /api/GetDelivery for delivery report."""
        return self.hormuud_provider.get_delivery(message_id=message_id, ref_id=ref_id)

    def send_bulk_outbound(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Dispatch bulk messages via Hormuud POST /api/Outbound/SendBulkSMS."""
        return self.hormuud_provider.send_bulk_outbound(messages)

