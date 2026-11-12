import pytest
from datetime import date
from sqlalchemy import or_
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.student import Student
from app.models.school_class import SchoolClass
from app.models.attendance import Attendance
from app.models.exam import Exam, ExamResult
from app.models.result_release import ResultReleaseBatch
from app.models.notification import Notification, NotificationDelivery, NotificationTemplate
from app.models.system_setting import SystemSetting
from app.services.notification_service import NotificationService


@pytest.fixture(scope="module")
def admin_token(client):
    login_resp = client.post(
        "/api/v1/auth/login",
        json={
            "identifier": settings.INITIAL_ADMIN_USERNAME,
            "password": settings.INITIAL_ADMIN_PASSWORD,
        }
    )
    assert login_resp.status_code == 200
    return login_resp.json()["access_token"]


@pytest.fixture(scope="module")
def student_token(client):
    login_resp = client.post(
        "/api/v1/auth/login",
        json={
            "identifier": "std_farhan",
            "password": "Student@Hawlwadaag2026",
        }
    )
    if login_resp.status_code == 200:
        return login_resp.json()["access_token"]
    return None


def test_notification_unauthorized_access(client):
    resp = client.get("/api/v1/notifications")
    assert resp.status_code in (401, 403)


def test_notification_student_forbidden(client, student_token):
    if student_token:
        resp = client.get(
            "/api/v1/notifications",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        assert resp.status_code == 403


def test_notification_counters_endpoint(client, admin_token):
    resp = client.get(
        "/api/v1/notifications/counters",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "new_attendance_absent_count" in data
    assert "new_result_release_count" in data
    assert "total_notifications" in data


def test_notification_channel_configs(client, admin_token):
    resp = client.get(
        "/api/v1/notifications/channels",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "channels" in data
    channels = [c["channel"] for c in data["channels"]]
    assert "SMS" in channels
    assert "EMAIL" in channels
    assert "IN_APP" in channels


def test_notification_templates_and_update(client, admin_token):
    resp = client.get(
        "/api/v1/notifications/templates",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp.status_code == 200
    templates = resp.json()
    assert len(templates) >= 4
    codes = [t["code"] for t in templates]
    assert "ATTENDANCE_ABSENT" in codes
    assert "RESULT_RELEASED" in codes

    # Test update template
    update_resp = client.put(
        "/api/v1/notifications/templates/ATTENDANCE_ABSENT",
        json={
            "name": "Student Absence Alert (Somali)",
            "title_template": "Hawlwadaag School: Maqnaansho Arday",
            "body_template": "Asc {{guardian_name}}, ardaygaaga {{student_name}} maanta ma uusan imaan dugsiga. Fadlan la soco xaalkiisa. — {{school_name}}",
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert "Asc {{guardian_name}}" in updated["body_template"]


def test_attendance_alerts_grouping_and_personalization(client, admin_token):
    db = SessionLocal()
    school_class = db.query(SchoolClass).first()
    student = db.query(Student).first()
    test_date = date(2026, 6, 10)

    # Clean up test records
    db.query(Attendance).filter(
        Attendance.student_id == student.id,
        Attendance.date == test_date,
    ).delete()
    db.query(Notification).filter(
        Notification.student_id == student.id,
        Notification.notification_type == "ATTENDANCE_ABSENT"
    ).delete()
    db.commit()

    # Create absent attendance
    att = Attendance(
        student_id=student.id,
        class_id=school_class.id,
        subject_id=1,
        teacher_id=1,
        academic_year="2025/2026",
        date=test_date,
        period="1",
        status="ABSENT"
    )
    db.add(att)
    db.commit()
    db.close()

    # Query attendance alerts for that date
    resp = client.get(
        f"/api/v1/notifications/attendance-alerts?date={test_date.isoformat()}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["date"] == test_date.isoformat()
    assert data["total_absent_students"] >= 1
    assert len(data["classes"]) >= 1

    # Verify personalized message preview
    matching_students = [
        s for cls in data["classes"] for s in cls["students"] if s["student_id"] == student.id
    ]
    assert len(matching_students) > 0
    std_data = matching_students[0]
    assert "Asc" in std_data["personalized_preview"]
    assert student.full_name in std_data["personalized_preview"]


def test_attendance_alerts_preview_and_notify_with_deduplication(client, admin_token):
    test_date = date(2026, 6, 10)

    # 1. Preview
    preview_resp = client.post(
        "/api/v1/notifications/attendance-alerts/preview",
        json={
            "target_type": "ALL",
            "date": test_date.isoformat(),
            "channel": "SMS",
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert preview_resp.status_code == 200
    pdata = preview_resp.json()
    assert pdata["total_recipients"] >= 1
    assert len(pdata["previews"]) >= 1
    sample = pdata["previews"][0]
    assert "Asc" in sample["message"]
    assert sample["channel"] == "SMS"

    # 2. Notify
    notify_resp = client.post(
        "/api/v1/notifications/attendance-alerts/notify",
        json={
            "target_type": "ALL",
            "date": test_date.isoformat(),
            "channel": "SMS",
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert notify_resp.status_code == 200
    ndata = notify_resp.json()
    assert ndata["success"] is True
    assert ndata["total_targeted"] >= 1

    # 3. Duplicate Prevention: Notify again
    notify_again_resp = client.post(
        "/api/v1/notifications/attendance-alerts/notify",
        json={
            "target_type": "ALL",
            "date": test_date.isoformat(),
            "channel": "SMS",
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert notify_again_resp.status_code == 200
    n2data = notify_again_resp.json()
    # Sent count should be 0 because all were already notified
    assert n2data["sent_or_queued_count"] == 0
    assert n2data["already_notified_count"] >= 1


def test_result_alerts_workflow_and_preview(client, admin_token):
    # Query result alerts
    resp = client.get(
        "/api/v1/notifications/result-alerts",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "total_unnotified_results" in data
    assert "groups" in data

    if len(data["groups"]) > 0:
        first_group = data["groups"][0]
        batch_id = first_group["release_batch_id"]

        # Preview result alerts
        prev_resp = client.post(
            "/api/v1/notifications/result-alerts/preview",
            json={"release_batch_id": batch_id, "channel": "SMS"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert prev_resp.status_code == 200
        prev_data = prev_resp.json()
        assert prev_data["total_recipients"] >= 1

        # Notify result alerts
        not_resp = client.post(
            "/api/v1/notifications/result-alerts/notify",
            json={"release_batch_id": batch_id, "channel": "SMS"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert not_resp.status_code == 200
        not_data = not_resp.json()
        assert not_data["success"] is True


def test_send_single_notification_not_configured_sms(client, admin_token):
    db = SessionLocal()
    student = db.query(Student).filter(Student.guardian_phone.isnot(None), Student.guardian_phone != "").first()
    db.close()

    if not student:
        pytest.skip("No student with phone number found in database")

    payload = {
        "student_id": student.id,
        "notification_type": "GENERAL_ANNOUNCEMENT",
        "title": "Hawlwadaag School Notice",
        "message": "Asc {{guardian_name}}, ardayga {{student_name}} wuxuu helay ogeysiis.",
        "channel": "SMS",
    }

    resp = client.post(
        "/api/v1/notifications/send",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["student_id"] == student.id
    assert data["status"] in ("NOT_CONFIGURED", "SENT", "DELIVERED")
    assert "Asc" in data["message"]


def test_send_single_notification_missing_contact(client, admin_token):
    db = SessionLocal()
    student = db.query(Student).filter(
        or_(Student.guardian_phone.is_(None), Student.guardian_phone == "")
    ).first()
    
    if not student:
        student = db.query(Student).first()
        student.guardian_phone = None
        db.commit()

    student_id = student.id
    db.close()

    payload = {
        "student_id": student_id,
        "notification_type": "GENERAL_ANNOUNCEMENT",
        "title": "Missing Contact Notice",
        "message": "Hello parent",
        "channel": "SMS",
    }

    resp = client.post(
        "/api/v1/notifications/send",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "NOT_SENT"
    assert data["failure_reason"] == "MISSING_CONTACT"


def test_send_single_notification_invalid_contact(client, admin_token):
    db = SessionLocal()
    student = db.query(Student).first()
    student_id = student.id
    db.close()

    payload = {
        "student_id": student_id,
        "custom_guardian_phone": "invalid-phone",
        "notification_type": "CUSTOM",
        "title": "Invalid Phone Test",
        "message": "Hello parent",
        "channel": "SMS",
    }

    resp = client.post(
        "/api/v1/notifications/send",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "FAILED"
    assert data["failure_reason"] == "INVALID_CONTACT"


def test_list_notifications_pagination_and_filters(client, admin_token):
    resp = client.get(
        "/api/v1/notifications?page=1&limit=10",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "total" in data
    assert "items" in data
    assert "page" in data
    assert data["page"] == 1


def test_notification_stats(client, admin_token):
    resp = client.get(
        "/api/v1/notifications/stats",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "total_notifications" in data
    assert "pending_count" in data
    assert "failed_count" in data
    assert "delivered_count" in data
    assert "not_configured_count" in data


def test_somali_templates_and_dynamic_personalization(client, admin_token):
    """Verify that Somali templates render without raw placeholders and inject PostgreSQL data."""
    db = SessionLocal()
    student = db.query(Student).filter(Student.guardian_phone.isnot(None)).first()
    assert student is not None, "Need at least one student with phone"
    student_id = student.id
    student_name = student.full_name
    guardian_name = student.guardian_name or "Parent/Guardian"
    db.close()

    # Test Somali Attendance Absence template rendering
    resp = client.post(
        "/api/v1/notifications/send",
        json={
            "student_id": student_id,
            "notification_type": "ATTENDANCE_ABSENT",
            "title": "Ogeysiis Maqnaansho - {{student_name}}",
            "message": "Asc {{guardian_name}}, waxaan ku ogeysiinaynaa in ardaygaaga {{student_name}} maanta uusan imaan dugsiga. Fadlan la soco xaalkiisa. — {{school_name}}",
            "channel": "SMS",
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "{{student_name}}" not in data["message"]
    assert "{{guardian_name}}" not in data["message"]
    assert student_name in data["message"]
    assert "Hawlwadaag" in data["message"]

    # Test Somali Fee Reminder template with fee_balance
    resp_fee = client.post(
        "/api/v1/notifications/send",
        json={
            "student_id": student_id,
            "notification_type": "FEE_REMINDER",
            "title": "Xasuusin Lacagta Dugsiga - {{student_name}}",
            "message": "Asc {{guardian_name}}, waxaan ku xasuusinaynaa in ardaygaaga {{student_name}} uu leeyahay lacag dugsi oo dhan {{fee_balance}} oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — {{school_name}}",
            "channel": "SMS",
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp_fee.status_code == 200
    fee_data = resp_fee.json()
    assert "{{fee_balance}}" not in fee_data["message"]
    assert "{{student_name}}" not in fee_data["message"]
    assert student_name in fee_data["message"]


def test_unread_count_and_mark_as_read(client, admin_token):
    # 1. Check unread count endpoint
    resp = client.get(
        "/api/v1/notifications/unread-count",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp.status_code == 200
    initial_unread = resp.json()["unread_count"]
    assert initial_unread >= 0

    # 2. Get list of notifications
    list_resp = client.get(
        "/api/v1/notifications?limit=5",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert list_resp.status_code == 200
    items = list_resp.json()["items"]
    assert len(items) > 0
    target_notif = items[0]

    # 3. Mark individual notification as read
    mark_resp = client.post(
        f"/api/v1/notifications/{target_notif['id']}/read",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert mark_resp.status_code == 200
    mark_data = mark_resp.json()
    assert mark_data["success"] is True
    assert mark_data["id"] == target_notif["id"]
    assert mark_data["status"] == "READ"
    assert mark_data["read_at"] is not None

    # 4. Mark all as read
    mark_all_resp = client.post(
        "/api/v1/notifications/mark-all-read",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert mark_all_resp.status_code == 200
    assert mark_all_resp.json()["success"] is True

    # 5. Check unread count is now 0
    after_resp = client.get(
        "/api/v1/notifications/unread-count",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert after_resp.status_code == 200
    assert after_resp.json()["unread_count"] == 0


