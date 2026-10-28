from datetime import datetime, date
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, ConfigDict, Field


class NotificationTemplateBase(BaseModel):
    code: str = Field(..., min_length=2, max_length=100)
    name: str = Field(..., min_length=2, max_length=200)
    title_template: str = Field(..., min_length=2, max_length=255)
    body_template: str = Field(..., min_length=2)
    category: str = Field(default="GENERAL")
    is_active: bool = True


class NotificationTemplateUpdate(BaseModel):
    name: Optional[str] = None
    title_template: Optional[str] = None
    body_template: Optional[str] = None
    is_active: Optional[bool] = None


class NotificationTemplateResponse(NotificationTemplateBase):
    id: int
    is_system: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationDeliveryResponse(BaseModel):
    id: int
    notification_id: int
    channel: str
    recipient: str
    provider_name: Optional[str] = None
    provider_message_id: Optional[str] = None
    status: str
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    attempt_number: int
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationResponse(BaseModel):
    id: int
    notification_type: str
    title: str
    message: str
    channel: str
    status: str
    failure_reason: Optional[str] = None
    student_id: Optional[int] = None
    student_name: Optional[str] = None
    student_admission_number: Optional[str] = None
    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None
    guardian_email: Optional[str] = None
    guardian_relationship: Optional[str] = None
    class_id: Optional[int] = None
    class_name: Optional[str] = None
    academic_year: Optional[str] = None
    related_attendance_id: Optional[int] = None
    related_exam_id: Optional[int] = None
    related_result_id: Optional[int] = None
    related_release_batch_id: Optional[int] = None
    idempotency_key: Optional[str] = None
    created_by_id: Optional[int] = None
    attempt_count: int
    created_at: datetime
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class NotificationDetailResponse(NotificationResponse):
    deliveries: List[NotificationDeliveryResponse] = []
    extra_data: Optional[Dict[str, Any]] = None


