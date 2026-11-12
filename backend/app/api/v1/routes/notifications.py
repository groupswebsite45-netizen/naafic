from datetime import date
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.api.dependencies.auth import get_current_active_admin, get_current_user
from app.repositories.notification_repo import NotificationRepository
from app.services.notification_service import NotificationService
from app.schemas.notification import (
    NotificationResponse,
    NotificationDetailResponse,
    NotificationListResponse,
    NotificationSummaryStats,
    NotificationCountersResponse,
    SingleNotificationCreate,
    BulkNotificationCreate,
    BulkNotificationResponse,
    NotificationTemplateResponse,
    NotificationTemplateUpdate,
    MissingContactsResponse,
    ChannelConfigResponse,
    AttendanceAlertsResponse,
    AttendanceAlertNotifyRequest,
    AttendanceAlertNotifyResponse,
    ResultAlertsResponse,
    ResultAlertNotifyRequest,
    ResultAlertNotifyResponse,
    MessagePreviewResponse,
)

router = APIRouter(prefix="/notifications", tags=["Admin Notifications"])


@router.get(
    "",
    response_model=NotificationListResponse,
    summary="List notifications with filtering, search, and pagination"
)
def list_notifications(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, description="ALL, PENDING, SENT, DELIVERED, READ, FAILED, NOT_SENT, NOT_CONFIGURED"),
    notification_type: Optional[str] = Query(None, description="ALL, ATTENDANCE_ABSENT, RESULT_RELEASED, FEE_REMINDER, GENERAL_ANNOUNCEMENT, CUSTOM"),
    channel: Optional[str] = Query(None, description="ALL, SMS, EMAIL, IN_APP"),
    class_id: Optional[int] = Query(None),
    student_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    search: Optional[str] = Query(None),
    academic_year: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_active_admin),
):
    service = NotificationService(db)
    items, total = service.repo.get_paginated(
        page=page,
        limit=limit,
        status=status,
        notification_type=notification_type,
        channel=channel,
        class_id=class_id,
        student_id=student_id,
        start_date=start_date,
        end_date=end_date,
        search=search,
        academic_year=academic_year,
    )
    total_pages = (total + limit - 1) // limit if total > 0 else 1
    return NotificationListResponse(
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages,
        items=[NotificationResponse.model_validate(n) for n in items],
    )


@router.get(
    "/stats",
    response_model=NotificationSummaryStats,
    summary="Get aggregated notification status and delivery metrics"
)
def get_notification_stats(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_active_admin),
):
    service = NotificationService(db)
    stats = service.repo.get_summary_stats()
    return NotificationSummaryStats(**stats)


@router.get(
    "/counters",
    response_model=NotificationCountersResponse,
    summary="Get real-time operational badge counters for unnotified attendance & results"
)
def get_notification_counters(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_active_admin),
):
    service = NotificationService(db)
    return service.get_notification_counters()


@router.get(
    "/channels",
    response_model=ChannelConfigResponse,
    summary="Get current status of configured notification channels (SMS, Email, In-App)"
)
def get_channel_configs(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_active_admin),
):
    service = NotificationService(db)
    return service.get_channel_configs()


@router.get(
    "/templates",
    response_model=List[NotificationTemplateResponse],
    summary="Get active notification message templates"
)
def get_templates(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_active_admin),
):
    service = NotificationService(db)
    templates = service.repo.get_templates(active_only=False)
    return [NotificationTemplateResponse.model_validate(t) for t in templates]


@router.put(
    "/templates/{code}",
    response_model=NotificationTemplateResponse,
    summary="Update a notification message template"
)
def update_template(
    code: str,
    payload: NotificationTemplateUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_active_admin),
):
    service = NotificationService(db)
    updated = service.update_template(code, payload)
    return NotificationTemplateResponse.model_validate(updated)


@router.get(
    "/settings",
    summary="Get automated notification trigger settings"
)
def get_notification_settings(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_active_admin),
):
    service = NotificationService(db)
    return service.get_notification_settings()


@router.put(
    "/settings",
    summary="Update automated notification trigger settings"
)
def update_notification_settings(
    settings_payload: Dict[str, Any],
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_active_admin),
):
    service = NotificationService(db)
    return service.update_notification_settings(settings_payload)


@router.get(
    "/missing-contacts",
    response_model=MissingContactsResponse,
    summary="List active students missing guardian phone or contact information"
)
def get_missing_contacts(
    class_id: Optional[int] = Query(None),
    academic_year: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_active_admin),
):
    service = NotificationService(db)
    return service.get_missing_contacts(class_id=class_id, academic_year=academic_year)


# =========================================================================
# ATTENDANCE ALERTS OPERATIONAL CENTER
# =========================================================================

@router.get(
    "/attendance-alerts",
    response_model=AttendanceAlertsResponse,
    summary="Get absent students grouped by class for a target date"
)
def get_attendance_alerts(
    date_str: Optional[str] = Query(None, alias="date"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_active_admin),
):
    service = NotificationService(db)
    target_date = date.fromisoformat(date_str) if date_str else date.today()
    return service.get_attendance_alerts(target_date=target_date)


@router.post(
    "/attendance-alerts/preview",
    response_model=MessagePreviewResponse,
    summary="Generate personalized message previews for absent student guardians"
)
def preview_attendance_alerts(
    payload: AttendanceAlertNotifyRequest,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_active_admin),
):
    service = NotificationService(db)
    return service.preview_attendance_alerts(payload)


@router.post(
    "/attendance-alerts/notify",
    response_model=AttendanceAlertNotifyResponse,
    summary="Notify absent student guardians (all, class, or selected) with duplicate prevention"
)
def notify_attendance_alerts(
    payload: AttendanceAlertNotifyRequest,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_active_admin),
):
    service = NotificationService(db)
    return service.notify_attendance_alerts(admin_user, payload)


