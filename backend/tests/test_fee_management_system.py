import pytest
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import create_application
from app.core.database import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.models.student import Student
from app.models.school_class import SchoolClass
from app.models.student_enrollment import StudentEnrollment
from app.models.fee import FeeStructure, StudentFee, FeePayment
from app.models.notification import Notification
from app.core.security import create_access_token
from app.services.providers.base_provider import DeliveryResult
from app.services.providers.hormuud_sms_provider import HormuudSmsProvider


@pytest.fixture(scope="module")
def app():
    return create_application()


@pytest.fixture(scope="module")
def client(app):
    return TestClient(app)


@pytest.fixture(scope="module")
def setup_users_and_tokens():
    db = SessionLocal()
    # 1. Admin
    admin_role = db.query(Role).filter(Role.name == "ADMIN").first()
    if not admin_role:
        admin_role = Role(name="ADMIN", description="Administrator")
        db.add(admin_role)
        db.commit()

    admin = db.query(User).filter(User.username == "admin_fee_test").first()
    if not admin:
        admin = User(
            username="admin_fee_test",
            email="admin_fee@hawlwadaag.edu.so",
            full_name="Finance Administrator",
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

    teacher = db.query(User).filter(User.username == "teacher_fee_test").first()
    if not teacher:
        teacher = User(
            username="teacher_fee_test",
            email="teacher_fee@hawlwadaag.edu.so",
            full_name="Teacher Fee Tester",
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

    student_user = db.query(User).filter(User.username == "student_fee_test").first()
    if not student_user:
        student_user = User(
            username="student_fee_test",
            email="student_fee@hawlwadaag.edu.so",
            full_name="Student Fee Tester",
            hashed_password="fakehashstudent",
            is_active=True,
        )
        student_user.roles.append(student_role)
        db.add(student_user)
        db.commit()
        db.refresh(student_user)

    admin_token = create_access_token(
        subject=str(admin.id),
        claims={"username": admin.username, "roles": ["ADMIN"], "is_superuser": True}
    )
    teacher_token = create_access_token(
        subject=str(teacher.id),
        claims={"username": teacher.username, "roles": ["TEACHER"], "is_superuser": False}
    )
    student_token = create_access_token(
        subject=str(student_user.id),
        claims={"username": student_user.username, "roles": ["STUDENT"], "is_superuser": False}
    )

    db.close()
    return {
        "admin_token": admin_token,
        "teacher_token": teacher_token,
        "student_token": student_token,
        "admin_id": admin.id,
    }


# =========================================================================
# TEST SUITE: PROFESSIONAL FEES & FINANCIAL MANAGEMENT
# =========================================================================

def test_create_fee_structure_with_frequency(client, setup_users_and_tokens):
    """1. Admin creates a fee structure with frequency, class, and due date."""
    headers = {"Authorization": f"Bearer {setup_users_and_tokens['admin_token']}"}
    due = (date.today() + timedelta(days=30)).isoformat()

    payload = {
        "name": "Term 1 Tuition 2026/2027",
        "academic_year": "2026/2027",
        "amount": 25.00,
        "frequency": "Monthly",
        "due_date": due,
        "description": "Monthly tuition fee for primary and secondary sections",
        "status": "ACTIVE",
    }
    resp = client.post("/api/v1/fees/structures", json=payload, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Term 1 Tuition 2026/2027"
    assert data["frequency"] == "Monthly"
    assert float(data["amount"]) == 25.00
    assert data["status"] == "ACTIVE"


def test_fee_structure_validation_positive_amount(client, setup_users_and_tokens):
    """2. Backend rejects zero or negative fee amounts."""
    headers = {"Authorization": f"Bearer {setup_users_and_tokens['admin_token']}"}
    payload = {
        "name": "Invalid Zero Fee",
        "academic_year": "2026/2027",
        "amount": 0.00,
        "frequency": "One-Time",
        "due_date": date.today().isoformat(),
    }
    resp = client.post("/api/v1/fees/structures", json=payload, headers=headers)
    assert resp.status_code == 422


def test_assign_fee_to_single_student(client, setup_users_and_tokens):
    """3. Assign fee to single student generates invoice with unique INV-YYYY-XXXXXX number."""
    db = SessionLocal()
    student = db.query(Student).filter(Student.status == "ACTIVE").first()
    if not student:
        student = Student(
            admission_number="ADM-FEE-TEST-001",
            first_name="Guled",
            last_name="Farah",
            gender="MALE",
            guardian_name="Farah Warsame",
            guardian_phone="252615443322",
            status="ACTIVE",
        )
        db.add(student)
        db.commit()
        db.refresh(student)

    # Create structure
    struct = FeeStructure(
        name=f"Exam Fee Special {datetime.now().microsecond}",
        academic_year="2026/2027",
        amount=Decimal("15.00"),
        frequency="Term",
        due_date=date.today() + timedelta(days=15),
        status="ACTIVE",
    )
    db.add(struct)
    db.commit()
    db.refresh(struct)
    db.close()

    headers = {"Authorization": f"Bearer {setup_users_and_tokens['admin_token']}"}
    assign_payload = {
        "target_type": "SINGLE_STUDENT",
        "student_id": student.id,
        "fee_structure_id": struct.id,
        "academic_year": "2026/2027",
    }
    resp = client.post("/api/v1/fees/invoices/assign", json=assign_payload, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["success"] is True
    assert data["created_count"] == 1
    assert len(data["created_invoices"]) == 1
    inv = data["created_invoices"][0]
    assert inv["invoice_number"].startswith("INV-")
    assert inv["balance_remaining"] == 15.0
    assert inv["status"] == "PENDING"


def test_assign_fee_to_entire_class_and_total_calculation(client, setup_users_and_tokens):
    """4. Bulk assign fee to entire class calculates total amount billed correctly."""
    db = SessionLocal()
    # Create or get class
    cls = db.query(SchoolClass).filter(SchoolClass.status == "ACTIVE").first()
    if not cls:
        cls = SchoolClass(name="Grade 8 Alpha", code="G8-A", capacity=35, academic_year="2026/2027", status="ACTIVE")
        db.add(cls)
        db.commit()
        db.refresh(cls)

    created_student_ids = []
    try:
        # Ensure 3 students in this class
        for i in range(3):
            adm = f"ADM-CLS-FEE-{i}-{datetime.now().microsecond}"
            st = Student(
                admission_number=adm,
                first_name=f"StudentClass{i}",
                last_name="Ahmed",
                gender="MALE",
                guardian_name=f"Guardian {i}",
                guardian_phone="252615998877",
                status="ACTIVE",
            )
            db.add(st)
            db.commit()
            db.refresh(st)
            created_student_ids.append(st.id)

            en = StudentEnrollment(
                student_id=st.id,
                class_id=cls.id,
                academic_year="2026/2027",
                status="ACTIVE",
            )
            db.add(en)
        db.commit()

        struct = FeeStructure(
            name=f"Class Fee {datetime.now().microsecond}",
            academic_year="2026/2027",
            class_id=cls.id,
            amount=Decimal("20.00"),
            frequency="Monthly",
            due_date=date.today() + timedelta(days=20),
            status="ACTIVE",
        )
        db.add(struct)
        db.commit()
        db.refresh(struct)
        db.close()

        headers = {"Authorization": f"Bearer {setup_users_and_tokens['admin_token']}"}
        assign_payload = {
            "target_type": "CLASS",
            "class_id": cls.id,
            "fee_structure_id": struct.id,
            "academic_year": "2026/2027",
        }
        resp = client.post("/api/v1/fees/invoices/assign", json=assign_payload, headers=headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["success"] is True
        assert data["created_count"] >= 3
        assert data["total_amount_billed"] >= 60.0
    finally:
        if created_student_ids:
            clean_db = SessionLocal()
            clean_db.query(FeePayment).filter(FeePayment.student_fee_id.in_(clean_db.query(StudentFee.id).filter(StudentFee.student_id.in_(created_student_ids)))).delete(synchronize_session=False)
            clean_db.query(StudentFee).filter(StudentFee.student_id.in_(created_student_ids)).delete(synchronize_session=False)
            clean_db.query(StudentEnrollment).filter(StudentEnrollment.student_id.in_(created_student_ids)).delete(synchronize_session=False)
            clean_db.query(Student).filter(Student.id.in_(created_student_ids)).delete(synchronize_session=False)
            clean_db.commit()
            clean_db.close()


def test_duplicate_invoice_assignment_prevented(client, setup_users_and_tokens):
    """5. Assigning the same fee structure to the same student again skips duplicate creation."""
    db = SessionLocal()
    st = db.query(Student).first()
    struct = FeeStructure(
        name=f"Dup Test Fee {datetime.now().microsecond}",
        academic_year="2026/2027",
        amount=Decimal("30.00"),
        frequency="Annual",
        due_date=date.today() + timedelta(days=10),
        status="ACTIVE",
    )
    db.add(struct)
    db.commit()
    db.refresh(struct)
    db.close()

    headers = {"Authorization": f"Bearer {setup_users_and_tokens['admin_token']}"}
    assign_payload = {
        "target_type": "SINGLE_STUDENT",
        "student_id": st.id,
        "fee_structure_id": struct.id,
    }
    # First attempt -> created_count = 1
    r1 = client.post("/api/v1/fees/invoices/assign", json=assign_payload, headers=headers)
    assert r1.status_code == 201
    assert r1.json()["created_count"] == 1

    # Second attempt -> skipped_count = 1, created_count = 0
    r2 = client.post("/api/v1/fees/invoices/assign", json=assign_payload, headers=headers)
    assert r2.status_code == 201
    assert r2.json()["created_count"] == 0
    assert r2.json()["skipped_count"] == 1


def test_record_partial_and_full_payment(client, setup_users_and_tokens):
    """6, 7 & 8. Partial payment updates balance to PARTIALLY_PAID, full payment transitions to PAID."""
    db = SessionLocal()
    st = db.query(Student).first()
    struct = FeeStructure(
        name=f"Tuition Step Payment {datetime.now().microsecond}",
        academic_year="2026/2027",
        amount=Decimal("50.00"),
        frequency="Monthly",
        due_date=date.today() + timedelta(days=10),
        status="ACTIVE",
    )
    db.add(struct)
    db.commit()

    inv = StudentFee(
        invoice_number=f"INV-TEST-{datetime.now().microsecond}",
        student_id=st.id,
        fee_structure_id=struct.id,
        academic_year="2026/2027",
        amount_due=Decimal("50.00"),
        discount_amount=Decimal("0.00"),
        due_date=date.today() + timedelta(days=10),
        status="PENDING",
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)
    db.close()

    headers = {"Authorization": f"Bearer {setup_users_and_tokens['admin_token']}"}

    # Step 1: Partial payment of $20
    pay1_payload = {
        "student_fee_id": inv.id,
        "amount_paid": 20.00,
        "payment_date": date.today().isoformat(),
        "payment_method": "EVC_PLUS",
        "reference_number": "EVC-TXN-101",
        "notes": "First installment via EVC Plus",
    }
    r1 = client.post("/api/v1/fees/payments", json=pay1_payload, headers=headers)
    assert r1.status_code == 201
    p1 = r1.json()
    assert p1["receipt_number"].startswith("RCT-")
    assert float(p1["amount_paid"]) == 20.00

    # Verify invoice status
    inv_check = client.get(f"/api/v1/fees/invoices/{inv.id}", headers=headers).json()
    assert inv_check["status"] == "PARTIALLY_PAID"
    assert inv_check["total_paid"] == 20.00
    assert inv_check["balance_remaining"] == 30.00

    # Step 2: Pay remaining $30
    pay2_payload = {
        "student_fee_id": inv.id,
        "amount_paid": 30.00,
        "payment_date": date.today().isoformat(),
        "payment_method": "CASH",
        "reference_number": "CASH-REC-102",
        "notes": "Final settlement",
    }
    r2 = client.post("/api/v1/fees/payments", json=pay2_payload, headers=headers)
    assert r2.status_code == 201

    # Verify invoice transitioned to PAID
    inv_final = client.get(f"/api/v1/fees/invoices/{inv.id}", headers=headers).json()
    assert inv_final["status"] == "PAID"
    assert inv_final["total_paid"] == 50.00
    assert inv_final["balance_remaining"] == 0.00


def test_payment_validation_negative_and_overpayment_rejected(client, setup_users_and_tokens):
    """9 & 10. Rejects zero, negative payments, and payments greater than remaining balance."""
    db = SessionLocal()
    st = db.query(Student).first()
    struct = FeeStructure(
        name=f"Overpay Test {datetime.now().microsecond}",
        academic_year="2026/2027",
        amount=Decimal("40.00"),
        frequency="Monthly",
        due_date=date.today() + timedelta(days=10),
        status="ACTIVE",
    )
    db.add(struct)
    db.commit()

    inv = StudentFee(
        invoice_number=f"INV-OVERPAY-{datetime.now().microsecond}",
        student_id=st.id,
        fee_structure_id=struct.id,
        academic_year="2026/2027",
        amount_due=Decimal("40.00"),
        discount_amount=Decimal("0.00"),
        due_date=date.today() + timedelta(days=10),
        status="PENDING",
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)
    db.close()

    headers = {"Authorization": f"Bearer {setup_users_and_tokens['admin_token']}"}

    # 1. Negative payment -> 422
    r_neg = client.post(
        "/api/v1/fees/payments",
        json={"student_fee_id": inv.id, "amount_paid": -10.00, "payment_method": "CASH"},
        headers=headers,
    )
    assert r_neg.status_code == 422

    # 2. Zero payment -> 422
    r_zero = client.post(
        "/api/v1/fees/payments",
        json={"student_fee_id": inv.id, "amount_paid": 0.00, "payment_method": "CASH"},
        headers=headers,
    )
    assert r_zero.status_code == 422

    # 3. Overpayment ($100 on $40 invoice) -> 422
    r_over = client.post(
        "/api/v1/fees/payments",
        json={"student_fee_id": inv.id, "amount_paid": 100.00, "payment_method": "CASH"},
        headers=headers,
    )
    assert r_over.status_code == 422
    assert "exceeds" in r_over.json()["detail"]


def test_official_receipt_payload(client, setup_users_and_tokens):
    """11. Verified payment returns single-page official receipt payload."""
    db = SessionLocal()
    st = db.query(Student).first()
    struct = FeeStructure(
        name=f"Receipt Test Fee {datetime.now().microsecond}",
        academic_year="2026/2027",
        amount=Decimal("35.00"),
        frequency="Term",
        due_date=date.today() + timedelta(days=5),
        status="ACTIVE",
    )
    db.add(struct)
    db.commit()

    inv = StudentFee(
        invoice_number=f"INV-RCT-{datetime.now().microsecond}",
        student_id=st.id,
        fee_structure_id=struct.id,
        academic_year="2026/2027",
        amount_due=Decimal("35.00"),
        discount_amount=Decimal("0.00"),
        due_date=date.today() + timedelta(days=5),
        status="PENDING",
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)
    db.close()

    headers = {"Authorization": f"Bearer {setup_users_and_tokens['admin_token']}"}
    p_res = client.post(
        "/api/v1/fees/payments",
        json={"student_fee_id": inv.id, "amount_paid": 35.00, "payment_method": "EDAHAB", "reference_number": "ED-7788"},
        headers=headers,
    ).json()

    # Query official receipt endpoint
    rct_resp = client.get(f"/api/v1/fees/payments/{p_res['id']}/receipt", headers=headers)
    assert rct_resp.status_code == 200
    rct = rct_resp.json()
    assert rct["receipt_number"] == p_res["receipt_number"]
    assert rct["student_name"] == st.full_name
    assert rct["payment_method"] == "EDAHAB"
    assert rct["school_name"] == "Hawlwadaag Primary and Secondary School"
    assert rct["amount_paid"] == 35.0
    assert rct["remaining_balance"] == 0.0


def test_overdue_invoice_detection(client, setup_users_and_tokens):
    """12. Invoices with due_date < today and balance > 0 are marked as overdue."""
    db = SessionLocal()
    st = db.query(Student).first()
    struct = FeeStructure(
        name=f"Past Due Fee {datetime.now().microsecond}",
        academic_year="2026/2027",
        amount=Decimal("45.00"),
        frequency="Monthly",
        due_date=date.today() - timedelta(days=5),  # in the past
        status="ACTIVE",
    )
    db.add(struct)
    db.commit()

    inv = StudentFee(
        invoice_number=f"INV-PASTDUE-{datetime.now().microsecond}",
        student_id=st.id,
        fee_structure_id=struct.id,
        academic_year="2026/2027",
        amount_due=Decimal("45.00"),
        discount_amount=Decimal("0.00"),
        due_date=date.today() - timedelta(days=5),
        status="OVERDUE",
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)
    db.close()

    headers = {"Authorization": f"Bearer {setup_users_and_tokens['admin_token']}"}
    resp = client.get("/api/v1/fees/invoices?status=OVERDUE", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert any(item["id"] == inv.id and item["is_overdue"] is True for item in data["items"])


def test_payment_cancellation_and_balance_restoration(client, setup_users_and_tokens):
    """13. Voiding a payment updates payment status to CANCELLED and restores invoice balance."""
    db = SessionLocal()
    st = db.query(Student).first()
    struct = FeeStructure(
        name=f"Void Test Fee {datetime.now().microsecond}",
        academic_year="2026/2027",
        amount=Decimal("60.00"),
        frequency="Monthly",
        due_date=date.today() + timedelta(days=10),
        status="ACTIVE",
    )
    db.add(struct)
    db.commit()

    inv = StudentFee(
        invoice_number=f"INV-VOID-{datetime.now().microsecond}",
        student_id=st.id,
        fee_structure_id=struct.id,
        academic_year="2026/2027",
        amount_due=Decimal("60.00"),
        discount_amount=Decimal("0.00"),
        due_date=date.today() + timedelta(days=10),
        status="PENDING",
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)
    db.close()

    headers = {"Authorization": f"Bearer {setup_users_and_tokens['admin_token']}"}
    p_res = client.post(
        "/api/v1/fees/payments",
        json={"student_fee_id": inv.id, "amount_paid": 60.00, "payment_method": "CASH"},
        headers=headers,
    ).json()

    # Cancel the payment
    cancel_res = client.post(
        f"/api/v1/fees/payments/{p_res['id']}/cancel?reason=Mistaken+Entry",
        headers=headers,
    )
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "CANCELLED"

    # Verify invoice balance is restored to 60.00 and status returned to PENDING
    inv_check = client.get(f"/api/v1/fees/invoices/{inv.id}", headers=headers).json()
    assert inv_check["status"] == "PENDING"
    assert inv_check["balance_remaining"] == 60.00
    assert inv_check["total_paid"] == 0.00


def test_financial_dashboard_kpis_and_aggregates(client, setup_users_and_tokens):
    """14, 15, 16 & 17. Telemetry KPIs, Class summary, and Payment method breakdown reflect PostgreSQL state."""
    headers = {"Authorization": f"Bearer {setup_users_and_tokens['admin_token']}"}

    # Summary KPIs
    s_resp = client.get("/api/v1/fees/summary", headers=headers)
    assert s_resp.status_code == 200
    sum_data = s_resp.json()
    assert sum_data["total_billed"] >= 0
    assert sum_data["total_collected"] >= 0
    assert sum_data["total_outstanding"] >= 0

    # Class summary
    c_resp = client.get("/api/v1/fees/reports/class-summary", headers=headers)
    assert c_resp.status_code == 200
    assert "classes" in c_resp.json()

    # Payment methods breakdown
    pm_resp = client.get("/api/v1/fees/reports/payment-methods", headers=headers)
    assert pm_resp.status_code == 200
    assert "methods" in pm_resp.json()

    # Monthly trends
    t_resp = client.get("/api/v1/fees/reports/collection-trends", headers=headers)
    assert t_resp.status_code == 200
    assert "trends" in t_resp.json()


def test_student_financial_profile_ledger(client, setup_users_and_tokens):
    """18. Retrieve complete student financial statement."""
    db = SessionLocal()
    st = db.query(Student).first()
    db.close()

    headers = {"Authorization": f"Bearer {setup_users_and_tokens['admin_token']}"}
    resp = client.get(f"/api/v1/fees/student/{st.id}", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["student_id"] == st.id
    assert "invoices" in data
    assert "payments" in data


def test_guardian_fee_sms_preview_and_send(client, setup_users_and_tokens):
    """19 & 20. Guardian fee reminder SMS preview and dispatch via Hormuud integration."""
    headers = {"Authorization": f"Bearer {setup_users_and_tokens['admin_token']}"}

    # 1. Preview
    prev_resp = client.post("/api/v1/fees/notifications/preview?target_type=ALL_OUTSTANDING", headers=headers)
    assert prev_resp.status_code == 200
    prev_data = prev_resp.json()
    assert "total_students" in prev_data
    assert "eligible_count" in prev_data

    # 2. Send SMS with Hormuud mock
    mock_del_res = DeliveryResult(
        status="SENT",
        provider_name="Hormuud SMS",
        provider_message_id="HORMUUD-FEE-MSG-01",
        sent_at=datetime.now(timezone.utc),
    )
    with patch.object(HormuudSmsProvider, "send", return_value=mock_del_res):
        send_resp = client.post(
            "/api/v1/fees/notifications/send",
            json={"target_type": "ALL_OUTSTANDING"},
            headers=headers,
        )
        assert send_resp.status_code == 200
        send_data = send_resp.json()
        assert send_data["success"] is True


def test_unauthorized_access_forbidden_for_teachers_and_students(client, setup_users_and_tokens):
    """21. Teachers and students are forbidden (HTTP 403) from administrative finance routes."""
    teach_headers = {"Authorization": f"Bearer {setup_users_and_tokens['teacher_token']}"}
    stud_headers = {"Authorization": f"Bearer {setup_users_and_tokens['student_token']}"}

    # Teacher cannot create fee structure
    r1 = client.post("/api/v1/fees/structures", json={}, headers=teach_headers)
    assert r1.status_code == 403

    # Teacher cannot record payment
    r2 = client.post("/api/v1/fees/payments", json={}, headers=teach_headers)
    assert r2.status_code == 403

    # Student cannot view summary KPI
    r3 = client.get("/api/v1/fees/summary", headers=stud_headers)
    assert r3.status_code == 403


def test_export_financial_csv(client, setup_users_and_tokens):
    """22. Export invoices ledger to CSV."""
    headers = {"Authorization": f"Bearer {setup_users_and_tokens['admin_token']}"}
    resp = client.get("/api/v1/fees/export", headers=headers)
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/csv")
    content = resp.text
    assert "Invoice Number" in content
    assert "Remaining Balance" in content


def test_delete_fee_structure_success(client, setup_users_and_tokens):
    """23. Admin can delete an existing fee structure."""
    headers = {"Authorization": f"Bearer {setup_users_and_tokens['admin_token']}"}
    due = (date.today() + timedelta(days=30)).isoformat()
    payload = {
        "name": "Fee To Delete",
        "academic_year": "2026/2027",
        "amount": 50.00,
        "frequency": "Monthly",
        "due_date": due,
    }
    create_resp = client.post("/api/v1/fees/structures", json=payload, headers=headers)
    assert create_resp.status_code == 201
    struct_id = create_resp.json()["id"]

    del_resp = client.delete(f"/api/v1/fees/structures/{struct_id}", headers=headers)
    assert del_resp.status_code == 200
    assert del_resp.json()["success"] is True

    # Confirm it is no longer returned in list
    list_resp = client.get("/api/v1/fees/structures", headers=headers)
    ids = [s["id"] for s in list_resp.json()]
    assert struct_id not in ids