class NotificationListResponse(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int
    items: List[NotificationResponse]


class NotificationSummaryStats(BaseModel):
    total_notifications: int
    delivered_count: int
    pending_count: int
    failed_count: int
    not_sent_count: int
    not_configured_count: int
    read_count: int
    sms_count: int
    email_count: int
    in_app_count: int
    today_count: int
    missing_contact_students: int


class NotificationCountersResponse(BaseModel):
    new_attendance_absent_count: int
    new_result_release_count: int
    total_failed_count: int
    total_pending_count: int
    total_delivered_count: int
    total_notifications: int


class SingleNotificationCreate(BaseModel):
    student_id: int = Field(..., description="Student whose guardian will receive notification")
    notification_type: str = Field(default="GENERAL_ANNOUNCEMENT", description="ATTENDANCE_ABSENT, RESULT_RELEASED, FEE_REMINDER, GENERAL_ANNOUNCEMENT, CUSTOM")
    title: str = Field(..., min_length=2, max_length=255)
    message: str = Field(..., min_length=2)
    channel: str = Field(default="SMS", description="SMS, EMAIL, IN_APP, WHATSAPP")
    custom_guardian_phone: Optional[str] = None
    custom_guardian_email: Optional[str] = None


class BulkNotificationCreate(BaseModel):
    target_type: str = Field(..., description="ALL_ACTIVE, CLASS, SELECTED_STUDENTS")
    class_id: Optional[int] = None
    student_ids: Optional[List[int]] = None
    academic_year: Optional[str] = None
    notification_type: str = Field(default="GENERAL_ANNOUNCEMENT")
    title: str = Field(..., min_length=2, max_length=255)
    message: str = Field(..., min_length=2)
    channel: str = Field(default="SMS")


class BulkNotificationResponse(BaseModel):
    success: bool
    message: str
    target_type: str
    total_targeted: int
    eligible_count: int
    missing_contact_count: int
    created_count: int
    skipped_duplicates_count: int
    notifications: List[NotificationResponse] = []


class MissingContactStudentItem(BaseModel):
    student_id: int
    admission_number: str
    full_name: str
    class_name: Optional[str] = None
    guardian_name: Optional[str] = None
    guardian_relationship: Optional[str] = None
    has_phone: bool
    has_email: bool
    status: str


class MissingContactsResponse(BaseModel):
    total_missing: int
    class_id: Optional[int] = None
    students: List[MissingContactStudentItem]


# =========================================================================
# ATTENDANCE ALERTS CENTER SCHEMAS
# =========================================================================

class AttendanceAlertStudentItem(BaseModel):
    attendance_id: int
    student_id: int
    student_name: str
    admission_number: str
    class_id: int
    class_name: str
    date: str
    period: Optional[str] = None
    subject_name: Optional[str] = None
    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None
    guardian_email: Optional[str] = None
    guardian_relationship: Optional[str] = None
    has_contact: bool
    is_notified: bool
    notification_status: Optional[str] = None
    personalized_preview: str


class AttendanceAlertClassGroup(BaseModel):
    class_id: int
    class_name: str
    class_code: str
    total_absent: int
    unnotified_count: int
    missing_contact_count: int
    students: List[AttendanceAlertStudentItem]


class AttendanceAlertsResponse(BaseModel):
    date: str
    total_absent_students: int
    total_unnotified: int
    total_notified: int
    total_missing_contacts: int
    classes: List[AttendanceAlertClassGroup]


class AttendanceAlertNotifyRequest(BaseModel):
    target_type: str = Field(default="ALL", description="ALL, CLASS, SELECTED_ATTENDANCES")
    date: Optional[str] = None
    class_id: Optional[int] = None
    attendance_ids: Optional[List[int]] = None
    channel: str = Field(default="SMS")
    custom_message_template: Optional[str] = None


class AttendanceAlertNotifyResponse(BaseModel):
    success: bool
    message: str
    total_targeted: int
    sent_or_queued_count: int
    already_notified_count: int
    missing_contact_count: int
    failed_count: int


# =========================================================================
# RESULT RELEASE ALERTS CENTER SCHEMAS
# =========================================================================

class ResultAlertStudentItem(BaseModel):
    result_id: int
    student_id: int
    student_name: str
    admission_number: str
    class_id: int
    class_name: str
    exam_name: str
    academic_year: str
    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None
    has_contact: bool
    is_notified: bool
    personalized_preview: str


class ResultAlertGroup(BaseModel):
    release_batch_id: int
    batch_code: str
    exam_name: str
    academic_year: str
    class_id: int
    class_name: str
    released_at: str
    total_students: int
    unnotified_count: int
    students: List[ResultAlertStudentItem]


class ResultAlertsResponse(BaseModel):
    total_unnotified_results: int
    groups: List[ResultAlertGroup]


class ResultAlertNotifyRequest(BaseModel):
    release_batch_id: Optional[int] = None
    class_id: Optional[int] = None
    exam_name: Optional[str] = None
    academic_year: Optional[str] = None
    student_ids: Optional[List[int]] = None
    channel: str = Field(default="SMS")
    custom_message_template: Optional[str] = None


class ResultAlertNotifyResponse(BaseModel):
    success: bool
    message: str
    total_targeted: int
    sent_or_queued_count: int
    already_notified_count: int
    missing_contact_count: int
    failed_count: int


# =========================================================================
# MESSAGE PREVIEWS & CHANNELS
# =========================================================================

class MessagePreviewItem(BaseModel):
    student_id: int
    student_name: str
    guardian_name: str
    recipient_contact: str
    channel: str
    title: str
    message: str
    has_contact: bool
    is_already_notified: bool


class MessagePreviewResponse(BaseModel):
    total_recipients: int
    valid_contacts_count: int
    missing_contacts_count: int
    already_notified_count: int
    previews: List[MessagePreviewItem]


class MessagePreviewRequest(BaseModel):
    preview_type: str = Field(..., description="ATTENDANCE, RESULTS, MANUAL")
    target_type: str = Field(default="ALL")
    date: Optional[str] = None
    class_id: Optional[int] = None
    attendance_ids: Optional[List[int]] = None
    release_batch_id: Optional[int] = None
    student_ids: Optional[List[int]] = None
    custom_message_template: Optional[str] = None
    channel: str = Field(default="SMS")


class ChannelConfigItem(BaseModel):
    channel: str
    name: Optional[str] = "Provider"
    provider_name: Optional[str] = None
    is_configured: bool
    status_label: str
    status_code: Optional[str] = None
    sender_id: Optional[str] = None
    base_url: Optional[str] = None
    account_username: Optional[str] = None
    details: str


class ChannelConfigResponse(BaseModel):
    channels: List[ChannelConfigItem]


class SmsCalculationResponse(BaseModel):
    char_count: int
    encoding: str
    segments: int
    max_per_segment: int


class HormuudConnectionTestResponse(BaseModel):
    success: bool
    status: str
    message: str
    response_time_ms: float = 0.0
    sender_id: Optional[str] = None
    base_url: Optional[str] = None
    balance: Optional[Any] = None
    http_status: Optional[int] = None
    endpoint: Optional[str] = None
    reason: Optional[str] = None
    checked_at: str


class HormuudBalanceResponse(BaseModel):
    success: bool
    is_configured: bool
    balance: Optional[Any] = None
    service: Optional[str] = "smsapi"
    sender_id: Optional[str] = None
    message: Optional[str] = None
    http_status: Optional[int] = None
    endpoint: Optional[str] = None
    last_checked: str
