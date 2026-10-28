import os
import re
import time
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, Tuple, List
import httpx

from app.core.config import settings
from app.services.providers.base_provider import BaseNotificationProvider, DeliveryResult
from app.utils.logger import logger


class HormuudTokenManager:
    """
    Manages OAuth Bearer tokens for the Hormuud SMS REST API.
    Caches the access token in memory with an expiration safety buffer,
    auto-refreshes when expired, and securely handles errors without leaking credentials.
    """

    def __init__(self):
        self._cached_token: Optional[str] = None
        self._expires_at: Optional[datetime] = None

    def get_token(
        self,
        base_url: str,
        username: str,
        password: str,
        force_refresh: bool = False,
        timeout: float = 10.0,
    ) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """
        Retrieve a valid Bearer token, reusing cached token if valid.
        Returns: (access_token, error_info_dict_or_None)
        """
        now = datetime.now(timezone.utc)

        # Reuse cached token if valid and not close to expiring (5 min buffer)
        if (
            not force_refresh
            and self._cached_token
            and self._expires_at
            and now < (self._expires_at - timedelta(minutes=5))
        ):
            return self._cached_token, None

        if not username or not password:
            return None, {
                "status": "NOT_CONFIGURED",
                "http_status": None,
                "endpoint": f"{base_url.rstrip('/')}/token",
                "reason": "Hormuud SMS username and password are not configured.",
                "message": "Hormuud SMS username and password are not configured in environment.",
            }

        token_url = f"{base_url.rstrip('/')}/token"

        try:
            # Hormuud /token endpoint accepts application/x-www-form-urlencoded
            payload = {
                "username": username,
                "password": password,
                "grant_type": "password",
            }

            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            }

            with httpx.Client(timeout=timeout) as client:
                resp = client.post(token_url, data=payload, headers=headers)

                # If form-data returned 415 or 400, try JSON body fallback
                if resp.status_code in (400, 415) and "json" not in resp.headers.get("content-type", ""):
                    resp = client.post(token_url, json=payload, headers={"Content-Type": "application/json", "Accept": "application/json"})

                if resp.status_code == 200:
                    data = resp.json()
                    access_token = data.get("access_token") or data.get("token") or data.get("data")
                    if not access_token:
                        return None, {
                            "status": "AUTHENTICATION_ERROR",
                            "http_status": 200,
                            "endpoint": f"POST {token_url}",
                            "reason": "Token response did not contain access_token.",
                            "message": "Token response did not contain access_token.",
                        }

                    expires_in = int(data.get("expires_in", 86400))  # Default 24 hours
                    self._cached_token = str(access_token)
                    self._expires_at = now + timedelta(seconds=expires_in)
                    logger.info(f"Successfully retrieved Hormuud SMS Bearer token (valid for {expires_in}s).")
                    return self._cached_token, None

                elif resp.status_code in (401, 403):
                    self.invalidate()
                    logger.warning(f"Hormuud SMS authentication failed: HTTP {resp.status_code}")
                    return None, {
                        "status": "AUTHENTICATION_ERROR",
                        "http_status": resp.status_code,
                        "endpoint": f"POST {token_url}",
                        "reason": f"Invalid Hormuud credentials (HTTP {resp.status_code}).",
                        "message": f"Authentication failed: Invalid Hormuud credentials (HTTP {resp.status_code}).",
                    }

                elif resp.status_code == 404:
                    self.invalidate()
                    logger.error(f"Hormuud token endpoint not found (HTTP 404): {token_url}")
                    return None, {
                        "status": "UNAVAILABLE",
                        "http_status": 404,
                        "endpoint": f"POST {token_url}",
                        "reason": "Hormuud endpoint was not found.",
                        "message": f"Connection failed. HTTP Status: 404. Endpoint: POST {token_url}. Reason: Hormuud endpoint was not found.",
                    }

                else:
                    self.invalidate()
                    logger.error(f"Hormuud token endpoint returned unexpected status: {resp.status_code}")
                    return None, {
                        "status": "UNAVAILABLE",
                        "http_status": resp.status_code,
                        "endpoint": f"POST {token_url}",
                        "reason": f"Hormuud gateway returned unexpected HTTP {resp.status_code}.",
                        "message": f"Hormuud token service returned HTTP {resp.status_code}: {resp.text[:200]}",
                    }

        except httpx.TimeoutException:
            logger.error(f"Timeout while connecting to Hormuud token endpoint: {token_url}")
            return None, {
                "status": "UNAVAILABLE",
                "http_status": None,
                "endpoint": f"POST {token_url}",
                "reason": "Connection to Hormuud SMS token endpoint timed out.",
                "message": f"Connection to Hormuud SMS token endpoint timed out ({token_url}).",
            }
        except httpx.ConnectError as ce:
            logger.error(f"Network error connecting to Hormuud: {ce}")
            return None, {
                "status": "UNAVAILABLE",
                "http_status": None,
                "endpoint": f"POST {token_url}",
                "reason": "Unable to reach Hormuud SMS gateway (Network / DNS error).",
                "message": f"Unable to reach Hormuud SMS gateway: {str(ce)}",
            }
        except Exception as exc:
            logger.error(f"Unexpected error retrieving Hormuud token: {exc}")
            return None, {
                "status": "UNAVAILABLE",
                "http_status": None,
                "endpoint": f"POST {token_url}",
                "reason": f"Unexpected error: {str(exc)}",
                "message": f"Error authenticating with Hormuud: {str(exc)}",
            }

    def invalidate(self):
        """Clear cached token."""
        self._cached_token = None
        self._expires_at = None