# =========================================================================
# RESULT RELEASE ALERTS OPERATIONAL CENTER
# =========================================================================

@router.get(
    "/result-alerts",
    response_model=ResultAlertsResponse,
    summary="Get released exam results with unnotified guardians grouped by exam/class"
)
def get_result_alerts(
    academic_year: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_active_admin),
):
    service = NotificationService(db)
    return service.get_result_alerts(academic_year=academic_year)


@router.post(
    "/result-alerts/preview",
    response_model=MessagePreviewResponse,
    summary="Generate personalized result release message previews"
)
def preview_result_alerts(
    payload: ResultAlertNotifyRequest,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_active_admin),
):
    service = NotificationService(db)
    return service.preview_result_alerts(payload)


@router.post(
    "/result-alerts/notify",
    response_model=ResultAlertNotifyResponse,
    summary="Notify released result guardians with duplicate prevention"
)
def notify_result_alerts(
    payload: ResultAlertNotifyRequest,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_active_admin),
):
    service = NotificationService(db)
    return service.notify_result_alerts(admin_user, payload)


# =========================================================================
# MANUAL SEND & RETRY
# =========================================================================

@router.post(
    "/send",
    response_model=NotificationResponse,
    summary="Send an individualized notification to a single student's guardian"
)
def send_single_notification(
    payload: SingleNotificationCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_active_admin),
):
    service = NotificationService(db)
    notif = service.send_single_notification(admin_user, payload)
    return NotificationResponse.model_validate(notif)


@router.post(
    "/send-bulk",
    response_model=BulkNotificationResponse,
    summary="Send bulk notifications to an entire class, selected students, or all active students"
)
def send_bulk_notifications(
    payload: BulkNotificationCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_active_admin),
):
    service = NotificationService(db)
    return service.send_bulk_notifications(admin_user, payload)


@router.get(
    "/unread-count",
    summary="Get count of unread in-app notifications"
)
def get_unread_count(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_active_admin),
):
    repo = NotificationRepository(db)
    count = repo.get_unread_count()
    return {"unread_count": count}


@router.post(
    "/mark-all-read",
    summary="Mark all in-app notifications as read"
)
def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_active_admin),
):
    repo = NotificationRepository(db)
    count = repo.mark_all_as_read()
    db.commit()
    return {"success": True, "marked_count": count}


@router.post(
    "/{notification_id}/read",
    summary="Mark an individual notification as read"
)
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_active_admin),
):
    repo = NotificationRepository(db)
    notif = repo.mark_as_read(notification_id)
    if not notif:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification ID {notification_id} not found."
        )
    db.commit()
    return {
        "success": True,
        "id": notification_id,
        "status": notif.status,
        "read_at": notif.read_at
    }


@router.get(
    "/{notification_id}",
    response_model=NotificationDetailResponse,
    summary="Get complete notification details including delivery attempt logs"
)
def get_notification_detail(
    notification_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_active_admin),
):
    service = NotificationService(db)
    notif = service.repo.get_by_id(notification_id)
    if not notif:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification ID {notification_id} not found."
        )
    return NotificationDetailResponse.model_validate(notif)


@router.post(
    "/{notification_id}/retry",
    response_model=NotificationResponse,
    summary="Retry delivery for a specific failed or not-configured notification"
)
def retry_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_active_admin),
):
    service = NotificationService(db)
    notif = service.retry_notification(notification_id)
    return NotificationResponse.model_validate(notif)


@router.post(
    "/retry-failed",
    summary="Batch retry all failed and unconfigured notifications"
)
def retry_all_failed_notifications(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_active_admin),
):
    service = NotificationService(db)
    return service.retry_all_failed()


# =========================================================================
# HORMUUD SMS PROVIDER & WEBHOOKS
# =========================================================================

@router.get(
    "/providers/hormuud/status",
    summary="Get safe operational status metadata for Hormuud SMS provider"
)
def get_hormuud_status(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_active_admin),
):
    service = NotificationService(db)
    return service.sms_provider.get_status_info()


@router.post(
    "/providers/hormuud/test-connection",
    summary="Admin test connection for Hormuud SMS REST Gateway"
)
def test_hormuud_connection(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_active_admin),
):
    service = NotificationService(db)
    return service.test_hormuud_connection()


@router.get(
    "/providers/hormuud/balance",
    summary="Check SMS credit balance from Hormuud SMS REST Gateway"
)
def get_hormuud_balance(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_active_admin),
):
    service = NotificationService(db)
    return service.get_hormuud_balance()


@router.post(
    "/webhook/hormuud",
    summary="Delivery status callback webhook from Hormuud SMS REST API"
)
def hormuud_delivery_webhook(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
):
    service = NotificationService(db)
    return service.handle_hormuud_delivery_report(payload)


@router.post(
    "/providers/hormuud/delivery",
    summary="Alternative delivery status callback route for Hormuud DLR"
)
def hormuud_delivery_callback(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
):
    service = NotificationService(db)
    return service.handle_hormuud_delivery_report(payload)


@router.post(
    "/providers/hormuud/get-delivery",
    summary="Query delivery report directly from Hormuud POST /api/GetDelivery"
)
def get_hormuud_delivery_query(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_active_admin),
):
    service = NotificationService(db)
    msg_id = payload.get("messageid") or payload.get("message_id")
    ref_id = payload.get("refid") or payload.get("reference_id")
    if not msg_id:
        raise HTTPException(status_code=400, detail="messageid parameter is required.")
    return service.get_hormuud_delivery(message_id=str(msg_id), ref_id=str(ref_id or ""))

