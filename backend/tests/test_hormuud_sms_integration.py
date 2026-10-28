import pytest
import uuid
from datetime import datetime, timezone, timedelta, date
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import httpx

from app.main import create_application
from app.core.database import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.models.student import Student
from app.models.school_class import SchoolClass
from app.models.attendance import Attendance
from app.models.exam import Exam, ExamResult
from app.models.result_release import ResultReleaseBatch
from app.models.notification import Notification, NotificationDelivery, NotificationTemplate
from app.services.providers.hormuud_sms_provider import HormuudSmsProvider, HormuudTokenManager
from app.services.providers.sms_provider import SMSProvider
from app.services.notification_service import NotificationService
from app.core.security import create_access_token


@pytest.fixture(scope="module")
def app():
    return create_application()


@pytest.fixture(scope="module")
def client(app):
    return TestClient(app)


@pytest.fixture(scope="module")
def test_users():
    db = SessionLocal()
    # 1. Admin
    admin_role = db.query(Role).filter(Role.name == "ADMIN").first()
    if not admin_role:
        admin_role = Role(name="ADMIN", description="Administrator")
        db.add(admin_role)
        db.commit()

    admin = db.query(User).filter(User.username == "admin_test_hormuud").first()
    if not admin:
        admin = User(
            username="admin_test_hormuud",
            email="admin_hormuud@school.edu.so",
            full_name="Admin Hormuud Tester",
            hashed_password="fakehashadmin",
            is_active=True,
            is_superuser=True,
        )
        admin.roles.append(admin_role)
        db.add(admin)
        db.commit()
        db.refresh(admin)

    # 2. Teacher
    teacher_role = db.query(Role).filter(Role.name == "TEACHER").first()
    if not teacher_role:
        teacher_role = Role(name="TEACHER", description="Teacher")
        db.add(teacher_role)
        db.commit()

    teacher = db.query(User).filter(User.username == "teacher_test_hormuud").first()
    if not teacher:
        teacher = User(
            username="teacher_test_hormuud",
            email="teacher_hormuud@school.edu.so",
            full_name="Teacher Hormuud Tester",
            hashed_password="fakehashteacher",
            is_active=True,
        )
        teacher.roles.append(teacher_role)
        db.add(teacher)
        db.commit()
        db.refresh(teacher)

    # 3. Student User
    student_role = db.query(Role).filter(Role.name == "STUDENT").first()
    if not student_role:
        student_role = Role(name="STUDENT", description="Student")
        db.add(student_role)
        db.commit()

    student_user = db.query(User).filter(User.username == "student_test_hormuud").first()
    if not student_user:
        student_user = User(
            username="student_test_hormuud",
            email="student_hormuud@school.edu.so",
            full_name="Student Hormuud Tester",
            hashed_password="fakehashstudent",
            is_active=True,
        )
        student_user.roles.append(student_role)
        db.add(student_user)
        db.commit()
        db.refresh(student_user)

    db.close()
    return {"admin": admin, "teacher": teacher, "student_user": student_user}


@pytest.fixture(scope="module")
def admin_token(test_users):
    user = test_users["admin"]
    return create_access_token(subject=str(user.id), claims={"username": user.username, "roles": ["ADMIN"], "is_superuser": True})


@pytest.fixture(scope="module")
def teacher_token(test_users):
    user = test_users["teacher"]
    return create_access_token(subject=str(user.id), claims={"username": user.username, "roles": ["TEACHER"], "is_superuser": False})


@pytest.fixture(scope="module")
def student_token(test_users):
    user = test_users["student_user"]
    return create_access_token(subject=str(user.id), claims={"username": user.username, "roles": ["STUDENT"], "is_superuser": False})


# =========================================================================
# TEST 1 & 2: HORMUUD DISABLED & NOT CONFIGURED MODES
# =========================================================================

def test_hormuud_not_configured_when_disabled():
    """When Hormuud is disabled or keys are missing, status is accurately NOT_CONFIGURED."""
    provider = HormuudSmsProvider(
        base_url="https://smsapi.hormuud.com",
        username="",
        password="",
        is_enabled=False
    )
    assert not provider.is_configured()
    info = provider.get_status_info()
    assert info["status_code"] == "DISABLED"

    res = provider.send(recipient="252615123456", message="Test alert")
    assert res.status == "NOT_CONFIGURED"
    assert res.error_code == "PROVIDER_NOT_CONFIGURED"


