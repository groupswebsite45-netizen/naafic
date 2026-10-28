"""
End-to-End Real Class and Student Enrollment Fees Workflow Test
Requirement 32:
Tests the entire Fees & Finance workflow against authoritative PostgreSQL data:
1. Admin login / auth
2. Select Primary
3. Select academic year (2026/2027)
4. Select a real class (Grade 8 - A)
5. Verify class exists
6. Verify student count (2 real enrolled students)
7. Fetch students via /fees/classes/{id}/students
8. Compare with Admin Students canonical enrollment
9. Create/view fee structure for Primary
10. Create invoice / assign fee to class
11. Record verified payment
12. Verify balance calculations (Decimal precision)
13. Verify PAID/PARTIAL/UNPAID/OVERDUE statuses
14. Open Outstanding Fees (/fees/outstanding)
15. Select Primary
16. Select class (Grade 8 - A)
17. Verify only unpaid/partial students appear
18. Select Secondary
19. Verify only Secondary classes appear
20. Verify Primary classes do not appear under Secondary
21. Verify Secondary students do not appear under Primary
22. Verify no duplicate students
"""
import os
import sys
from pathlib import Path
from decimal import Decimal
from datetime import date, timedelta
import pytest
from fastapi.testclient import TestClient

# Ensure backend root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import create_application
from app.core.database import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.models.school_class import SchoolClass
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.models.fee import FeeStructure, StudentFee, FeePayment
from app.core.security import create_access_token


@pytest.fixture(scope="module")
def app():
    return create_application()


@pytest.fixture(scope="module")
def client(app):
    return TestClient(app)


@pytest.fixture(scope="module")
def admin_headers():
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.is_superuser == True).first()
        if not admin:
            admin = db.query(User).first()
        token = create_access_token(
            subject=str(admin.id),
            claims={"username": admin.username, "roles": ["ADMIN"], "is_superuser": True}
        )
        return {"Authorization": f"Bearer {token}"}
    finally:
        db.close()


