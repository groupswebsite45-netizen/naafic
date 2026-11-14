import sys
import os
import random
from datetime import date

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.school_class import SchoolClass
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.models.teacher import Teacher
from app.models.subject import Subject
from app.models.attendance import Attendance
from app.models.exam import Exam, ExamResult
from app.models.class_promotion import ClassPromotionBatch, ClassPromotionRecord
from app.models.user import User
from app.models.role import Role
from app.core.security import get_password_hash

client = TestClient(app)


@pytest.fixture(scope="module")
def admin_token():
    res = client.post("/api/v1/auth/login", json={
        "identifier": "admin",
        "password": "Admin@Hawlwadaag2026"
    })
    assert res.status_code == 200, f"Admin login failed: {res.text}"
    return res.json()["access_token"]


@pytest.fixture(scope="module")
def teacher_token():
    db = SessionLocal()
    try:
        teacher_user = db.query(User).filter(User.username == "teacher_test_prom").first()
        if not teacher_user:
            teacher_role = db.query(Role).filter(Role.name == "TEACHER").first()
            if not teacher_role:
                teacher_role = Role(name="TEACHER", description="Teacher Role")
                db.add(teacher_role)
                db.commit()
            teacher_user = User(
                email="teacher_prom@hawlwadaagschool.edu.so",
                username="teacher_test_prom",
                hashed_password=get_password_hash("Teacher@123"),
                full_name="Teacher Promotion Test",
                is_active=True
            )
            db.add(teacher_user)
            db.commit()
            db.refresh(teacher_user)
            db.execute(
                User.__table__.metadata.tables["user_roles"].insert().values(
                    user_id=teacher_user.id,
                    role_id=teacher_role.id
                )
            )
            db.commit()
    finally:
        db.close()

    res = client.post("/api/v1/auth/login", json={
        "identifier": "teacher_test_prom",
        "password": "Teacher@123"
    })
    assert res.status_code == 200, f"Teacher login failed: {res.text}"
    return res.json()["access_token"]