def test_hormuud_not_configured_when_missing_credentials():
    """When Hormuud is enabled but credentials are missing, status is NOT_CONFIGURED."""
    provider = HormuudSmsProvider(
        base_url="https://smsapi.hormuud.com",
        username="",
        password="",
        is_enabled=True
    )
    assert not provider.is_configured()
    info = provider.get_status_info()
    assert info["status_code"] == "NOT_CONFIGURED"


# =========================================================================
# TEST 3: SOMALIA PHONE NUMBER NORMALIZATION
# =========================================================================

def test_hormuud_somalia_phone_normalization():
    """Verify phone normalization for various Somalia mobile number formats."""
    # +252615123456 -> 252615123456
    assert HormuudSmsProvider.normalize_somalia_phone("+252615123456") == "252615123456"
    # 252615123456 -> 252615123456
    assert HormuudSmsProvider.normalize_somalia_phone("252615123456") == "252615123456"
    # 0615123456 -> 252615123456
    assert HormuudSmsProvider.normalize_somalia_phone("0615123456") == "252615123456"
    # 615123456 -> 252615123456
    assert HormuudSmsProvider.normalize_somalia_phone("615123456") == "252615123456"
    # Somtel/Telesom 062xxxxxxx -> 25262xxxxxxx
    assert HormuudSmsProvider.normalize_somalia_phone("0625123456") == "252625123456"
    # Somtel 65xxxxxxx -> 25265xxxxxxx
    assert HormuudSmsProvider.normalize_somalia_phone("655123456") == "252655123456"
    # With spaces & dashes
    assert HormuudSmsProvider.normalize_somalia_phone("+252 61-512-3456") == "252615123456"

    # Invalid numbers
    assert HormuudSmsProvider.normalize_somalia_phone("") is None
    assert HormuudSmsProvider.normalize_somalia_phone("12345") is None
    assert HormuudSmsProvider.normalize_somalia_phone("abcdef") is None
    assert HormuudSmsProvider.normalize_somalia_phone("+14155552671") is None  # Non-Somalia


# =========================================================================
# TEST 4: TOKEN RETRIEVAL & IN-MEMORY CACHING
# =========================================================================

def test_hormuud_token_acquisition_and_caching():
    """Verify Bearer token is requested and cached until expiration."""
    tm = HormuudTokenManager()
    
    # Mock HTTP response for /token
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "access_token": "hormuud_test_token_xyz_12345",
        "token_type": "bearer",
        "expires_in": 3600,
    }

    with patch("httpx.Client.post", return_value=mock_resp) as mock_post:
        token, err = tm.get_token(
            base_url="https://smsapi.hormuud.com",
            username="test_user",
            password="test_password",
        )
        assert err is None
        assert token == "hormuud_test_token_xyz_12345"
        assert mock_post.call_count == 1

        # Second call should use cache without hitting HTTP
        token2, err2 = tm.get_token(
            base_url="https://smsapi.hormuud.com",
            username="test_user",
            password="test_password",
        )
        assert token2 == "hormuud_test_token_xyz_12345"
        assert mock_post.call_count == 1  # Still 1 because cached!


# =========================================================================
# TEST 5: TOKEN AUTO-REFRESH & INVALIDATION
# =========================================================================

def test_hormuud_token_refresh_on_expiry():
    """Verify token auto-refreshes when expired or force_refresh is set."""
    tm = HormuudTokenManager()
    
    # Set expired token
    tm._cached_token = "old_expired_token"
    tm._expires_at = datetime.now(timezone.utc) - timedelta(minutes=10)

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "access_token": "new_refreshed_token_67890",
        "expires_in": 7200,
    }

    with patch("httpx.Client.post", return_value=mock_resp):
        token, err = tm.get_token(
            base_url="https://smsapi.hormuud.com",
            username="test_user",
            password="test_password",
        )
        assert token == "new_refreshed_token_67890"


# =========================================================================
# TEST 6: AUTHENTICATION FAILURE HANDLING
# =========================================================================

def test_hormuud_authentication_failure_handling():
    """Verify 401/403 responses return clear errors without crashing."""
    tm = HormuudTokenManager()
    
    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_resp.text = "Invalid username or password"

    with patch("httpx.Client.post", return_value=mock_resp):
        token, err = tm.get_token(
            base_url="https://smsapi.hormuud.com",
            username="wrong_user",
            password="wrong_password",
        )
        assert token is None
        assert isinstance(err, dict)
        assert err["http_status"] == 401
        assert "Invalid Hormuud credentials" in err["reason"]