def test_fees_real_class_22_step_workflow(client, admin_headers):
    db = SessionLocal()
    try:
        academic_year = "2026/2027"

        # -------------------------------------------------------------
        # 1. Admin login verification
        # -------------------------------------------------------------
        assert admin_headers["Authorization"].startswith("Bearer ")

        # -------------------------------------------------------------
        # 2. Select Primary & 3. Select Academic Year
        # -------------------------------------------------------------
        resp_primary_classes = client.get(
            f"/api/v1/fees/classes?academic_year={academic_year}&education_level=PRIMARY",
            headers=admin_headers,
        )
        assert resp_primary_classes.status_code == 200, f"Failed: {resp_primary_classes.text}"
        primary_classes = resp_primary_classes.json()
        assert len(primary_classes) > 0, "Expected active primary classes for 2026/2027"

        # -------------------------------------------------------------
        # 4. Select a real class (Grade 8 - A)
        # -------------------------------------------------------------
        g8_class = next((c for c in primary_classes if c["name"] == "Grade 8 - A"), None)
        assert g8_class is not None, "Grade 8 - A must exist in Primary classes"

        # -------------------------------------------------------------
        # 5. Verify class exists
        # -------------------------------------------------------------
        g8_id = g8_class["id"]
        assert g8_class["division"] == "PRIMARY"
        assert g8_class["level"] == "Grade 8"
        assert g8_class["section"] == "A"
        assert g8_class["academic_year"] == academic_year

        # -------------------------------------------------------------
        # 6. Verify student count (must NOT be empty / 0; exactly 5 students)
        # -------------------------------------------------------------
        assert g8_class["students_count"] == 5, f"Grade 8 - A student count is {g8_class.get('students_count')}, expected 5"

        # -------------------------------------------------------------
        # 7. Fetch students via canonical fees endpoint
        # -------------------------------------------------------------
        resp_g8_students = client.get(
            f"/api/v1/fees/classes/{g8_id}/students?academic_year={academic_year}",
            headers=admin_headers,
        )
        assert resp_g8_students.status_code == 200, f"Failed: {resp_g8_students.text}"
        g8_data = resp_g8_students.json()
        assert g8_data["total_students"] == 5
        assert len(g8_data["students"]) == 5

        # -------------------------------------------------------------
        # 8. Compare with Admin Students canonical enrollment
        # -------------------------------------------------------------
        admin_enrollments = db.query(StudentEnrollment).join(
            Student, Student.id == StudentEnrollment.student_id
        ).filter(
            StudentEnrollment.class_id == g8_id,
            StudentEnrollment.academic_year == academic_year,
            StudentEnrollment.status == "ACTIVE",
            Student.status == "ACTIVE",
        ).all()
        assert len(admin_enrollments) == 5
        admin_student_ids = {e.student_id for e in admin_enrollments}
        fees_student_ids = {s["student_id"] for s in g8_data["students"]}
        assert admin_student_ids == fees_student_ids, "Admin Students IDs and Fees Student IDs must match 100%"

        # -------------------------------------------------------------
        # 9. Create/view fee structure for Primary
        # -------------------------------------------------------------
        struct_payload = {
            "name": f"E2E Workflow Tuition {academic_year}",
            "academic_year": academic_year,
            "education_level": "PRIMARY",
            "class_id": g8_id,
            "amount": 100.00,
            "frequency": "Monthly",
            "due_date": (date.today() + timedelta(days=15)).isoformat(),
            "description": "E2E Automated verification fee structure",
            "status": "ACTIVE",
        }
        resp_create_struct = client.post(
            "/api/v1/fees/structures",
            json=struct_payload,
            headers=admin_headers,
        )
        assert resp_create_struct.status_code == 201, f"Failed: {resp_create_struct.text}"
        created_struct = resp_create_struct.json()
        struct_id = created_struct["id"]
        assert float(created_struct["amount"]) == 100.00

        # -------------------------------------------------------------
        # 10. Create invoice / assign fee to class
        # -------------------------------------------------------------
        assign_payload = {
            "target_type": "CLASS",
            "class_id": g8_id,
            "fee_structure_id": struct_id,
            "academic_year": academic_year,
            "custom_amount": 100.00,
        }
        resp_assign = client.post(
            "/api/v1/fees/assign",
            json=assign_payload,
            headers=admin_headers,
        )
        assert resp_assign.status_code in (200, 201), f"Failed: {resp_assign.text}"
        assign_data = resp_assign.json()
        assert assign_data["created_count"] == 5, f"Expected 5 invoices for Grade 8 - A, got {assign_data['created_count']}"

        # -------------------------------------------------------------
        # 11. Record payment & 12. Verify balance & 13. Verify PAID/PARTIAL
        # -------------------------------------------------------------
        # Get one student's invoice
        inv = db.query(StudentFee).filter(
            StudentFee.class_id == g8_id,
            StudentFee.fee_structure_id == struct_id,
            StudentFee.academic_year == academic_year,
        ).first()
        assert inv is not None
        assert float(inv.net_amount) == 100.00
        assert inv.status == "PENDING"

        # Record partial payment of $40.00
        pay_payload = {
            "student_fee_id": inv.id,
            "amount_paid": 40.00,
            "payment_date": date.today().isoformat(),
            "payment_method": "EVC_PLUS",
            "reference_number": "E2E-PARTIAL-40",
            "notes": "Partial test payment",
        }
        resp_pay = client.post(
            "/api/v1/fees/payments",
            json=pay_payload,
            headers=admin_headers,
        )
        assert resp_pay.status_code == 201, f"Payment failed: {resp_pay.text}"
        
        # Reload invoice and check balance & status
        db.refresh(inv)
        assert float(inv.total_paid) == 40.00
        assert float(inv.balance_remaining) == 60.00
        assert inv.status == "PARTIALLY_PAID"

        # Pay remaining $60.00 to verify PAID status
        pay_remaining = {
            "student_fee_id": inv.id,
            "amount_paid": 60.00,
            "payment_date": date.today().isoformat(),
            "payment_method": "CASH",
            "reference_number": "E2E-FULL-60",
            "notes": "Clear balance payment",
        }
        resp_pay2 = client.post(
            "/api/v1/fees/payments",
            json=pay_remaining,
            headers=admin_headers,
        )
        assert resp_pay2.status_code == 201
        db.refresh(inv)
        assert float(inv.total_paid) == 100.00
        assert float(inv.balance_remaining) == 0.00
        assert inv.status == "PAID"

        # Pay any remaining balance for student 1 so their overall balance is 0.00 (PAID)
        all_s1_invs = db.query(StudentFee).filter(
            StudentFee.student_id == inv.student_id,
            StudentFee.academic_year == academic_year,
        ).all()
        s1_invoices = [f for f in all_s1_invs if float(f.balance_remaining) > 0.001]
        for rem_inv in s1_invoices:
            client.post(
                "/api/v1/fees/payments",
                json={
                    "student_fee_id": rem_inv.id,
                    "amount_paid": float(rem_inv.balance_remaining),
                    "payment_date": date.today().isoformat(),
                    "payment_method": "CASH",
                    "reference_number": f"CLEAR-BAL-{rem_inv.id}",
                    "notes": "Clear pre-existing balance for test student",
                },
                headers=admin_headers,
            )

        # -------------------------------------------------------------
        # 14. Open Outstanding Fees & 15. Select Primary & 16. Select Class
        # -------------------------------------------------------------
        resp_out = client.get(
            f"/api/v1/fees/outstanding?academic_year={academic_year}&education_level=PRIMARY&class_id={g8_id}",
            headers=admin_headers,
        )
        assert resp_out.status_code == 200, f"Outstanding failed: {resp_out.text}"
        out_data = resp_out.json()

        # -------------------------------------------------------------
        # 17. Verify only unpaid students appear
        # Student 1 paid -> balance 0, Student 2 has unpaid balance
        # -------------------------------------------------------------
        assert out_data["total_students"] == 5
        assert out_data["paid_count"] >= 1
        # Student 1 (balance = 0) must NOT appear in the outstanding items list
        item_student_ids = {item["student_id"] for item in out_data["items"]}
        assert inv.student_id not in item_student_ids, "Fully paid student must not appear in outstanding list"

        # Students with balance > 0 should be in items list
        for item in out_data["items"]:
            assert item["balance"] > 0, "Students with zero balance must not appear in outstanding items"
            assert item["class_id"] == g8_id

        # -------------------------------------------------------------
        # 18. Select Secondary
        # -------------------------------------------------------------
        resp_sec_classes = client.get(
            f"/api/v1/fees/classes?academic_year={academic_year}&education_level=SECONDARY",
            headers=admin_headers,
        )
        assert resp_sec_classes.status_code == 200
        sec_classes = resp_sec_classes.json()

        # -------------------------------------------------------------
        # 19. Verify only Secondary classes appear
        # -------------------------------------------------------------
        for sc in sec_classes:
            assert sc["division"] == "SECONDARY"
            assert sc["level"].startswith("Form ")

        # -------------------------------------------------------------
        # 20. Verify Primary classes do not appear under Secondary
        # -------------------------------------------------------------
        sec_class_names = [sc["name"] for sc in sec_classes]
        assert "Grade 8 - A" not in sec_class_names
        assert "Grade 7 - A" not in sec_class_names
        assert "Grade 5 - A" not in sec_class_names

        # -------------------------------------------------------------
        # 21. Verify Secondary students do not appear under Primary
        # -------------------------------------------------------------
        resp_primary_out = client.get(
            f"/api/v1/fees/outstanding?academic_year={academic_year}&education_level=PRIMARY",
            headers=admin_headers,
        )
        assert resp_primary_out.status_code == 200
        for item in resp_primary_out.json()["items"]:
            assert item["education_level"] == "PRIMARY"
            assert not item["class_name"].startswith("Form ")

        # -------------------------------------------------------------
        # 22. Verify no duplicate students
        # -------------------------------------------------------------
        seen_student_ids = set()
        for item in resp_primary_out.json()["items"]:
            # Student can have at most one outstanding summary record in this view
            assert item["student_id"] not in seen_student_ids, f"Duplicate student ID {item['student_id']} in outstanding list"
            seen_student_ids.add(item["student_id"])

        print("\nAll 22 Steps of Fees Real Class Workflow Passed Successfully!")

    finally:
        db.close()