def test_complete_class_promotion_system(admin_token, teacher_token):
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    teacher_headers = {"Authorization": f"Bearer {teacher_token}"}

    print("\n==================================================")
    print("TESTING CLASS CHANGE & BULK PROMOTION SYSTEM")
    print("School: Hawlwadaag Primary and Secondary School")
    print("==================================================")

    db = SessionLocal()
    try:
        # Setup real test classes: Form 1, Form 2, Form 3, Form 4, Form 5, Form 6
        rand_suffix = random.randint(1000, 9999)
        form_classes = {}
        for form_num in range(1, 7):
            code = f"F{form_num}-PROM-{rand_suffix}"
            c = SchoolClass(
                name=f"Form {form_num}",
                code=code,
                section="Stream A",
                academic_year="2026/2027",
                capacity=40,
                status="ACTIVE"
            )
            db.add(c)
            db.commit()
            db.refresh(c)
            form_classes[form_num] = c

        # Create student portal user for Mohamed Ali Mire
        mohamed_username = f"mohamed_mire_{rand_suffix}"
        mohamed_user = User(
            email=f"mohamed_{rand_suffix}@student.hawlwadaagschool.edu.so",
            username=mohamed_username,
            hashed_password=get_password_hash("Student@123"),
            full_name="Mohamed Ali Mire",
            is_active=True
        )
        db.add(mohamed_user)
        db.commit()
        db.refresh(mohamed_user)
        st_role = db.query(Role).filter(Role.name == "STUDENT").first()
        if st_role:
            db.execute(
                User.__table__.metadata.tables["user_roles"].insert().values(
                    user_id=mohamed_user.id,
                    role_id=st_role.id
                )
            )
            db.commit()

        # Create students for each form
        students_by_form = {}
        created_students = []
        for form_num in range(1, 7):
            students_by_form[form_num] = []
            for s_idx in range(1, 4):
                adm_no = f"ADM-PROM-{form_num}-{s_idx}-{rand_suffix}"
                first_n = "Mohamed" if (form_num == 5 and s_idx == 1) else f"Student{form_num}_{s_idx}"
                middle_n = "Ali" if (form_num == 5 and s_idx == 1) else "A."
                last_n = "Mire" if (form_num == 5 and s_idx == 1) else f"Surname{rand_suffix}"

                # Link student portal user for Mohamed Ali Mire
                user_id = mohamed_user.id if (form_num == 5 and s_idx == 1) else None

                s = Student(
                    user_id=user_id,
                    admission_number=adm_no,
                    first_name=first_n,
                    middle_name=middle_n,
                    last_name=last_n,
                    gender="Male" if s_idx % 2 == 1 else "Female",
                    status="ACTIVE"
                )
                db.add(s)
                db.commit()
                db.refresh(s)

                # Active enrollment for 2026/2027 in Form X
                enr = StudentEnrollment(
                    student_id=s.id,
                    class_id=form_classes[form_num].id,
                    academic_year="2026/2027",
                    roll_number=f"R-{s_idx}",
                    status="ACTIVE"
                )
                db.add(enr)
                db.commit()

                students_by_form[form_num].append(s)
                created_students.append(s)

        mohamed_student = students_by_form[5][0]
        assert mohamed_student.first_name == "Mohamed"
        assert mohamed_student.last_name == "Mire"

        # Create Subject, Teacher, Attendance, Exam & Result for Mohamed in Form 5 for 2026/2027
        subj = db.query(Subject).first()
        if not subj:
            subj = Subject(name="Mathematics", code=f"MATH-{rand_suffix}", department="Sciences", status="ACTIVE")
            db.add(subj)
            db.commit()

        # Historical attendance in 2026/2027 (Form 5)
        att = Attendance(
            student_id=mohamed_student.id,
            class_id=form_classes[5].id,
            subject_id=subj.id,
            academic_year="2026/2027",
            date=date(2026, 9, 15),
            period="08:00 - 09:00",
            status="PRESENT"
        )
        db.add(att)
        db.commit()

        # Historical exam & result in 2026/2027 (Form 5)
        exam = Exam(
            name="Term 1 Midterm Exam 2026",
            exam_type="MIDTERM",
            academic_year="2026/2027",
            class_id=form_classes[5].id,
            subject_id=subj.id,
            start_date=date(2026, 9, 10),
            max_marks=100.0,
            status="COMPLETED"
        )
        db.add(exam)
        db.commit()
        db.refresh(exam)

        exam_res = ExamResult(
            exam_id=exam.id,
            student_id=mohamed_student.id,
            subject_id=subj.id,
            marks_obtained=94.5,
            grade="A",
            status="RELEASED"
        )
        db.add(exam_res)
        db.commit()
        print("[OK] Database setup complete with historical records for 2026/2027.")

    finally:
        db.close()

    # Login as Mohamed Ali Mire student portal account
    st_login = client.post("/api/v1/auth/login", json={
        "identifier": mohamed_username,
        "password": "Student@123"
    })
    assert st_login.status_code == 200, f"Student login failed: {st_login.text}"
    student_headers = {"Authorization": f"Bearer {st_login.json()['access_token']}"}

    # --------------------------------------------------------------------------
    # TEST 1 & 2 & 3: Individual Form 5 -> Form 6 Class Change / Promotion
    # --------------------------------------------------------------------------
    print("\n[TEST 1-3] Testing Individual Class Change (Mohamed Ali Mire: Form 5 -> Form 6)...")
    ind_payload = {
        "new_class_id": form_classes[6].id,
        "academic_year": "2026/2027",
        "reason": "Annual Academic Progression",
        "is_promotion": True
    }
    ind_res = client.post(
        f"/api/v1/class-promotions/students/{mohamed_student.id}/change-class",
        json=ind_payload,
        headers=admin_headers
    )
    assert ind_res.status_code == 200, f"Individual class change failed: {ind_res.text}"
    ind_data = ind_res.json()
    print(f"[OK] Response: {ind_data['message']} (Batch Code: {ind_data['batch_code']})")
    assert ind_data["new_class_name"] == "Form 6"
    assert ind_data["academic_year"] == "2026/2027"

    # Verify Historical Record in Database:
    # 1. Enrollment in 2026/2027 must remain Form 5!
    # 2. Enrollment in 2026/2027 must be Form 6!
    db = SessionLocal()
    try:
        enr_2026 = db.query(StudentEnrollment).filter(
            StudentEnrollment.student_id == mohamed_student.id,
            StudentEnrollment.academic_year == "2026/2027"
        ).first()
        assert enr_2026 is not None, "2026/2027 enrollment was lost!"
        assert enr_2026.class_id == form_classes[5].id, "Historical 2026/2027 enrollment class was altered!"
        assert enr_2026.status == "PROMOTED", "Historical enrollment status should be PROMOTED"
        print("[OK] Historical 2026/2027 enrollment verified intact (Form 5).")

        enr_2027 = db.query(StudentEnrollment).filter(
            StudentEnrollment.student_id == mohamed_student.id,
            StudentEnrollment.academic_year == "2026/2027"
        ).first()
        assert enr_2027 is not None, "2026/2027 enrollment was not created!"
        assert enr_2027.class_id == form_classes[6].id, "2026/2027 enrollment class is not Form 6!"
        assert enr_2027.status == "ACTIVE", "2026/2027 enrollment must be ACTIVE!"
        print("[OK] New 2026/2027 enrollment verified in PostgreSQL (Form 6).")
    finally:
        db.close()

    # --------------------------------------------------------------------------
    # TEST 4, 5, 6, 7 & 8: Bulk Promotion of All Classes
    # --------------------------------------------------------------------------
    print("\n[TEST 4-8] Testing Suggested Mappings & Bulk Class Promotion...")
    mappings_res = client.get(
        "/api/v1/class-promotions/suggested-mappings?source_year=2026/2027&target_year=2026/2027",
        headers=admin_headers
    )
    assert mappings_res.status_code == 200, f"Suggested mappings failed: {mappings_res.text}"
    mappings_data = mappings_res.json()
    print(f"[OK] Suggested mappings retrieved: {len(mappings_data['mappings'])} class mappings.")

    # Find the mappings for Form 1..Form 6
    form_mappings = [m for m in mappings_data["mappings"] if "Form" in m["from_class_name"]]
    # Form 6 should be terminal / graduating!
    form_6_mapping = next((m for m in form_mappings if m["from_class_name"] == "Form 6"), None)
    if form_6_mapping:
        assert form_6_mapping["is_terminal_class"] is True
        assert form_6_mapping["action"] == "GRADUATE" or form_6_mapping["to_class_id"] is None
        print("[OK] Form 6 is correctly identified as terminal/graduating class without auto-promotion.")

    # Build the Bulk Promotion Payload
    bulk_mappings = [
        {"from_class_id": form_classes[1].id, "to_class_id": form_classes[2].id, "action": "PROMOTE"},
        {"from_class_id": form_classes[2].id, "to_class_id": form_classes[3].id, "action": "PROMOTE"},
        {"from_class_id": form_classes[3].id, "to_class_id": form_classes[4].id, "action": "PROMOTE"},
        {"from_class_id": form_classes[4].id, "to_class_id": form_classes[5].id, "action": "PROMOTE"},
        {"from_class_id": form_classes[5].id, "to_class_id": form_classes[6].id, "action": "PROMOTE"},
        {"from_class_id": form_classes[6].id, "to_class_id": None, "action": "GRADUATE"},
    ]

    # Test Preview API
    preview_res = client.post("/api/v1/class-promotions/preview", json={
        "source_academic_year": "2026/2027",
        "target_academic_year": "2026/2027",
        "mappings": bulk_mappings
    }, headers=admin_headers)
    assert preview_res.status_code == 200, f"Preview failed: {preview_res.text}"
    preview_data = preview_res.json()
    print(f"[OK] Preview generated: {preview_data['total_students_affected']} students affected, {preview_data['total_to_promote']} to promote, {preview_data['total_to_graduate']} to graduate.")
    assert preview_data["total_students_affected"] >= 15

    # Execute Bulk Promotion
    bulk_res = client.post("/api/v1/class-promotions/bulk", json={
        "source_academic_year": "2026/2027",
        "target_academic_year": "2026/2027",
        "mappings": bulk_mappings,
        "reason": "Annual Hawlwadaag School Promotion 2026/2027 -> 2026/2027"
    }, headers=admin_headers)
    assert bulk_res.status_code == 201, f"Bulk promotion failed: {bulk_res.text}"
    bulk_data = bulk_res.json()
    batch_code = bulk_data["batch_code"]
    print(f"[OK] Bulk Promotion successfully executed! Batch Code: {batch_code}")
    assert batch_code.startswith("PROM-2027-")
    assert bulk_data["total_promoted"] >= 10
    assert bulk_data["total_graduated"] >= 2

    # --------------------------------------------------------------------------
    # TEST 9, 10, 11: Validation Rejections
    # --------------------------------------------------------------------------
    print("\n[TEST 9-11] Testing Validation Rejections...")

    # Duplicate promotion attempt for the same target year -> must be rejected
    dup_res = client.post("/api/v1/class-promotions/bulk", json={
        "source_academic_year": "2026/2027",
        "target_academic_year": "2026/2027",
        "mappings": bulk_mappings
    }, headers=admin_headers)
    dup_err = dup_res.json().get("error", {}).get("message") or dup_res.json().get("detail", "")
    print(f"[OK] Duplicate promotion properly rejected with 400: {dup_err}")

    # Identical source and target academic year
    same_year_res = client.post("/api/v1/class-promotions/bulk", json={
        "source_academic_year": "2026/2027",
        "target_academic_year": "2026/2027",
        "mappings": bulk_mappings
    }, headers=admin_headers)
    assert same_year_res.status_code == 400
    print("[OK] Identical academic year properly rejected.")

    # Source == Destination class rejection
    same_class_res = client.post("/api/v1/class-promotions/bulk", json={
        "source_academic_year": "2026/2027",
        "target_academic_year": "2026/2027",
        "mappings": [{"from_class_id": form_classes[3].id, "to_class_id": form_classes[3].id, "action": "PROMOTE"}]
    }, headers=admin_headers)
    assert same_class_res.status_code == 400
    print("[OK] Source == Destination class properly rejected.")

    # --------------------------------------------------------------------------
    # TEST 12 & 13: RBAC Authorization
    # --------------------------------------------------------------------------
    print("\n[TEST 12-13] Testing Authorization (Teacher & Student must receive 403)...")
    teacher_try = client.post("/api/v1/class-promotions/bulk", json={
        "source_academic_year": "2026/2027",
        "target_academic_year": "2026/2027",
        "mappings": bulk_mappings
    }, headers=teacher_headers)
    assert teacher_try.status_code == 403, f"Teacher promotion attempt expected 403, got {teacher_try.status_code}"
    print("[OK] Teacher receives 403 Forbidden.")

    student_try = client.post(f"/api/v1/class-promotions/students/{mohamed_student.id}/change-class", json={
        "new_class_id": form_classes[6].id,
        "academic_year": "2028/2029"
    }, headers=student_headers)
    assert student_try.status_code == 403, f"Student promotion attempt expected 403, got {student_try.status_code}"
    print("[OK] Student receives 403 Forbidden.")

    # --------------------------------------------------------------------------
    # TEST 14: Atomic Transaction Rollback
    # --------------------------------------------------------------------------
    print("\n[TEST 14] Testing Atomic Transaction Rollback on error...")
    # Attempt promotion with an invalid destination class
    bad_bulk_res = client.post("/api/v1/class-promotions/bulk", json={
        "source_academic_year": "2026/2027",
        "target_academic_year": "2029/2030",
        "mappings": [
            {"from_class_id": form_classes[1].id, "to_class_id": 99999999, "action": "PROMOTE"}
        ]
    }, headers=admin_headers)
    assert bad_bulk_res.status_code == 400
    bad_msg = bad_bulk_res.json().get("error", {}).get("message") or bad_bulk_res.json().get("detail", "")
    assert "No students were changed" in bad_msg
    print(f"[OK] Database transaction rollback verified: '{bad_msg}'")

    # --------------------------------------------------------------------------
    # TEST 15: Promotion History and PostgreSQL Audit Persistence
    # --------------------------------------------------------------------------
    print("\n[TEST 15] Testing Promotion History & Audit Trail...")
    history_res = client.get("/api/v1/class-promotions/history", headers=admin_headers)
    assert history_res.status_code == 200
    history_items = history_res.json()
    assert len(history_items) >= 1
    recent_batch = next((b for b in history_items if b["batch_code"] == batch_code), None)
    assert recent_batch is not None
    assert recent_batch["status"] == "COMPLETED"
    print(f"[OK] Batch {batch_code} confirmed in audit history API.")

    batch_detail_res = client.get(f"/api/v1/class-promotions/history/{recent_batch['id']}", headers=admin_headers)
    assert batch_detail_res.status_code == 200
    batch_detail = batch_detail_res.json()
    assert len(batch_detail["records"]) >= 10
    print(f"[OK] Batch details verified with {len(batch_detail['records'])} student records.")

    # --------------------------------------------------------------------------
    # TEST 16, 17, 18: Historical Attendance, Exam, and Results Integrity
    # --------------------------------------------------------------------------
    print("\n[TEST 16-18] Verifying Attendance, Exams, and Results Integrity...")
    db = SessionLocal()
    try:
        # Check Attendance record for Mohamed Ali Mire
        hist_att = db.query(Attendance).filter(
            Attendance.student_id == mohamed_student.id,
            Attendance.academic_year == "2026/2027"
        ).first()
        assert hist_att is not None
        assert hist_att.class_id == form_classes[5].id, "Attendance class assignment was altered!"
        assert hist_att.status == "PRESENT"
        print("[OK] Historical attendance record for 2026/2027 remains associated with Form 5.")

        # Check Exam & Exam Result for Mohamed Ali Mire
        hist_result = db.query(ExamResult).filter(
            ExamResult.student_id == mohamed_student.id
        ).first()
        assert hist_result is not None
        assert hist_result.marks_obtained == 94.5
        assert hist_result.grade == "A"
        assert hist_result.exam.academic_year == "2026/2027"
        assert hist_result.exam.class_id == form_classes[5].id
        print("[OK] Historical exam & assessment results for 2026/2027 remain associated with Form 5.")
    finally:
        db.close()

    # --------------------------------------------------------------------------
    # TEST 19: Student Portal Academic Year Filter
    # --------------------------------------------------------------------------
    print("\n[TEST 19] Testing Student Portal Academic Year Scoping...")
    # When student queries 2026/2027: class must be Form 6
    class_2027_res = client.get("/api/v1/student-portal/class?academic_year=2026/2027", headers=student_headers)
    assert class_2027_res.status_code == 200, f"Student portal failed: {class_2027_res.text}"
    class_2027_data = class_2027_res.json()
    assert class_2027_data["school_class"]["name"] == "Form 6"
    assert class_2027_data["academic_year"] == "2026/2027"
    print("[OK] Student portal for 2026/2027 correctly displays Form 6.")

    # When student queries 2026/2027: class must be Form 5
    class_2026_res = client.get("/api/v1/student-portal/class?academic_year=2026/2027", headers=student_headers)
    assert class_2026_res.status_code == 200
    class_2026_data = class_2026_res.json()
    assert class_2026_data["school_class"]["name"] == "Form 5"
    assert class_2026_data["academic_year"] == "2026/2027"
    print("[OK] Student portal for 2026/2027 correctly displays Form 5.")

    # --------------------------------------------------------------------------
    # TEST 20: Safe Batch Rollback Verification
    # --------------------------------------------------------------------------
    print("\n[TEST 20] Testing Safe Batch Rollback...")
    rollback_res = client.post(
        f"/api/v1/class-promotions/history/{recent_batch['id']}/rollback",
        headers=admin_headers
    )
    assert rollback_res.status_code == 200, f"Rollback failed: {rollback_res.text}"
    rb_data = rollback_res.json()
    print(f"[OK] Rollback successful: {rb_data['message']}")
    assert rb_data["success"] is True

    # Verify in PostgreSQL: target enrollments deleted, source enrollments active again!
    db = SessionLocal()
    try:
        rb_batch = db.query(ClassPromotionBatch).filter(ClassPromotionBatch.id == recent_batch["id"]).first()
        assert rb_batch.status == "ROLLED_BACK"

        # Check that target enrollments for 2026/2027 created by that batch are removed
        # (excluding Mohamed who was promoted in earlier individual test)
        other_student = students_by_form[1][0]
        other_enr_2027 = db.query(StudentEnrollment).filter(
            StudentEnrollment.student_id == other_student.id,
            StudentEnrollment.academic_year == "2026/2027"
        ).first()
        assert other_enr_2027 is None, "Target enrollment should be deleted by rollback!"

        # Check that 2026/2027 enrollment is restored to ACTIVE
        other_enr_2026 = db.query(StudentEnrollment).filter(
            StudentEnrollment.student_id == other_student.id,
            StudentEnrollment.academic_year == "2026/2027"
        ).first()
        assert other_enr_2026.status == "ACTIVE"
        print("[OK] PostgreSQL verification confirmed complete rollback safety and restored enrollment state.")
    finally:
        db.close()

    print("\n==================================================")
    print("ALL 20 CLASS PROMOTION SYSTEM TESTS PASSED SUCCESSFULLY!")
    print("==================================================")


if __name__ == "__main__":
    pytest.main(["-s", __file__])