def test_hormuud_404_endpoint_diagnostic_handling():
    """Verify 404 endpoint returns exact endpoint, status code 404, and clear reason."""
    provider = HormuudSmsProvider(
        base_url="https://smsapi.hormuud.com",
        username="test_user",
        password="test_password",
        sender_id="HAWLWADAAG",
        is_enabled=True,
    )

    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_resp.text = "404 Not Found"

    with patch("httpx.Client.post", return_value=mock_resp):
        res = provider.test_connection()
        assert res["success"] is False
        assert res["http_status"] == 404
        assert "POST https://smsapi.hormuud.com/token" in res["endpoint"]
        assert "Hormuud endpoint was not found" in res["reason"]
        assert "HTTP Status: 404" in res["message"]


# =========================================================================
# TEST 7: SEND SMS & MESSAGE ID PERSISTENCE IN POSTGRESQL
# =========================================================================

def test_hormuud_send_sms_success_and_message_id():
    """Verify single SMS dispatch to Hormuud SendSMS endpoint and MessageID capture."""
    tm = HormuudTokenManager()
    tm._cached_token = "valid_test_token"
    tm._expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

    provider = HormuudSmsProvider(
        base_url="https://smsapi.hormuud.com",
        username="valid_user",
        password="valid_password",
        sender_id="HAWLWADAAG",
        is_enabled=True,
        token_manager=tm,
    )

    mock_send_resp = MagicMock()
    mock_send_resp.status_code = 200
    mock_send_resp.json.return_value = {
        "ResponceCode": 200,
        "ResponceMessage": "Success",
        "Data": "MSG-HORMUUD-987654321",
    }

    with patch("httpx.Client.post", return_value=mock_send_resp) as mock_post:
        result = provider.send(
            recipient="+252 61 512 3456",
            message="Asc Waalidka, ardaygaaga maanta wuu joogay dugsiga.",
            extra_data={"refid": "HAWL-REF-001"}
        )

        assert result.status == "SENT"
        assert result.provider_message_id == "MSG-HORMUUD-987654321"
        assert result.provider_name == "Hormuud SMS"
        assert mock_post.call_count == 1
        
        # Verify JSON body passed to Hormuud
        called_args, called_kwargs = mock_post.call_args
        json_body = called_kwargs.get("json", {})
        assert json_body["mobile"] == "252615123456"
        assert json_body["senderid"] == "HAWLWADAAG"
        assert json_body["refid"] == "HAWL-REF-001"


# =========================================================================
# TEST 8: DELIVERY REPORT WEBHOOK CALLBACK (DLR)
# =========================================================================

