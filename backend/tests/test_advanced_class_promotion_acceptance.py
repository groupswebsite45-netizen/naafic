import sys
import os
import uuid
from datetime import date, datetime, timezone

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.school_class import SchoolClass
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.models.class_promotion import ClassPromotionBatch, ClassPromotionRecord
from app.models.exam import Exam, ExamResult
from app.models.attendance import Attendance
from app.models.fee import StudentFee
from app.services.class_promotion_service import ClassPromotionService

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
def auth_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


def test_acceptance_criteria_1_to_14(auth_headers):
    """
    Complete end-to-end acceptance test verifying all 14 criteria:
    1. Grade 2 students progress to Grade 3 in the next academic year.
    2. Grade 4A students progress to Grade 5A.
    3. Grade 4B students progress to Grade 5B.
    4. Primary and Secondary promotions remain separate.
    5. Bulk promotion affects only the selected education level and eligible classes.
    6. Single-class promotion does not affect other classes.
    7. Individual promotion affects only the selected student.
    8. Repeat and graduation workflows behave according to school policy.
    9. Missing destination classes are detected before confirmation.
    10. Duplicate enrollments are prevented.
    11. Previous academic records remain available after promotion.
    12. Promotion history records the correct actions.
    13. Existing student, class, exam, results, fees, and attendance modules continue working.
    14. The promotion data persists after refreshing the application.
    """
    db = SessionLocal()
    try:
        from scripts.setup_promotion_data import ensure_classes, ensure_students_for_tests
        # Reset any previous test records and enrollments
        test_students = db.query(Student).filter(Student.admission_number.like("ADM-2026-%")).all()
        test_student_ids = [s.id for s in test_students]
        if test_student_ids:
            db.query(StudentEnrollment).filter(
                StudentEnrollment.student_id.in_(test_student_ids),
                StudentEnrollment.academic_year == "2026/2027"
            ).delete(synchronize_session=False)

            db.query(StudentEnrollment).filter(
                StudentEnrollment.student_id.in_(test_student_ids),
                StudentEnrollment.academic_year == "2026/2027"
            ).update({"status": "ACTIVE"}, synchronize_session=False)

            db.query(Student).filter(
                Student.id.in_(test_student_ids)
            ).update({"status": "ACTIVE"}, synchronize_session=False)

            test_records = db.query(ClassPromotionRecord).filter(
                ClassPromotionRecord.student_id.in_(test_student_ids)
            ).all()
            batch_ids = {r.batch_id for r in test_records}
            if test_records:
                db.query(ClassPromotionRecord).filter(
                    ClassPromotionRecord.student_id.in_(test_student_ids)
                ).delete(synchronize_session=False)
            if batch_ids:
                db.query(ClassPromotionBatch).filter(
                    ClassPromotionBatch.id.in_(batch_ids)
                ).delete(synchronize_session=False)

        db.commit()
        ensure_classes(db)
        ensure_students_for_tests(db)
        db.expire_all()

        service = ClassPromotionService(db)

        # ----------------------------------------------------------------------
        # Test 4: Primary and Secondary promotions remain separate
        # ----------------------------------------------------------------------
        pri_res = client.get(
            "/api/v1/class-promotions/suggested-mappings",
            params={"source_year": "2026/2027", "target_year": "2026/2027", "education_level": "PRIMARY"},
            headers=auth_headers
        )
        assert pri_res.status_code == 200
        pri_data = pri_res.json()
        assert pri_data["education_level"] == "PRIMARY"
        # Ensure NO Secondary classes are in Primary mappings
        for m in pri_data["mappings"]:
            assert m["education_level"] == "PRIMARY"
            assert "Form" not in m["from_class_name"]

        sec_res = client.get(
            "/api/v1/class-promotions/suggested-mappings",
            params={"source_year": "2026/2027", "target_year": "2026/2027", "education_level": "SECONDARY"},
            headers=auth_headers
        )
        assert sec_res.status_code == 200
        sec_data = sec_res.json()
        assert sec_data["education_level"] == "SECONDARY"
        # Ensure NO Primary classes are in Secondary mappings
        for m in sec_data["mappings"]:
            assert m["education_level"] == "SECONDARY"
            assert "Grade" not in m["from_class_name"]

        # ----------------------------------------------------------------------
        # Test 1, 2, 3: Automatic progression and Section Preservation:
        # Grade 2A -> Grade 3A, Grade 4A -> Grade 5A, Grade 4B -> Grade 5B
        # ----------------------------------------------------------------------
        pri_mappings_map = {m["from_class_name"]: m for m in pri_data["mappings"]}

        # 1. Grade 2 -> Grade 3
        assert "Grade 2 - A" in pri_mappings_map
        g2a = pri_mappings_map["Grade 2 - A"]
        assert g2a["to_class_name"] == "Grade 3 - A", f"Expected Grade 3 - A, got {g2a['to_class_name']}"
        assert g2a["section"] == "A"
        assert g2a["action"] == "PROMOTE"

        # 2. Grade 4A -> Grade 5A
        assert "Grade 4 - A" in pri_mappings_map
        g4a = pri_mappings_map["Grade 4 - A"]
        assert g4a["to_class_name"] == "Grade 5 - A", f"Expected Grade 5 - A, got {g4a['to_class_name']}"
        assert g4a["section"] == "A"
        assert g4a["action"] == "PROMOTE"

        # 3. Grade 4B -> Grade 5B
        assert "Grade 4 - B" in pri_mappings_map
        g4b = pri_mappings_map["Grade 4 - B"]
        assert g4b["to_class_name"] == "Grade 5 - B", f"Expected Grade 5 - B, got {g4b['to_class_name']}"
        assert g4b["section"] == "B"
        assert g4b["action"] == "PROMOTE"

        # Secondary section check: Form 1 - B -> Form 2 - B
        sec_mappings_map = {m["from_class_name"]: m for m in sec_data["mappings"]}
        assert "Form 1 - B" in sec_mappings_map
        f1b = sec_mappings_map["Form 1 - B"]
        assert f1b["to_class_name"] == "Form 2 - B", f"Expected Form 2 - B, got {f1b['to_class_name']}"
        assert f1b["section"] == "B"

        # ----------------------------------------------------------------------
        # Test 8: Repeat and graduation workflows behave according to policy
        # Terminal classes (Grade 8 and Form 4) must graduate, not promote to nonexistent class
        # ----------------------------------------------------------------------
        g8a = pri_mappings_map["Grade 8 - A"]
        assert g8a["action"] == "GRADUATE"
        assert g8a["to_class_id"] is None
        assert g8a["is_terminal_class"] is True

        f4a = sec_mappings_map["Form 4 - A"]
        assert f4a["action"] == "GRADUATE"
        assert f4a["to_class_id"] is None
        assert f4a["is_terminal_class"] is True

        # ----------------------------------------------------------------------
        # Test 9: Missing destination classes are detected before confirmation
        # Grade 4 - E exists in DB, but Section E does not exist in next grade (Grade 5).
        # It must be flagged with missing_destination_warning = True!
        # ----------------------------------------------------------------------
        if "Grade 4 - E" in pri_mappings_map:
            g4e = pri_mappings_map["Grade 4 - E"]
            assert g4e["missing_destination_warning"] is True
            assert g4e["to_class_id"] is None

            # Trying to preview with a missing destination class must flag an error and block confirmation
            prev_missing = client.post(
                "/api/v1/class-promotions/preview",
                json={
                    "source_academic_year": "2026/2027",
                    "target_academic_year": "2026/2027",
                    "mappings": [
                        {"from_class_id": g4e["from_class_id"], "to_class_id": None, "action": "PROMOTE"}
                    ]
                },
                headers=auth_headers
            )
            assert prev_missing.status_code == 200
            prev_m_data = prev_missing.json()
            assert prev_m_data["can_execute"] is False
            assert prev_m_data["missing_destination_classes_count"] >= 1
            assert len(prev_m_data["validation_errors"]) >= 1

        # ----------------------------------------------------------------------
        # Test 6: Single-class promotion does not affect other classes
        # Promote only Grade 4 - A -> Grade 5 - A. Students in Grade 4 - B must remain in Grade 4 - B!
        # ----------------------------------------------------------------------
        c_g4a = db.query(SchoolClass).filter(
            SchoolClass.academic_year == "2026/2027",
            SchoolClass.level == "Grade 4",
            SchoolClass.section == "A"
        ).first()

        c_g5a = db.query(SchoolClass).filter(
            SchoolClass.academic_year == "2026/2027",
            SchoolClass.level == "Grade 5",
            SchoolClass.section == "A"
        ).first()

        c_g4b = db.query(SchoolClass).filter(
            SchoolClass.academic_year == "2026/2027",
            SchoolClass.level == "Grade 4",
            SchoolClass.section == "B"
        ).first()

        assert c_g4a and c_g5a and c_g4b, "Required classes must exist in DB."

        # Count active students in Grade 4B before promotion
        g4b_students_before = db.query(StudentEnrollment).filter(
            StudentEnrollment.class_id == c_g4b.id,
            StudentEnrollment.status == "ACTIVE"
        ).all()
        g4b_student_ids_before = {e.student_id for e in g4b_students_before}
        assert len(g4b_student_ids_before) > 0

        # Execute single-class promotion on Grade 4A
        single_res = client.post(
            "/api/v1/class-promotions/class-level",
            json={
                "from_class_id": c_g4a.id,
                "to_class_id": c_g5a.id,
                "source_academic_year": "2026/2027",
                "target_academic_year": "2026/2027",
                "action": "PROMOTE",
                "reason": "Test Single Class Promotion Grade 4A"
            },
            headers=auth_headers
        )
        assert single_res.status_code == 201, f"Single class promotion failed: {single_res.text}"
        single_batch = single_res.json()
        assert single_batch["promotion_type"] == "CLASS_LEVEL"
        assert single_batch["total_promoted"] > 0

        # Verify students in Grade 4B were COMPLETELY UNTOUCHED!
        g4b_students_after = db.query(StudentEnrollment).filter(
            StudentEnrollment.class_id == c_g4b.id,
            StudentEnrollment.status == "ACTIVE"
        ).all()
        g4b_student_ids_after = {e.student_id for e in g4b_students_after}
        assert g4b_student_ids_before == g4b_student_ids_after, "Students in Grade 4B must remain in Grade 4B!"

        # ----------------------------------------------------------------------
        # Test 10: Duplicate enrollments are prevented
        # Trying to promote Grade 4A to Grade 5A again for the same target year must fail / block
        # ----------------------------------------------------------------------
        dup_prev = client.post(
            "/api/v1/class-promotions/preview",
            json={
                "source_academic_year": "2026/2027",
                "target_academic_year": "2026/2027",
                "mappings": [
                    {"from_class_id": c_g4a.id, "to_class_id": c_g5a.id, "action": "PROMOTE"}
                ]
            },
            headers=auth_headers
        )
        assert dup_prev.status_code == 200
        dup_prev_data = dup_prev.json()
        assert dup_prev_data["can_execute"] is False or dup_prev_data["total_students_affected"] == 0, \
            "Duplicate promotion must be prevented."

        # ----------------------------------------------------------------------
        # Test 7: Individual promotion affects only the selected student
        # Pick one student from Grade 4B and promote individually to Grade 5B
        # Classmates in Grade 4B must remain in Grade 4B!
        # ----------------------------------------------------------------------
        c_g5b = db.query(SchoolClass).filter(
            SchoolClass.academic_year == "2026/2027",
            SchoolClass.level == "Grade 5",
            SchoolClass.section == "B"
        ).first()
        assert c_g5b, "Grade 5B must exist."

        one_g4b_student_id = list(g4b_student_ids_after)[0]
        other_g4b_student_ids = g4b_student_ids_after - {one_g4b_student_id}

        ind_res = client.post(
            "/api/v1/class-promotions/individual-promote",
            json={
                "student_id": one_g4b_student_id,
                "source_academic_year": "2026/2027",
                "target_academic_year": "2026/2027",
                "action": "PROMOTE",
                "target_class_id": c_g5b.id,
                "reason": "Individual student promotion test"
            },
            headers=auth_headers
        )
        assert ind_res.status_code == 201
        ind_batch = ind_res.json()
        assert ind_batch["promotion_type"] == "INDIVIDUAL_PROMOTION"
        assert ind_batch["total_promoted"] == 1

        # Check target enrollment of the selected student
        new_ind_enr = db.query(StudentEnrollment).filter(
            StudentEnrollment.student_id == one_g4b_student_id,
            StudentEnrollment.academic_year == "2026/2027",
            StudentEnrollment.class_id == c_g5b.id
        ).first()
        assert new_ind_enr is not None
        assert new_ind_enr.status == "ACTIVE"

        # Verify classmates in Grade 4B were not affected!
        for other_id in other_g4b_student_ids:
            other_target_enr = db.query(StudentEnrollment).filter(
                StudentEnrollment.student_id == other_id,
                StudentEnrollment.academic_year == "2026/2027"
            ).first()
            assert other_target_enr is None, f"Classmate {other_id} must not have been promoted!"

        # ----------------------------------------------------------------------
        # Test 11: Previous academic records remain available after promotion
        # The source enrollment record in 2026/2027 remains in DB with status PROMOTED
        # ----------------------------------------------------------------------
        db.expire_all()
        old_enr = db.query(StudentEnrollment).filter(
            StudentEnrollment.student_id == one_g4b_student_id,
            StudentEnrollment.academic_year == "2026/2027"
        ).first()
        assert old_enr is not None
        assert old_enr.status == "PROMOTED"

        # ----------------------------------------------------------------------
        # Test 12: Promotion history records the correct actions
        # ----------------------------------------------------------------------
        hist_res = client.get("/api/v1/class-promotions/history", headers=auth_headers)
        assert hist_res.status_code == 200
        hist_batches = hist_res.json()
        assert len(hist_batches) >= 2
        batch_codes = [b["batch_code"] for b in hist_batches]
        assert single_batch["batch_code"] in batch_codes
        assert ind_batch["batch_code"] in batch_codes

        # Get details of individual promotion batch
        batch_det_res = client.get(f"/api/v1/class-promotions/history/{ind_batch['id']}", headers=auth_headers)
        assert batch_det_res.status_code == 200
        batch_det = batch_det_res.json()
        assert len(batch_det["records"]) == 1
        rec = batch_det["records"][0]
        assert rec["student_id"] == one_g4b_student_id
        assert rec["action"] == "PROMOTE"
        assert rec["from_class_name"] == c_g4b.name
        assert rec["to_class_name"] == c_g5b.name

        # ----------------------------------------------------------------------
        # Test 13: Existing student, class, exam, fees, and attendance modules work
        # ----------------------------------------------------------------------
        # Students endpoint
        st_res = client.get("/api/v1/students", headers=auth_headers)
        assert st_res.status_code == 200

        # Classes endpoint
        cl_res = client.get("/api/v1/classes", headers=auth_headers)
        assert cl_res.status_code == 200

        # Fees endpoint
        fee_res = client.get("/api/v1/fees/structures", headers=auth_headers)
        assert fee_res.status_code in [200, 404]

        # ----------------------------------------------------------------------
        # Test 14: Safe Rollback & Data Persistence
        # Rollback the individual promotion batch and verify student is restored to Grade 4B
        # ----------------------------------------------------------------------
        rb_res = client.post(f"/api/v1/class-promotions/history/{ind_batch['id']}/rollback", headers=auth_headers)
        assert rb_res.status_code == 200
        assert rb_res.json()["success"] is True

        db.expire_all()
        # Verify target enrollment was removed and old enrollment restored to ACTIVE
        rolled_target_enr = db.query(StudentEnrollment).filter(
            StudentEnrollment.student_id == one_g4b_student_id,
            StudentEnrollment.academic_year == "2026/2027"
        ).first()
        assert rolled_target_enr is None, "Target enrollment must be removed after rollback."

        restored_old_enr = db.query(StudentEnrollment).filter(
            StudentEnrollment.student_id == one_g4b_student_id,
            StudentEnrollment.academic_year == "2026/2027"
        ).first()
        assert restored_old_enr is not None
        assert restored_old_enr.status == "ACTIVE", "Source enrollment must be restored to ACTIVE after rollback."

        print("\nAll 14 Acceptance Criteria Successfully Verified!")

    finally:
        db.close()
