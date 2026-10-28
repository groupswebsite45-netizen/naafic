"""
Automated Comprehensive Test Suite: Fees & Student Population Consistency & Reconciliation
Requirements: Sections 31 & 32
Author: Google Deepmind Antigravity Agent
"""

import pytest
import os
import sys
from datetime import date
from decimal import Decimal
from fastapi.testclient import TestClient

from app.main import create_application
from app.core.database import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.models.student import Student
from app.models.school_class import SchoolClass
from app.models.student_enrollment import StudentEnrollment
from app.models.fee import StudentFee, FeePayment, FeeStructure
from app.core.security import create_access_token


@pytest.fixture(scope="module")
def test_setup():
    app = create_application()
    client = TestClient(app)
    db = SessionLocal()

    # Find or create admin user for authentication
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        admin = db.query(User).filter(User.is_superuser == True).first()
    if not admin:
        admin_role = db.query(Role).filter(Role.name == "ADMIN").first()
        if not admin_role:
            admin_role = Role(name="ADMIN", description="Administrator")
            db.add(admin_role)
            db.commit()
        admin = User(
            username="admin_fee_verifier",
            email="admin_fee_verifier@hawlwadaagschool.edu.so",
            full_name="System Admin Verifier",
            hashed_password="fakehashadmin",
            is_active=True,
            is_superuser=True
        )
        admin.roles.append(admin_role)
        db.add(admin)
        db.commit()
        db.refresh(admin)

    token = create_access_token(
        subject=str(admin.id),
        claims={"username": admin.username, "roles": ["ADMIN"], "is_superuser": True}
    )
    headers = {"Authorization": f"Bearer {token}"}

    yield {
        "client": client,
        "db": db,
        "admin": admin,
        "headers": headers,
    }

    db.close()


# =========================================================================
# SECTION 31: 20 CORE CONSISTENCY TESTS
# =========================================================================