# Global singleton instance for in-memory token caching
hormuud_token_manager = HormuudTokenManager()


class HormuudSmsProvider(BaseNotificationProvider):
    """
    Official Hormuud SMS REST API Provider.
    Implements single and bulk SMS dispatch, Somalia phone normalization,
    delivery reports, balance checking, and connection diagnostics.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        sender_id: Optional[str] = None,
        is_enabled: Optional[bool] = None,
        token_manager: Optional[HormuudTokenManager] = None,
    ):
        self.base_url = (base_url or os.getenv("HORMUUD_SMS_BASE_URL") or settings.HORMUUD_SMS_BASE_URL or "https://smsapi.hormuud.com").rstrip("/")
        self.username = username if username is not None else (os.getenv("HORMUUD_SMS_USERNAME") or settings.HORMUUD_SMS_USERNAME or "")
        self.password = password if password is not None else (os.getenv("HORMUUD_SMS_PASSWORD") or settings.HORMUUD_SMS_PASSWORD or "")
        self.sender_id = sender_id or os.getenv("HORMUUD_SMS_SENDER_ID") or settings.HORMUUD_SMS_SENDER_ID or "HAWLWADAAG"
        
        if is_enabled is not None:
            self.is_enabled = is_enabled
        else:
            env_val = os.getenv("HORMUUD_SMS_ENABLED")
            if env_val is not None:
                self.is_enabled = env_val.lower() in ("true", "1", "yes")
            else:
                self.is_enabled = bool(settings.HORMUUD_SMS_ENABLED)

        self.token_manager = token_manager or hormuud_token_manager
        self.provider_name = "Hormuud SMS"

    # =========================================================================
    # CONFIGURATION & STATUS
    # =========================================================================

    def is_configured(self) -> bool:
        """Check if Hormuud SMS is enabled and essential credentials are set."""
        return bool(self.is_enabled and self.username and self.password and self.base_url)

    def get_status_info(self) -> Dict[str, Any]:
        """Return safe provider status metadata without exposing passwords or tokens."""
        configured = self.is_configured()
        
        # Determine status label
        if not self.is_enabled:
            status_label = "Disabled"
            status_code = "DISABLED"
        elif not (self.username and self.password):
            status_label = "Not Configured"
            status_code = "NOT_CONFIGURED"
        else:
            status_label = "Configured"
            status_code = "CONFIGURED"

        masked_username = f"{self.username[:3]}***" if len(self.username) >= 3 else "***" if self.username else "Not set"

        return {
            "channel": "SMS",
            "name": self.provider_name,
            "provider_name": self.provider_name,
            "is_configured": configured,
            "status_code": status_code,
            "status_label": status_label,
            "sender_id": self.sender_id,
            "base_url": self.base_url,
            "account_username": masked_username,
            "details": f"Sender ID: {self.sender_id} | Hormuud SMS Gateway ({self.base_url})" if configured else "Hormuud SMS API credentials are not configured in system settings.",
        }

    # =========================================================================
    # PHONE NUMBER NORMALIZATION
    # =========================================================================

    @staticmethod
    def normalize_somalia_phone(phone: Optional[str]) -> Optional[str]:
        """
        Normalize Somalia telephone numbers into international standard format (25261xxxxxxx).
        
        Supported inputs:
        - +252615123456 -> 252615123456
        - 252615123456  -> 252615123456
        - 0615123456    -> 252615123456
        - 615123456     -> 252615123456
        - 062..., 068..., 065..., 077..., 090...
        
        Returns:
            Normalized 12-digit string starting with 252, or None if invalid.
        """
        if not phone:
            return None

        # Clean all whitespace, dashes, parentheses, plus
        cleaned = re.sub(r"[\s\-\(\)\+]", "", str(phone))

        if not cleaned.isdigit():
            return None

        # Format 1: 061xxxxxxx (10 digits starting with 0)
        if len(cleaned) == 10 and cleaned.startswith("0"):
            cleaned = "252" + cleaned[1:]

        # Format 2: 61xxxxxxx (9 digits starting with 6 or 7 or 9)
        elif len(cleaned) == 9 and cleaned[0] in ("6", "7", "9"):
            cleaned = "252" + cleaned

        # Format 3: 25261xxxxxxx (12 digits starting with 252)
        elif len(cleaned) == 12 and cleaned.startswith("252"):
            pass

        # Format 4: 00252... (14 digits)
        elif len(cleaned) == 14 and cleaned.startswith("00252"):
            cleaned = cleaned[2:]

        else:
            return None

        # Validate final 12-digit Somalia structure: 252 followed by 9 digits
        if len(cleaned) == 12 and cleaned.startswith("252"):
            # Second part prefix validation (61=Hormuud, 62=Somtel/Telesom, 63, 65, 68, 77, 90, etc.)
            operator_prefix = cleaned[3:5]
            if operator_prefix in ("61", "62", "63", "64", "65", "66", "67", "68", "69", "71", "77", "90", "91"):
                return cleaned

        return None

    # =========================================================================
    # DISPATCH: SINGLE SMS (POST /api/SendSMS)
    # =========================================================================

    def send(
        self,
        recipient: str,
        message: str,
        title: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None,
    ) -> DeliveryResult:
        """
        Dispatch a single SMS message via Hormuud POST /api/SendSMS endpoint.
        """
        if not self.is_configured():
            logger.warning(f"SMS dispatch requested for {recipient} but Hormuud SMS provider is NOT_CONFIGURED.")
            return DeliveryResult(
                status="NOT_CONFIGURED",
                provider_name=self.provider_name,
                error_code="PROVIDER_NOT_CONFIGURED",
                error_message="Hormuud SMS is not enabled or credentials are missing in system environment.",
            )

        # 1. Normalize Phone Number
        normalized_phone = self.normalize_somalia_phone(recipient)
        if not normalized_phone:
            logger.warning(f"Invalid Somalia recipient phone number: '{recipient}'")
            return DeliveryResult(
                status="FAILED",
                provider_name=self.provider_name,
                error_code="INVALID_CONTACT",
                error_message=f"Phone number '{recipient}' is not a valid Somalia mobile number.",
            )

        # 2. Acquire Bearer Token
        token, auth_info = self.token_manager.get_token(
            base_url=self.base_url,
            username=self.username,
            password=self.password,
        )

        if not token:
            auth_msg = auth_info.get("message") if isinstance(auth_info, dict) else str(auth_info or "Authentication failed.")
            logger.error(f"Failed to authenticate with Hormuud: {auth_msg}")
            return DeliveryResult(
                status="FAILED",
                provider_name=self.provider_name,
                error_code="AUTHENTICATION_ERROR",
                error_message=auth_msg,
            )

        # 3. Construct Hormuud MTRequest Body
        extra = extra_data or {}
        ref_id = extra.get("refid") or extra.get("reference_id") or f"HAWL-{int(time.time())}-{uuid.uuid4().hex[:6]}"
        now_dt = datetime.now(timezone.utc)
        req_date = now_dt.strftime("%Y-%m-%d %H:%M:%S")

        hormuud_payload = {
            "refid": ref_id,
            "mobile": normalized_phone,
            "message": message,
            "senderid": self.sender_id,
            "mType": -1,
            "eType": -1,
            "validity": 0,
            "delivery": 0,
            "UDH": "",
            "RequestDate": req_date,
        }

        send_url = f"{self.base_url}/api/SendSMS"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        try:
            with httpx.Client(timeout=15.0) as client:
                resp = client.post(send_url, json=hormuud_payload, headers=headers)

                # If token expired on server side (401), invalidate and retry once
                if resp.status_code == 401:
                    logger.warning("Hormuud returned 401 Unauthorized. Refreshing token and retrying...")
                    self.token_manager.invalidate()
                    new_token, retry_auth_info = self.token_manager.get_token(
                        base_url=self.base_url,
                        username=self.username,
                        password=self.password,
                        force_refresh=True,
                    )
                    if new_token:
                        headers["Authorization"] = f"Bearer {new_token}"
                        resp = client.post(send_url, json=hormuud_payload, headers=headers)
                    else:
                        retry_msg = retry_auth_info.get("message") if isinstance(retry_auth_info, dict) else "Token refresh failed on 401 response."
                        return DeliveryResult(
                            status="FAILED",
                            provider_name=self.provider_name,
                            error_code="AUTHENTICATION_ERROR",
                            error_message=retry_msg,
                        )

                # Parse JSON response
                try:
                    res_json = resp.json()
                except Exception:
                    res_json = {"raw_text": resp.text}

                if resp.status_code == 200:
                    code = res_json.get("ResponceCode") or res_json.get("ResponseCode") or res_json.get("ErrorCode") or res_json.get("code")
                    msg = res_json.get("ResponceMessage") or res_json.get("ResponseMessage") or res_json.get("Description") or res_json.get("ErrorMessage") or "Success"
                    
                    # Extract MessageID
                    msg_id = (
                        res_json.get("Data")
                        or res_json.get("MessageID")
                        or res_json.get("MessageId")
                        or res_json.get("message_id")
                        or res_json.get("msgid")
                        or ref_id
                    )

                    is_success_code = code in (200, 0, "200", "0", None)

                    if is_success_code:
                        logger.info(f"Hormuud SMS accepted for {normalized_phone}. MsgID: {msg_id}, RefID: {ref_id}")
                        return DeliveryResult(
                            status="SENT",
                            provider_name=self.provider_name,
                            provider_message_id=str(msg_id),
                            sent_at=now_dt,
                            raw_response=res_json,
                        )
                    else:
                        logger.error(f"Hormuud SMS returned error code {code}: {msg}")
                        return DeliveryResult(
                            status="FAILED",
                            provider_name=self.provider_name,
                            error_code=f"HORMUUD_ERROR_{code}",
                            error_message=str(msg),
                            raw_response=res_json,
                        )

                elif resp.status_code in (401, 403):
                    return DeliveryResult(
                        status="FAILED",
                        provider_name=self.provider_name,
                        error_code="AUTHENTICATION_ERROR",
                        error_message=f"Hormuud API rejected authorization (HTTP {resp.status_code}).",
                        raw_response=res_json,
                    )
                elif resp.status_code == 404:
                    return DeliveryResult(
                        status="FAILED",
                        provider_name=self.provider_name,
                        error_code="HTTP_404",
                        error_message=f"Hormuud SendSMS endpoint not found (HTTP 404 at {send_url}).",
                        raw_response=res_json,
                    )
                else:
                    logger.error(f"Hormuud SendSMS failed with HTTP {resp.status_code}: {resp.text[:200]}")
                    return DeliveryResult(
                        status="FAILED",
                        provider_name=self.provider_name,
                        error_code=f"HTTP_{resp.status_code}",
                        error_message=f"Hormuud gateway returned HTTP {resp.status_code}: {resp.text[:200]}",
                        raw_response=res_json,
                    )

        except httpx.TimeoutException:
            logger.error(f"Timeout connecting to Hormuud SendSMS endpoint for {normalized_phone}")
            return DeliveryResult(
                status="FAILED",
                provider_name=self.provider_name,
                error_code="TIMEOUT",
                error_message="Connection to Hormuud SendSMS endpoint timed out.",
            )
        except httpx.ConnectError as ce:
            logger.error(f"Connection error to Hormuud SendSMS: {ce}")
            return DeliveryResult(
                status="FAILED",
                provider_name=self.provider_name,
                error_code="CONNECT_ERROR",
                error_message=f"Network error communicating with Hormuud: {str(ce)}",
            )
        except Exception as exc:
            logger.error(f"Unexpected error in Hormuud SMS dispatch: {exc}")
            return DeliveryResult(
                status="FAILED",
                provider_name=self.provider_name,
                error_code="UNEXPECTED_ERROR",
                error_message=str(exc),
            )

    # =========================================================================
    # DISPATCH: BULK SMS (POST /api/Outbound/SendBulkSMS)
    # =========================================================================

    def send_bulk(
        self,
        messages: List[Dict[str, Any]],
    ) -> List[DeliveryResult]:
        """
        Dispatch a batch of personalized messages.
        Iterates over messages ensuring each individual recipient receives their customized text.
        """
        results: List[DeliveryResult] = []
        for item in messages:
            recipient = item.get("recipient") or item.get("mobile") or ""
            text = item.get("message") or ""
            title = item.get("title")
            extra = item.get("extra_data") or {}
            res = self.send(recipient=recipient, message=text, title=title, extra_data=extra)
            results.append(res)
        return results

    def send_bulk_outbound(
        self,
        messages: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Call official Hormuud Bulk SMS endpoint POST /api/Outbound/SendBulkSMS.
        """
        if not self.is_configured():
            return {"success": False, "message": "Hormuud SMS is not configured."}

        token, auth_info = self.token_manager.get_token(
            base_url=self.base_url,
            username=self.username,
            password=self.password,
        )
        if not token:
            auth_msg = auth_info.get("message") if isinstance(auth_info, dict) else "Authentication failed."
            return {"success": False, "message": auth_msg}

        bulk_url = f"{self.base_url}/api/Outbound/SendBulkSMS"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                resp = client.post(bulk_url, json={"messages": messages, "senderid": self.sender_id}, headers=headers)
                return {
                    "success": resp.status_code == 200,
                    "status_code": resp.status_code,
                    "endpoint": f"POST {bulk_url}",
                    "data": resp.json() if resp.status_code == 200 else resp.text,
                }
        except Exception as exc:
            return {"success": False, "endpoint": f"POST {bulk_url}", "message": str(exc)}

    # =========================================================================
    # BALANCE & HEALTH DIAGNOSTICS (POST /api/checkbalance)
    # =========================================================================

    def check_balance(self) -> Dict[str, Any]:
        """
        Query SMS account balance from Hormuud POST /api/checkbalance.
        """
        now_str = datetime.now(timezone.utc).isoformat()

        if not self.is_configured():
            return {
                "success": False,
                "is_configured": False,
                "balance": None,
                "service": "smsapi",
                "sender_id": self.sender_id,
                "message": "Hormuud SMS is not configured.",
                "http_status": None,
                "endpoint": f"POST {self.base_url}/api/checkbalance",
                "last_checked": now_str,
            }

        token, auth_info = self.token_manager.get_token(
            base_url=self.base_url,
            username=self.username,
            password=self.password,
        )

        if not token:
            auth_msg = auth_info.get("message") if isinstance(auth_info, dict) else "Authentication failed."
            http_stat = auth_info.get("http_status") if isinstance(auth_info, dict) else None
            return {
                "success": False,
                "is_configured": True,
                "balance": None,
                "service": "smsapi",
                "sender_id": self.sender_id,
                "message": auth_msg,
                "http_status": http_stat,
                "endpoint": f"POST {self.base_url}/api/checkbalance",
                "last_checked": now_str,
            }

        balance_url = f"{self.base_url}/api/checkbalance"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        payload = {"service": "smsapi"}

        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(balance_url, json=payload, headers=headers)

                if resp.status_code == 200:
                    data = resp.json()
                    bal = data.get("Balance") or data.get("balance") or data.get("Data") or data.get("sms_balance")
                    return {
                        "success": True,
                        "is_configured": True,
                        "balance": bal,
                        "service": "smsapi",
                        "sender_id": self.sender_id,
                        "http_status": 200,
                        "endpoint": f"POST {balance_url}",
                        "last_checked": now_str,
                        "raw": data,
                    }
                elif resp.status_code == 404:
                    return {
                        "success": False,
                        "is_configured": True,
                        "balance": None,
                        "service": "smsapi",
                        "sender_id": self.sender_id,
                        "message": f"Hormuud balance endpoint was not found at POST {balance_url} (HTTP 404).",
                        "http_status": 404,
                        "endpoint": f"POST {balance_url}",
                        "last_checked": now_str,
                    }
                else:
                    return {
                        "success": False,
                        "is_configured": True,
                        "balance": None,
                        "service": "smsapi",
                        "sender_id": self.sender_id,
                        "message": f"Hormuud returned HTTP {resp.status_code}",
                        "http_status": resp.status_code,
                        "endpoint": f"POST {balance_url}",
                        "last_checked": now_str,
                    }
        except Exception as exc:
            return {
                "success": False,
                "is_configured": True,
                "balance": None,
                "service": "smsapi",
                "sender_id": self.sender_id,
                "message": str(exc),
                "http_status": None,
                "endpoint": f"POST {balance_url}",
                "last_checked": now_str,
            }

    # =========================================================================
    # DELIVERY STATUS QUERY (POST /api/GetDelivery)
    # =========================================================================

    def get_delivery(
        self,
        message_id: str,
        ref_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Query delivery report for a sent message from Hormuud POST /api/GetDelivery.
        """
        if not self.is_configured():
            return {"success": False, "message": "Hormuud SMS is not configured."}

        token, auth_info = self.token_manager.get_token(
            base_url=self.base_url,
            username=self.username,
            password=self.password,
        )
        if not token:
            auth_msg = auth_info.get("message") if isinstance(auth_info, dict) else "Authentication failed."
            return {"success": False, "message": auth_msg}

        delivery_url = f"{self.base_url}/api/GetDelivery"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        payload = {
            "messageid": str(message_id),
            "refid": str(ref_id or ""),
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(delivery_url, json=payload, headers=headers)
                return {
                    "success": resp.status_code == 200,
                    "status_code": resp.status_code,
                    "endpoint": f"POST {delivery_url}",
                    "data": resp.json() if resp.status_code == 200 else resp.text,
                }
        except Exception as exc:
            return {"success": False, "endpoint": f"POST {delivery_url}", "message": str(exc)}

    # =========================================================================
    # TEST CONNECTION DIAGNOSTIC
    # =========================================================================

    def test_connection(self) -> Dict[str, Any]:
        """
        Safe Admin diagnostic test:
        1. Validates configuration.
        2. Requests a real Hormuud bearer token from POST /token.
        3. If token succeeds: returns CONNECTED.
        4. If authentication fails (401/403): returns AUTHENTICATION_ERROR.
        5. If unreachable/timeout: returns UNAVAILABLE.
        6. If 404: returns UNAVAILABLE with exact endpoint requested.
        """
        start_time = time.time()
        now_str = datetime.now(timezone.utc).isoformat()
        token_endpoint = f"POST {self.base_url}/token"

        if not self.is_configured():
            return {
                "success": False,
                "status": "NOT_CONFIGURED",
                "message": "Hormuud SMS is disabled or credentials are not set in environment settings.",
                "response_time_ms": 0.0,
                "sender_id": self.sender_id,
                "base_url": self.base_url,
                "http_status": None,
                "endpoint": token_endpoint,
                "reason": "Hormuud SMS credentials not configured.",
                "checked_at": now_str,
            }

        token, auth_info = self.token_manager.get_token(
            base_url=self.base_url,
            username=self.username,
            password=self.password,
            force_refresh=True,
            timeout=8.0,
        )

        elapsed_ms = round((time.time() - start_time) * 1000, 2)

        if not token:
            if isinstance(auth_info, dict):
                diag_status = auth_info.get("status", "UNAVAILABLE")
                http_stat = auth_info.get("http_status")
                endpoint_called = auth_info.get("endpoint", token_endpoint)
                reason_str = auth_info.get("reason", "Authentication failed.")
                msg_str = auth_info.get("message", "Authentication failed with Hormuud SMS API.")
            else:
                diag_status = "AUTHENTICATION_ERROR"
                http_stat = None
                endpoint_called = token_endpoint
                reason_str = str(auth_info or "Authentication failed.")
                msg_str = str(auth_info or "Authentication failed with Hormuud SMS API.")

            return {
                "success": False,
                "status": diag_status,
                "message": msg_str,
                "response_time_ms": elapsed_ms,
                "sender_id": self.sender_id,
                "base_url": self.base_url,
                "http_status": http_stat,
                "endpoint": endpoint_called,
                "reason": reason_str,
                "checked_at": now_str,
            }

        # If token succeeded, attempt balance check for complete health status
        balance_info = self.check_balance()
        balance_val = balance_info.get("balance") if balance_info.get("success") else None

        return {
            "success": True,
            "status": "CONNECTED",
            "message": f"Successfully connected to Hormuud SMS Gateway ({elapsed_ms} ms).",
            "response_time_ms": elapsed_ms,
            "sender_id": self.sender_id,
            "base_url": self.base_url,
            "balance": balance_val,
            "http_status": 200,
            "endpoint": token_endpoint,
            "reason": "Bearer token retrieved and verified successfully.",
            "checked_at": now_str,
        }

    # =========================================================================
    # DELIVERY REPORT (DLR) WEBHOOK PROCESSING
    # =========================================================================

    def process_delivery_report(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse incoming Hormuud delivery webhook callback.
        
        Expected fields:
        - refid / reference_id
        - messageid / message_id
        - status / delivery_status (DELIVERED, UNDELIVERED, EXPIRED, FAILED)
        - delivery_date / timestamp
        - error_code / reason
        """
        ref_id = payload.get("refid") or payload.get("reference_id") or payload.get("RefId")
        msg_id = payload.get("messageid") or payload.get("message_id") or payload.get("MessageID") or payload.get("MsgId")
        raw_status = str(payload.get("status") or payload.get("delivery_status") or payload.get("Status") or "").upper()
        error_code = payload.get("error_code") or payload.get("ErrorCode") or payload.get("code")
        error_message = payload.get("reason") or payload.get("error_message") or payload.get("Description")
        
        del_date_str = payload.get("delivery_date") or payload.get("deliverydate") or payload.get("timestamp")

        # Map to internal status
        if raw_status in ("DELIVERED", "1", "SUCCESS", "DELIVRD"):
            mapped_status = "DELIVERED"
        elif raw_status in ("UNDELIVERED", "FAILED", "2", "EXPIRED", "REJECTED", "UNDELIV"):
            mapped_status = "FAILED"
        elif raw_status in ("SENT", "QUEUED", "PENDING", "0"):
            mapped_status = "SENT"
        else:
            mapped_status = "SENT"

        delivered_at = None
        if mapped_status == "DELIVERED":
            if del_date_str:
                try:
                    delivered_at = datetime.fromisoformat(del_date_str)
                except Exception:
                    delivered_at = datetime.now(timezone.utc)
            else:
                delivered_at = datetime.now(timezone.utc)

        return {
            "ref_id": ref_id,
            "provider_message_id": msg_id,
            "provider_status": raw_status,
            "mapped_status": mapped_status,
            "error_code": error_code,
            "error_message": error_message,
            "delivered_at": delivered_at,
            "raw_payload": payload,
        }