def test_hormuud_delivery_report_webhook(client):
    """Verify delivery webhook from Hormuud updates PostgreSQL delivery record to DELIVERED."""
    db = SessionLocal()
    now = datetime.now(timezone.utc)

    # 1. Create a notification and delivery record
    notif = Notification(
        notification_type="ATTENDANCE_ABSENT",
        title="Maqnaansho",
        message="Test webhook alert",
        channel="SMS",
        status="SENT",
        guardian_phone="252615999888",
        created_at=now,
        attempt_count=1,
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)

    unique_msg_id = f"HORMUUD-MSG-DLR-{uuid.uuid4().hex[:8]}"
    delivery = NotificationDelivery(
        notification_id=notif.id,
        channel="SMS",
        recipient="252615999888",
        provider_name="Hormuud SMS",
        provider_message_id=unique_msg_id,
        status="SENT",
        attempt_number=1,
        sent_at=now,
        created_at=now,
    )
    db.add(delivery)
    db.commit()
    db.refresh(delivery)
    db.close()

    # 2. Simulate Hormuud Delivery Callback Webhook
    dlr_payload = {
        "messageid": unique_msg_id,
        "refid": f"HAWL-NOTIF-{notif.id}",
        "status": "DELIVERED",
        "delivery_date": datetime.now(timezone.utc).isoformat(),
        "ErrorCode": 0,
        "reason": "Delivered to handset",
    }

    resp = client.post("/api/v1/notifications/webhook/hormuud", json=dlr_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["status"] == "DELIVERED"
    assert data["notification_id"] == notif.id

    # 3. Verify database record
    db = SessionLocal()
    updated_notif = db.query(Notification).filter(Notification.id == notif.id).first()
    updated_del = db.query(NotificationDelivery).filter(NotificationDelivery.id == delivery.id).first()

    assert updated_del.status == "DELIVERED"
    assert updated_del.delivered_at is not None
    assert updated_notif.status == "DELIVERED"
    assert updated_notif.delivered_at is not None
    db.close()


# =========================================================================
# TEST 9: CHECK BALANCE API
# =========================================================================

def test_hormuud_check_balance_api(client, admin_token):
    """Verify Admin check balance endpoint."""
    with patch.object(
        HormuudSmsProvider,
        "check_balance",
        return_value={
            "success": True,
            "is_configured": True,
            "balance": "4500 SMS",
            "service": "smsapi",
            "last_checked": datetime.now(timezone.utc).isoformat(),
        }
    ):
        resp = client.get(
            "/api/v1/notifications/providers/hormuud/balance",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["balance"] == "4500 SMS"


# =========================================================================
# TEST 10: TEST CONNECTION DIAGNOSTIC API
# =========================================================================

def test_hormuud_test_connection_api(client, admin_token):
    """Verify Admin test connection endpoint."""
    with patch.object(
        HormuudSmsProvider,
        "test_connection",
        return_value={
            "success": True,
            "status": "CONNECTED",
            "message": "Successfully connected to Hormuud SMS Gateway (45.2 ms).",
            "response_time_ms": 45.2,
            "balance": "1000 SMS",
            "checked_at": datetime.now(timezone.utc).isoformat(),
        }
    ):
        resp = client.post(
            "/api/v1/notifications/providers/hormuud/test-connection",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["status"] == "CONNECTED"
        assert "Successfully connected" in data["message"]


# =========================================================================
# TEST 11: PERSONALIZED ATTENDANCE ABSENCE SMS DISPATCH
# =========================================================================

def test_personalized_attendance_sms_dispatch(client, admin_token):
    """Verify personalized absence notification resolves Somali placeholders and records in DB."""
    db = SessionLocal()
    # Create test student & class
    school_class = db.query(SchoolClass).filter(SchoolClass.status == "ACTIVE").first()
    if not school_class:
        school_class = SchoolClass(name="Form 4 A", code="F4-A", capacity=40, academic_year="2026/2027", status="ACTIVE")
        db.add(school_class)
        db.commit()

    student = db.query(Student).filter(Student.guardian_phone.isnot(None)).first()
    if not student:
        student = Student(
            admission_number="ADM-TEST-HORMUUD-01",
            first_name="Mohamed",
            last_name="Ali Mire",
            gender="MALE",
            guardian_name="Cabdi Mire",
            guardian_phone="+252615334455",
            status="ACTIVE",
        )
        db.add(student)
        db.commit()

    test_date = date(2026, 9, 20)

    # Clean old attendance
    db.query(Attendance).filter(Attendance.student_id == student.id, Attendance.date == test_date).delete()
    db.commit()

    att = Attendance(
        student_id=student.id,
        class_id=school_class.id,
        subject_id=1,
        teacher_id=1,
        academic_year="2026/2027",
        date=test_date,
        period="1",
        status="ABSENT",
    )
    db.add(att)
    db.commit()
    db.refresh(att)
    db.close()

    from app.services.providers.base_provider import DeliveryResult
    mock_del_res = DeliveryResult(
        status="SENT",
        provider_name="Hormuud SMS",
        provider_message_id="HORMUUD-ATT-001",
        sent_at=datetime.now(timezone.utc),
    )

    with patch.object(HormuudSmsProvider, "send", return_value=mock_del_res):
        resp = client.post(
            "/api/v1/notifications/attendance-alerts/notify",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "date": test_date.isoformat(),
                "target_type": "SELECTED_ATTENDANCES",
                "attendance_ids": [att.id],
                "channel": "SMS",
            }
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["sent_or_queued_count"] == 1

        # Verify message in PostgreSQL
        db = SessionLocal()
        notif = db.query(Notification).filter(Notification.related_attendance_id == att.id).first()
        assert notif is not None
        assert notif.status in ("SENT", "DELIVERED")
        assert student.full_name in notif.message
        assert "Asc" in notif.message
        db.close()


# =========================================================================
# TEST 12: DUPLICATE PREVENTION WITH IDEMPOTENCY KEY
# =========================================================================

def test_duplicate_prevention_with_idempotency_key(client, admin_token):
    """Verify duplicate alerts for the same absence are prevented safely."""
    db = SessionLocal()
    student = db.query(Student).first()
    test_date = date(2026, 9, 21)

    # Clean old records
    db.query(Attendance).filter(Attendance.student_id == student.id, Attendance.date == test_date).delete()
    db.commit()

    att = Attendance(
        student_id=student.id,
        class_id=1,
        subject_id=1,
        teacher_id=1,
        academic_year="2026/2027",
        date=test_date,
        period="1",
        status="ABSENT",
    )
    db.add(att)
    db.commit()
    db.refresh(att)
    db.close()

    from app.services.providers.base_provider import DeliveryResult
    mock_del_res = DeliveryResult(
        status="SENT",
        provider_name="Hormuud SMS",
        provider_message_id="HORMUUD-DUP-001",
        sent_at=datetime.now(timezone.utc),
    )

    with patch.object(HormuudSmsProvider, "send", return_value=mock_del_res):
        # First send
        r1 = client.post(
            "/api/v1/notifications/attendance-alerts/notify",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "date": test_date.isoformat(),
                "target_type": "SELECTED_ATTENDANCES",
                "attendance_ids": [att.id],
                "channel": "SMS",
            }
        )
        assert r1.status_code == 200
        d1 = r1.json()
        assert d1["sent_or_queued_count"] == 1

        # Second send (must be skipped as already notified)
        r2 = client.post(
            "/api/v1/notifications/attendance-alerts/notify",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "date": test_date.isoformat(),
                "target_type": "SELECTED_ATTENDANCES",
                "attendance_ids": [att.id],
                "channel": "SMS",
            }
        )
        assert r2.status_code == 200
        d2 = r2.json()
        assert d2["already_notified_count"] == 1
        assert d2["sent_or_queued_count"] == 0


# =========================================================================
# TEST 13: RETRY FAILED NOTIFICATION
# =========================================================================

def test_retry_failed_notification(client, admin_token):
    """Verify single notification retry functionality."""
    db = SessionLocal()
    notif = Notification(
        notification_type="CUSTOM",
        title="Retry Test",
        message="Testing retry mechanism",
        channel="SMS",
        status="FAILED",
        failure_reason="TEMPORARY_NETWORK_ERROR",
        guardian_phone="252615888777",
        created_at=datetime.now(timezone.utc),
        attempt_count=1,
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    db.close()

    from app.services.providers.base_provider import DeliveryResult
    mock_del_res = DeliveryResult(
        status="SENT",
        provider_name="Hormuud SMS",
        provider_message_id="HORMUUD-RETRY-SUCCESS",
        sent_at=datetime.now(timezone.utc),
    )

    with patch.object(HormuudSmsProvider, "send", return_value=mock_del_res):
        resp = client.post(
            f"/api/v1/notifications/{notif.id}/retry",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "SENT"
        assert data["attempt_count"] >= 2


# =========================================================================
# TEST 14: AUTHORIZATION (TEACHER & STUDENT FORBIDDEN)
# =========================================================================

def test_hormuud_endpoints_forbidden_for_teacher_and_student(client, teacher_token, student_token):
    """Verify Teacher and Student users receive 403 Forbidden for Admin notification routes."""
    # 1. Teacher access to test-connection -> 403
    r_teach = client.post(
        "/api/v1/notifications/providers/hormuud/test-connection",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert r_teach.status_code == 403

    # 2. Student access to test-connection -> 403
    r_stud = client.post(
        "/api/v1/notifications/providers/hormuud/test-connection",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert r_stud.status_code == 403

    # 3. Teacher access to balance -> 403
    r_bal = client.get(
        "/api/v1/notifications/providers/hormuud/balance",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert r_bal.status_code == 403


# =========================================================================
# TEST 15: SECURITY - CREDENTIALS NEVER EXPOSED IN API RESPONSES
# =========================================================================

def test_hormuud_credentials_never_exposed_in_api(client, admin_token):
    """Verify API responses for settings and status mask credentials."""
    resp = client.get(
        "/api/v1/notifications/providers/hormuud/status",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "password" not in data
    assert "access_token" not in data
    assert "api_secret" not in data


# =========================================================================
# TEST 16: VERIFY ALL OFFICIAL HORMUUD ENDPOINT PATHS & STRUCTURES
# =========================================================================

def test_hormuud_all_five_endpoint_paths_and_structures():
    """
    Verify exact endpoint paths required by Hormuud documentation:
    1. POST /token
    2. POST /api/SendSMS
    3. POST /api/Outbound/SendBulkSMS
    4. POST /api/checkbalance
    5. POST /api/GetDelivery
    """
    tm = HormuudTokenManager()
    tm._cached_token = "valid_test_token"
    tm._expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

    provider = HormuudSmsProvider(
        base_url="https://smsapi.hormuud.com",
        username="test_user",
        password="test_password",
        sender_id="HAWLWADAAG",
        is_enabled=True,
        token_manager=tm,
    )

    # 1. Test /token endpoint call structure
    mock_token_resp = MagicMock()
    mock_token_resp.status_code = 200
    mock_token_resp.json.return_value = {"access_token": "token_abc_123", "expires_in": 3600}

    with patch("httpx.Client.post", return_value=mock_token_resp) as mock_post:
        fresh_tm = HormuudTokenManager()
        token, err = fresh_tm.get_token(
            base_url="https://smsapi.hormuud.com",
            username="test_user",
            password="test_password",
            force_refresh=True
        )
        assert token == "token_abc_123"
        call_url, kwargs = mock_post.call_args[0][0], mock_post.call_args[1]
        assert call_url == "https://smsapi.hormuud.com/token"
        assert kwargs["data"]["grant_type"] == "password"
        assert kwargs["headers"]["Content-Type"] == "application/x-www-form-urlencoded"

    # 2. Test /api/SendSMS endpoint call structure
    mock_sms_resp = MagicMock()
    mock_sms_resp.status_code = 200
    mock_sms_resp.json.return_value = {"ResponceCode": 200, "ResponceMessage": "Success", "Data": "MSG-001"}

    with patch("httpx.Client.post", return_value=mock_sms_resp) as mock_post:
        res = provider.send(recipient="252615112233", message="Hello guardian")
        assert res.status == "SENT"
        call_url, kwargs = mock_post.call_args[0][0], mock_post.call_args[1]
        assert call_url == "https://smsapi.hormuud.com/api/SendSMS"
        assert kwargs["headers"]["Authorization"] == "Bearer valid_test_token"
        assert kwargs["json"]["mobile"] == "252615112233"
        assert kwargs["json"]["mType"] == -1
        assert kwargs["json"]["eType"] == -1
        assert kwargs["json"]["validity"] == 0
        assert kwargs["json"]["delivery"] == 0
        assert "RequestDate" in kwargs["json"]

    # 3. Test /api/Outbound/SendBulkSMS endpoint call structure
    mock_bulk_resp = MagicMock()
    mock_bulk_resp.status_code = 200
    mock_bulk_resp.json.return_value = {"Status": "OK"}

    with patch("httpx.Client.post", return_value=mock_bulk_resp) as mock_post:
        res = provider.send_bulk_outbound([{"mobile": "252615112233", "message": "Bulk 1"}])
        assert res["success"] is True
        call_url, kwargs = mock_post.call_args[0][0], mock_post.call_args[1]
        assert call_url == "https://smsapi.hormuud.com/api/Outbound/SendBulkSMS"
        assert kwargs["headers"]["Authorization"] == "Bearer valid_test_token"

    # 4. Test /api/checkbalance endpoint call structure
    mock_bal_resp = MagicMock()
    mock_bal_resp.status_code = 200
    mock_bal_resp.json.return_value = {"balance": "5000"}

    with patch("httpx.Client.post", return_value=mock_bal_resp) as mock_post:
        res = provider.check_balance()
        assert res["success"] is True
        call_url, kwargs = mock_post.call_args[0][0], mock_post.call_args[1]
        assert call_url == "https://smsapi.hormuud.com/api/checkbalance"
        assert kwargs["headers"]["Authorization"] == "Bearer valid_test_token"
        assert kwargs["json"] == {"service": "smsapi"}

    # 5. Test /api/GetDelivery endpoint call structure
    mock_dlr_resp = MagicMock()
    mock_dlr_resp.status_code = 200
    mock_dlr_resp.json.return_value = {"Status": "DELIVERED"}

    with patch("httpx.Client.post", return_value=mock_dlr_resp) as mock_post:
        res = provider.get_delivery(message_id="MSG-001", ref_id="REF-001")
        assert res["success"] is True
        call_url, kwargs = mock_post.call_args[0][0], mock_post.call_args[1]
        assert call_url == "https://smsapi.hormuud.com/api/GetDelivery"
        assert kwargs["headers"]["Authorization"] == "Bearer valid_test_token"
        assert kwargs["json"] == {"messageid": "MSG-001", "refid": "REF-001"}