def test_01_and_02_get_active_enrolled_and_fee_eligible_students(test_setup):
    """Test 1 & 2: Authoritative active enrolled students in 2026/2027 and Fees eligible students."""
    db = test_setup["db"]
    client = test_setup["client"]
    headers = test_setup["headers"]

    # Direct PostgreSQL query: Active students with active enrollment in 2026/2027
    db_students = (
        db.query(Student)
        .join(StudentEnrollment, Student.id == StudentEnrollment.student_id)
        .filter(
            Student.status == "ACTIVE",
            StudentEnrollment.status == "ACTIVE",
            StudentEnrollment.academic_year == "2026/2027"
        )
        .all()
    )
    assert len(db_students) > 0, "PostgreSQL must contain active enrolled students"

    # API call to fees eligible students
    res = client.get("/api/v1/fees/students/eligible?academic_year=2026/2027", headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["total_eligible"] == len(db_students), (
        f"API total_eligible ({data['total_eligible']}) must match DB count ({len(db_students)})"
    )


def test_03_04_05_06_student_ids_comparison_no_missing_extra_duplicates(test_setup):
    """Test 3, 4, 5, 6: Compare student IDs - verify no missing, no extra, no duplicate students."""
    db = test_setup["db"]
    client = test_setup["client"]
    headers = test_setup["headers"]

    db_students = (
        db.query(Student.id)
        .join(StudentEnrollment, Student.id == StudentEnrollment.student_id)
        .filter(
            Student.status == "ACTIVE",
            StudentEnrollment.status == "ACTIVE",
            StudentEnrollment.academic_year == "2026/2027"
        )
        .all()
    )
    db_student_ids = sorted([s[0] for s in db_students])

    res = client.get("/api/v1/fees/students/eligible?academic_year=2026/2027", headers=headers)
    assert res.status_code == 200
    api_items = res.json()["items"]
    api_student_ids = [item["student_id"] for item in api_items]

    # Check duplicates
    assert len(api_student_ids) == len(set(api_student_ids)), "Fee-eligible students list must not contain duplicates"

    # Check missing and extra
    sorted_api_ids = sorted(api_student_ids)
    assert sorted_api_ids == db_student_ids, (
        f"Fees eligible student IDs must match PostgreSQL authoritative IDs exactly. "
        f"Missing: {set(db_student_ids) - set(sorted_api_ids)}, Extra: {set(sorted_api_ids) - set(db_student_ids)}"
    )


def test_07_class_filtering(test_setup):
    """Test 7: Class filtering must return ONLY students of that specific class."""
    db = test_setup["db"]
    client = test_setup["client"]
    headers = test_setup["headers"]

    grade_7a = db.query(SchoolClass).filter(SchoolClass.name.ilike("%Grade 7%A%")).first()
    assert grade_7a is not None

    db_7a_ids = [
        s[0] for s in (
            db.query(Student.id)
            .join(StudentEnrollment, Student.id == StudentEnrollment.student_id)
            .filter(
                Student.status == "ACTIVE",
                StudentEnrollment.status == "ACTIVE",
                StudentEnrollment.academic_year == "2026/2027",
                StudentEnrollment.class_id == grade_7a.id
            )
            .all()
        )
    ]

    res = client.get(f"/api/v1/fees/students/eligible?academic_year=2026/2027&class_id={grade_7a.id}", headers=headers)
    assert res.status_code == 200
    api_items = res.json()["items"]
    api_7a_ids = [item["student_id"] for item in api_items]

    assert sorted(api_7a_ids) == sorted(db_7a_ids), "Filtered class student list must match PostgreSQL enrollment exactly"


def test_08_primary_secondary_filtering(test_setup):
    """Test 8: Primary and Secondary filtering must never mix students."""
    db = test_setup["db"]
    client = test_setup["client"]
    headers = test_setup["headers"]

    # Primary
    res_pri = client.get("/api/v1/fees/students/eligible?academic_year=2026/2027&education_level=PRIMARY", headers=headers)
    assert res_pri.status_code == 200
    pri_items = res_pri.json()["items"]
    for st in pri_items:
        assert st["education_level"] == "PRIMARY", f"Student {st['student_name']} in primary filter is not PRIMARY"

    # Secondary
    res_sec = client.get("/api/v1/fees/students/eligible?academic_year=2026/2027&education_level=SECONDARY", headers=headers)
    assert res_sec.status_code == 200
    sec_items = res_sec.json()["items"]
    for st in sec_items:
        assert st["education_level"] == "SECONDARY", f"Student {st['student_name']} in secondary filter is not SECONDARY"

    # Disjoint check
    pri_ids = set(st["student_id"] for st in pri_items)
    sec_ids = set(st["student_id"] for st in sec_items)
    assert pri_ids.isdisjoint(sec_ids), "Primary and Secondary students must never overlap"


def test_09_academic_year_filtering(test_setup):
    """Test 9: Academic year filtering works properly."""
    client = test_setup["client"]
    headers = test_setup["headers"]

    res_2026 = client.get("/api/v1/fees/students/eligible?academic_year=2026/2027", headers=headers)
    assert res_2026.status_code == 200
    count_2026 = res_2026.json()["total_eligible"]

    res_old = client.get("/api/v1/fees/students/eligible?academic_year=2020/2021", headers=headers)
    assert res_old.status_code == 200
    count_old = res_old.json()["total_eligible"]

    assert count_old == 0, "Old unused academic year must return 0 students"
    assert count_2026 > 0, "Current academic year 2026/2027 must return enrolled students"


def test_10_11_12_13_14_fee_and_payment_calculations(test_setup):
    """Test 10-14: Fee calculations, payment calculations, outstanding, partial payment, full payment."""
    db = test_setup["db"]
    client = test_setup["client"]
    headers = test_setup["headers"]

    # Select an active student from Grade 7-A
    student = (
        db.query(Student)
        .join(StudentEnrollment, Student.id == StudentEnrollment.student_id)
        .filter(
            Student.status == "ACTIVE",
            StudentEnrollment.status == "ACTIVE",
            StudentEnrollment.academic_year == "2026/2027"
        )
        .first()
    )
    assert student is not None

    # Use existing active fee structure ID 150 or create one for test
    fee_struct = db.query(FeeStructure).filter(FeeStructure.id == 150).first()
    if not fee_struct:
        fee_struct = FeeStructure(
            name="Unit Test Fee",
            academic_year="2026/2027",
            education_level="PRIMARY",
            amount=Decimal("20.00"),
            frequency="Monthly",
            due_date=date.today(),
            status="ACTIVE",
            created_by_id=test_setup["admin"].id
        )
        db.add(fee_struct)
        db.commit()
        db.refresh(fee_struct)

    # Clean up any leftover invoices for this student from prior runs
    db.query(FeePayment).filter(FeePayment.student_id == student.id).delete()
    db.query(StudentFee).filter(StudentFee.student_id == student.id).delete()
    db.commit()

    # Assign fee to this student
    assign_res = client.post(
        "/api/v1/fees/invoices/assign",
        json={
            "fee_structure_id": fee_struct.id,
            "academic_year": "2026/2027",
            "target_type": "SINGLE_STUDENT",
            "student_id": student.id,
            "amount_due": 20.00
        },
        headers=headers
    )
    assert assign_res.status_code in (200, 201)
    inv_id = assign_res.json()["created_invoices"][0]["id"]

    # Verify initial invoice state (Test 10 & 12)
    inv = db.query(StudentFee).filter(StudentFee.id == inv_id).first()
    assert inv.net_amount == Decimal("20.00")
    assert inv.total_paid == Decimal("0.00")
    assert inv.balance_remaining == Decimal("20.00")
    assert inv.status in ("PENDING", "UNPAID")

    # Test 13: Partial Payment ($8.00)
    pay1_res = client.post(
        "/api/v1/fees/payments",
        json={
            "student_fee_id": inv_id,
            "amount_paid": 8.00,
            "payment_method": "EVC_PLUS",
            "payment_date": str(date.today()),
            "reference_number": "TX-PARTIAL-001"
        },
        headers=headers
    )
    assert pay1_res.status_code in (200, 201)

    db.refresh(inv)
    assert inv.total_paid == Decimal("8.00")
    assert inv.balance_remaining == Decimal("12.00")
    assert inv.status == "PARTIALLY_PAID"

    # Test 14: Full Payment (remaining $12.00)
    pay2_res = client.post(
        "/api/v1/fees/payments",
        json={
            "student_fee_id": inv_id,
            "amount_paid": 12.00,
            "payment_method": "CASH",
            "payment_date": str(date.today()),
            "reference_number": "TX-FULL-002"
        },
        headers=headers
    )
    assert pay2_res.status_code in (200, 201)

    db.refresh(inv)
    assert inv.total_paid == Decimal("20.00")
    assert inv.balance_remaining == Decimal("0.00")
    assert inv.status == "PAID"

    # Clean up test invoice & payments so database remains in pristine state
    db.query(FeePayment).filter(FeePayment.student_fee_id == inv_id).delete()
    db.query(StudentFee).filter(StudentFee.id == inv_id).delete()
    db.commit()


def test_15_new_student_registration_appears_in_fees(test_setup):
    """Test 15: New student registration in Students immediately appears in Fees eligibility."""
    db = test_setup["db"]
    client = test_setup["client"]
    headers = test_setup["headers"]

    grade_7a = db.query(SchoolClass).filter(SchoolClass.name.ilike("%Grade 7%A%")).first()
    assert grade_7a is not None

    # Register temporary student
    temp_student = Student(
        admission_number="ADM-TEST-REG-999",
        first_name="TestAuto",
        last_name="Enrolled",
        gender="MALE",
        date_of_birth=date(2012, 1, 1),
        status="ACTIVE"
    )
    db.add(temp_student)
    db.commit()
    db.refresh(temp_student)

    # Active enrollment
    enr = StudentEnrollment(
        student_id=temp_student.id,
        class_id=grade_7a.id,
        academic_year="2026/2027",
        start_date=date.today(),
        status="ACTIVE"
    )
    db.add(enr)
    db.commit()

    # Query Fees eligibility API
    res = client.get(f"/api/v1/fees/students/eligible?academic_year=2026/2027&class_id={grade_7a.id}", headers=headers)
    assert res.status_code == 200
    ids = [item["student_id"] for item in res.json()["items"]]
    assert temp_student.id in ids, "Newly registered student must automatically appear in Fees eligible list"

    # Clean up temporary student
    db.query(StudentEnrollment).filter(StudentEnrollment.student_id == temp_student.id).delete()
    db.query(Student).filter(Student.id == temp_student.id).delete()
    db.commit()


def test_16_class_change_updates_fees(test_setup):
    """Test 16: When student changes class, fee counts and eligibility update automatically."""
    db = test_setup["db"]
    client = test_setup["client"]
    headers = test_setup["headers"]

    grade_7a = db.query(SchoolClass).filter(SchoolClass.name.ilike("%Grade 7%A%")).first()
    grade_8a = db.query(SchoolClass).filter(SchoolClass.name.ilike("%Grade 8%A%")).first()
    assert grade_7a and grade_8a

    # Register temporary student in 7-A
    st = Student(
        admission_number="ADM-TRANSFER-01",
        first_name="Transfer",
        last_name="Student",
        gender="FEMALE",
        date_of_birth=date(2011, 5, 5),
        status="ACTIVE"
    )
    db.add(st)
    db.commit()
    db.refresh(st)

    enr = StudentEnrollment(
        student_id=st.id,
        class_id=grade_7a.id,
        academic_year="2026/2027",
        start_date=date.today(),
        status="ACTIVE"
    )
    db.add(enr)
    db.commit()

    # Verify in 7-A
    res1 = client.get(f"/api/v1/fees/students/eligible?academic_year=2026/2027&class_id={grade_7a.id}", headers=headers)
    assert st.id in [i["student_id"] for i in res1.json()["items"]]

    # Move student to 8-A: update active enrollment
    enr.class_id = grade_8a.id
    db.commit()

    # Verify student is now in 8-A and NOT in 7-A
    res_7a_after = client.get(f"/api/v1/fees/students/eligible?academic_year=2026/2027&class_id={grade_7a.id}", headers=headers)
    res_8a_after = client.get(f"/api/v1/fees/students/eligible?academic_year=2026/2027&class_id={grade_8a.id}", headers=headers)

    assert st.id not in [i["student_id"] for i in res_7a_after.json()["items"]]
    assert st.id in [i["student_id"] for i in res_8a_after.json()["items"]]

    # Clean up
    db.query(StudentEnrollment).filter(StudentEnrollment.student_id == st.id).delete()
    db.query(Student).filter(Student.id == st.id).delete()
    db.commit()


def test_17_student_financial_profile_loads(test_setup):
    """Test 17: Verify Student Financial Profile loads without errors."""
    db = test_setup["db"]
    client = test_setup["client"]
    headers = test_setup["headers"]

    first_student = db.query(Student).filter(Student.status == "ACTIVE").first()
    assert first_student is not None

    res = client.get(f"/api/v1/fees/students/{first_student.id}/financial-profile", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["student_id"] == first_student.id
    assert "total_billed" in data
    assert "total_paid" in data
    assert "outstanding_balance" in data


def test_18_19_no_orphan_invoices_or_payments(test_setup):
    """Test 18 & 19: Verify zero orphan invoices (nonexistent student/class) and zero orphan payments."""
    db = test_setup["db"]

    # Invoices with nonexistent student
    orphan_invoices = (
        db.query(StudentFee)
        .outerjoin(Student, StudentFee.student_id == Student.id)
        .filter(Student.id.is_(None))
        .count()
    )
    assert orphan_invoices == 0, f"Found {orphan_invoices} orphan invoices with no valid student"

    # Payments with nonexistent student fee invoice
    orphan_payments = (
        db.query(FeePayment)
        .outerjoin(StudentFee, FeePayment.student_fee_id == StudentFee.id)
        .filter(StudentFee.id.is_(None))
        .count()
    )
    assert orphan_payments == 0, f"Found {orphan_payments} orphan payments with no valid invoice"


def test_20_fee_structure_list_contains_only_legitimate_structures(test_setup):
    """Test 20: Verify fee structures list contains only legitimate structures."""
    db = test_setup["db"]
    client = test_setup["client"]
    headers = test_setup["headers"]

    res = client.get("/api/v1/fees/structures", headers=headers)
    assert res.status_code == 200
    structures = res.json()

    for s in structures:
        # Legitimate structure must have valid name, academic year, and amount > 0
        assert float(s["amount"]) > 0
        assert s["academic_year"] in ("2026/2027", "2025/2026", "2024/2025")
        assert s["status"] in ("ACTIVE", "INACTIVE")


# =========================================================================
# SECTION 32: EXACT RECONCILIATION TEST SCENARIO
# =========================================================================

def test_exact_reconciliation_scenario_32(test_setup):
    """
    Exact Section 32 Test Scenario:
    PRIMARY Grade 8-A: 10 students
    Fee: $15/student
    Expected: Students = 10, Fee = $15, Expected = $150
    Record payments for 3 students x $15:
      Paid Students = 3, Unpaid Students = 7, Paid = $45, Outstanding = $105
      Verify $45 + $105 = $150
    Register 11th student:
      Students = 11, Expected = $165, Paid = $45, Outstanding = $120
    Pay 11th student's $15:
      Students = 11, Paid Students = 4, Unpaid Students = 7, Paid = $60, Outstanding = $105.
    """
    db = test_setup["db"]
    client = test_setup["client"]
    headers = test_setup["headers"]

    grade_8a = db.query(SchoolClass).filter(SchoolClass.name.ilike("%Grade 8%A%")).first()
    assert grade_8a is not None, "Grade 8-A must exist in database"

    # Check current real active students in Grade 8-A
    existing_enrs = (
        db.query(StudentEnrollment)
        .join(Student, StudentEnrollment.student_id == Student.id)
        .filter(
            StudentEnrollment.class_id == grade_8a.id,
            StudentEnrollment.status == "ACTIVE",
            StudentEnrollment.academic_year == "2026/2027",
            Student.status == "ACTIVE"
        )
        .all()
    )
    existing_count = len(existing_enrs)

    # To reach exactly 10 students for this test scenario, create needed temporary students
    needed = 10 - existing_count
    temp_students = []
    temp_enrs = []

    for i in range(needed):
        s = Student(
            admission_number=f"ADM-RECON-SCENARIO-{i+1:03d}",
            first_name=f"ScenarioStudent{i+1}",
            last_name="Grade8A",
            gender="MALE",
            date_of_birth=date(2011, 1, 1),
            status="ACTIVE"
        )
        db.add(s)
        db.commit()
        db.refresh(s)
        temp_students.append(s)

        e = StudentEnrollment(
            student_id=s.id,
            class_id=grade_8a.id,
            academic_year="2026/2027",
            start_date=date.today(),
            status="ACTIVE"
        )
        db.add(e)
        db.commit()
        temp_enrs.append(e)

    created_invoices = []
    inv_11_id = None
    fee_structure_id = None

    try:
        # 1. Verify exactly 10 active students in Grade 8-A
        res_eligible = client.get(f"/api/v1/fees/students/eligible?academic_year=2026/2027&class_id={grade_8a.id}", headers=headers)
        assert res_eligible.status_code == 200
        eligible_items = res_eligible.json()["items"]
        assert len(eligible_items) == 10, f"Expected 10 students, got {len(eligible_items)}"

        # 2. Create class fee structure: $15/student
        struct_res = client.post(
            "/api/v1/fees/structures",
            json={
                "name": "Grade 8 Monthly Tuition Fee",
                "academic_year": "2026/2027",
                "education_level": "PRIMARY",
                "class_id": grade_8a.id,
                "amount": 15.00,
                "frequency": "Monthly",
                "due_date": str(date.today()),
                "status": "ACTIVE"
            },
            headers=headers
        )
        assert struct_res.status_code in (200, 201)
        fee_structure_id = struct_res.json()["id"]

        # 3. Assign fee to Grade 8-A
        assign_res = client.post(
            "/api/v1/fees/invoices/assign",
            json={
                "fee_structure_id": fee_structure_id,
                "academic_year": "2026/2027",
                "target_type": "CLASS",
                "class_id": grade_8a.id,
                "amount_due": 15.00
            },
            headers=headers
        )
        assert assign_res.status_code in (200, 201)
        created_invoices = [inv["id"] for inv in assign_res.json()["created_invoices"]]
        assert len(created_invoices) == 10

        # Check initial summary: Expected = 10 * 15 = $150
        sum_res1 = client.get(f"/api/v1/fees/summary?academic_year=2026/2027&class_id={grade_8a.id}", headers=headers)
        assert sum_res1.status_code == 200
        s1 = sum_res1.json()
        assert s1["total_students"] == 10
        assert s1["fee_per_student"] == 15.00
        assert s1["expected_total"] == 150.00
        assert s1["total_paid"] == 0.00
        assert s1["total_outstanding"] == 150.00
        assert s1["paid_students_count"] == 0
        assert s1["unpaid_students_count"] == 10
        assert s1["is_reconciled"] is True

        # 4. Record payments for 3 students x $15
        for i in range(3):
            inv_id = created_invoices[i]
            pay_res = client.post(
                "/api/v1/fees/payments",
                json={
                    "student_fee_id": inv_id,
                    "amount_paid": 15.00,
                    "payment_method": "EVC_PLUS",
                    "payment_date": str(date.today()),
                    "reference_number": f"TX-SCENARIO-32-{i+1}"
                },
                headers=headers
            )
            assert pay_res.status_code in (200, 201)

        # Verify: Paid Students = 3, Unpaid Students = 7, Paid = $45, Outstanding = $105
        # Verify: $45 + $105 = $150
        sum_res2 = client.get(f"/api/v1/fees/summary?academic_year=2026/2027&class_id={grade_8a.id}", headers=headers)
        assert sum_res2.status_code == 200
        s2 = sum_res2.json()

        assert s2["total_students"] == 10
        assert s2["paid_students_count"] == 3
        assert s2["unpaid_students_count"] == 7
        assert s2["total_paid"] == 45.00
        assert s2["total_outstanding"] == 105.00
        assert s2["expected_total"] == 150.00
        assert Decimal(str(s2["total_paid"])) + Decimal(str(s2["total_outstanding"])) == Decimal(str(s2["expected_total"]))
        assert s2["is_reconciled"] is True

        # 5. Register another Grade 8-A student (11th student)
        st_11 = Student(
            admission_number="ADM-RECON-SCENARIO-011",
            first_name="Eleventh",
            last_name="Student",
            gender="FEMALE",
            date_of_birth=date(2011, 2, 2),
            status="ACTIVE"
        )
        db.add(st_11)
        db.commit()
        db.refresh(st_11)
        temp_students.append(st_11)

        enr_11 = StudentEnrollment(
            student_id=st_11.id,
            class_id=grade_8a.id,
            academic_year="2026/2027",
            start_date=date.today(),
            status="ACTIVE"
        )
        db.add(enr_11)
        db.commit()
        temp_enrs.append(enr_11)

        # Expected: Students = 11, Expected = $165, Paid = $45, Outstanding = $120
        sum_res3 = client.get(f"/api/v1/fees/summary?academic_year=2026/2027&class_id={grade_8a.id}", headers=headers)
        assert sum_res3.status_code == 200
        s3 = sum_res3.json()

        assert s3["total_students"] == 11
        assert s3["expected_total"] == 165.00
        assert s3["total_paid"] == 45.00
        assert s3["total_outstanding"] == 120.00
        assert s3["paid_students_count"] == 3
        assert s3["unpaid_students_count"] == 8
        assert s3["is_reconciled"] is True

        # Assign fee to 11th student
        assign_11 = client.post(
            "/api/v1/fees/invoices/assign",
            json={
                "fee_structure_id": fee_structure_id,
                "academic_year": "2026/2027",
                "target_type": "SINGLE_STUDENT",
                "student_id": st_11.id,
                "amount_due": 15.00
            },
            headers=headers
        )
        assert assign_11.status_code in (200, 201)
        inv_11_id = assign_11.json()["created_invoices"][0]["id"]

        # 6. Pay the new student's $15
        pay_11_res = client.post(
            "/api/v1/fees/payments",
            json={
                "student_fee_id": inv_11_id,
                "amount_paid": 15.00,
                "payment_method": "EVC_PLUS",
                "payment_date": str(date.today()),
                "reference_number": "TX-SCENARIO-32-11"
            },
            headers=headers
        )
        assert pay_11_res.status_code in (200, 201)

        # Expected:
        # Students = 11, Paid Students = 4, Unpaid Students = 7, Paid = $60, Outstanding = $105
        sum_res4 = client.get(f"/api/v1/fees/summary?academic_year=2026/2027&class_id={grade_8a.id}", headers=headers)
        assert sum_res4.status_code == 200
        s4 = sum_res4.json()

        assert s4["total_students"] == 11
        assert s4["paid_students_count"] == 4
        assert s4["unpaid_students_count"] == 7
        assert s4["total_paid"] == 60.00
        assert s4["total_outstanding"] == 105.00
        assert s4["expected_total"] == 165.00
        assert Decimal(str(s4["total_paid"])) + Decimal(str(s4["total_outstanding"])) == Decimal(str(s4["expected_total"]))
        assert s4["is_reconciled"] is True

        print("Exact Section 32 reconciliation scenario PASSED with 100% mathematical precision!")

    finally:
        # CLEANUP: Remove scenario payments, invoices, fee structure, and temporary students
        all_scenario_inv_ids = created_invoices + ([inv_11_id] if 'inv_11_id' in locals() else [])
        if all_scenario_inv_ids:
            db.query(FeePayment).filter(FeePayment.student_fee_id.in_(all_scenario_inv_ids)).delete(synchronize_session=False)
            db.query(StudentFee).filter(StudentFee.id.in_(all_scenario_inv_ids)).delete(synchronize_session=False)
        if 'fee_structure_id' in locals():
            db.query(FeeStructure).filter(FeeStructure.id == fee_structure_id).delete(synchronize_session=False)

        for e in temp_enrs:
            db.query(StudentEnrollment).filter(StudentEnrollment.id == e.id).delete(synchronize_session=False)
        for s in temp_students:
            db.query(Student).filter(Student.id == s.id).delete(synchronize_session=False)
        db.commit()


if __name__ == "__main__":
    pytest.main(["-v", "-s", __file__])
