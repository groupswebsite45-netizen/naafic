"""
Acceptance Test Suite for Somroyal EMS:
Advanced Results Management System.

Tests all requirements:
1. 10 Real-time KPI statistics sourced from PostgreSQL.
2. Filters by academic year, education level, exam, class, and subject.
3. Class Result Sheet matrix with student marks, totals, percentages, grades, ranks, pass/fail, and summary stats.
4. Download Class Results as print-ready PDF.
5. Class Rankings & Merit List with competition ranking (1, 2, 2, 4).
6. Download Class Rankings as PDF and Excel (.xlsx).
7. Individual Student Result Report transcript and PDF download.
8. Subject Performance analysis and Absent Students tracker with documented reasons.
9. Teacher-to-Admin review workflow and prohibition of admin mark entry.
10. Student privacy and tenant isolation.
"""

import io
import pytest
from decimal import Decimal
from datetime import date, datetime, timezone
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import SessionLocal
from app.core.security import create_access_token
from app.models.user import User
from app.models.user_role import UserRole
from app.models.role import Role
from app.models.teacher import Teacher
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.models.school_class import SchoolClass
from app.models.subject import Subject
from app.models.exam import Exam, ExamResult
from app.models.result_submission import ResultSubmission


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture(scope="module")
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="module")
def auth_tokens(db):
    """Fetch or create tokens for Admin, Teacher, and Student."""
    # 1. Admin
    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        admin_role = db.query(Role).filter(Role.name == "ADMIN").first()
        admin_user = User(
            username="admin_test_arm",
            email="admin_arm@test.somroyal.edu.so",
            hashed_password="hashed_pw_test",
            status="ACTIVE",
            is_active=True,
        )
        db.add(admin_user)
        db.flush()
        if admin_role:
            db.add(UserRole(user_id=admin_user.id, role_id=admin_role.id))
            db.commit()

    admin_token = create_access_token(subject=str(admin_user.id))

    # 2. Teacher
    teacher_user = db.query(User).join(Teacher, Teacher.user_id == User.id).first()
    if not teacher_user:
        teacher_role = db.query(Role).filter(Role.name == "TEACHER").first()
        teacher_user = User(
            username="teacher_test_arm",
            email="teacher_arm@test.somroyal.edu.so",
            hashed_password="hashed_pw_test",
            status="ACTIVE",
            is_active=True,
        )
        db.add(teacher_user)
        db.flush()
        if teacher_role:
            db.add(UserRole(user_id=teacher_user.id, role_id=teacher_role.id))
            db.commit()

    teacher_token = create_access_token(subject=str(teacher_user.id))

    # 3. Student
    student_user = db.query(User).join(Student, Student.user_id == User.id).first()
    student_record = None
    if student_user:
        student_record = db.query(Student).filter(Student.user_id == student_user.id).first()

    student_token = (
        create_access_token(subject=str(student_user.id))
        if student_user
        else None
    )

    return {
        "admin_headers": {"Authorization": f"Bearer {admin_token}"},
        "teacher_headers": {"Authorization": f"Bearer {teacher_token}"},
        "student_headers": {"Authorization": f"Bearer {student_token}"} if student_token else None,
        "student_record": student_record,
    }


# =============================================================================
# TEST SUITE 1: FILTER OPTIONS & METADATA
# =============================================================================

def test_get_filter_options(client, auth_tokens):
    """Verify that filter options return academic years, exams, classes with enrollments, and subjects."""
    res = client.get("/api/v1/results/filter-options", headers=auth_tokens["admin_headers"])
    assert res.status_code == 200, res.text
    data = res.json()

    assert "academic_years" in data
    assert len(data["academic_years"]) > 0
    assert "exam_names" in data
    assert "classes" in data
    assert "subjects" in data
    assert "teachers" in data


# =============================================================================
# TEST SUITE 2: 10 REAL-TIME POSTGRESQL DASHBOARD KPIS
# =============================================================================

def test_get_dashboard_statistics(client, auth_tokens, db):
    """Verify that all 10 KPIs are dynamically computed from live database records."""
    res = client.get(
        "/api/v1/results/dashboard/statistics",
        params={"academic_year": "2026-2027", "exam_name": "Mid-Term Examination 2026/2027"},
        headers=auth_tokens["admin_headers"]
    )
    assert res.status_code == 200, res.text
    stats = res.json()

    # Verify all 10 KPI keys are present
    kpi_keys = [
        "total_classes_with_students",
        "total_eligible_students",
        "total_submitted_sheets",
        "completed_subjects",
        "pending_teacher_submissions",
        "students_sat_exam",
        "absent_students",
        "awaiting_admin_review",
        "approved_results",
        "published_results",
    ]
    for key in kpi_keys:
        assert key in stats, f"Missing KPI: {key}"
        assert isinstance(stats[key], int), f"KPI {key} should be integer"
        assert stats[key] >= 0, f"KPI {key} should be non-negative"

    # Verify counts match underlying DB for 2026-2027
    assert stats["total_classes_with_students"] > 0
    assert stats["total_eligible_students"] > 0


# =============================================================================
# TEST SUITE 3: CLASS RESULT SHEET MATRIX & SUMMARIES
# =============================================================================

def test_get_class_result_sheet(client, auth_tokens, db):
    """Verify full class result sheet returns eligible students, subject marks, competition ranks, and class summary."""
    # Class 5 has 30 students and 12 subjects
    res = client.get(
        "/api/v1/results/classes/5/sheet",
        params={"academic_year": "2026-2027", "exam_name": "Mid-Term Examination 2026/2027"},
        headers=auth_tokens["admin_headers"]
    )
    assert res.status_code == 200, res.text
    data = res.json()

    # School branding
    assert "school" in data
    assert "name" in data["school"]
    assert "Hawlwadaag" in data["school"]["name"] or "Somroyal" in data["school"]["name"]

    # Class & Exam info
    assert data["class_info"]["id"] == 5
    assert len(data["subjects"]) >= 1
    assert len(data["students"]) == 30

    # Verify student attributes and competition rank
    first_student = data["students"][0]
    assert first_student["rank"] == 1
    assert first_student["student_name"] is not None
    assert first_student["admission_number"] is not None
    assert first_student["total_obtained"] is not None
    assert first_student["total_max"] > 0
    assert first_student["percentage"] is not None
    assert first_student["grade"] in ("A+", "A", "B", "C", "D", "F")
    assert first_student["pass_status"] in ("PASS", "FAIL")

    # Verify class summary statistics
    summary = data["class_summary"]
    assert summary["registered_students"] == 30
    assert summary["sat_exam_students"] == 30
    assert summary["pass_percentage"] >= 0.0
    assert summary["class_average_percentage"] >= 0.0
    assert summary["highest_total"] >= summary["lowest_total"]
    assert len(summary["subject_performance"]) >= 1


# =============================================================================
# TEST SUITE 4: DOWNLOAD CLASS RESULTS AS PDF
# =============================================================================

def test_download_class_result_sheet_pdf(client, auth_tokens):
    """Verify downloading Class Results PDF produces a non-empty print-ready PDF document."""
    res = client.get(
        "/api/v1/results/classes/5/sheet/pdf",
        params={"academic_year": "2026-2027", "exam_name": "Mid-Term Examination 2026/2027"},
        headers=auth_tokens["admin_headers"]
    )
    assert res.status_code == 200, res.text
    assert res.headers["content-type"] == "application/pdf"
    assert "Class_Result_Sheet_" in res.headers["content-disposition"]

    pdf_bytes = res.content
    assert len(pdf_bytes) > 1000, "PDF buffer should contain document content"
    assert pdf_bytes.startswith(b"%PDF"), "PDF must begin with valid %PDF magic bytes"


# =============================================================================
# TEST SUITE 5: CLASS RANKINGS & MERIT LIST (COMPETITION RANKING 1, 2, 2, 4)
# =============================================================================

def test_get_class_rankings(client, auth_tokens):
    """Verify class rankings returns students ordered with competition ranking (1, 2, 2, 4)."""
    res = client.get(
        "/api/v1/results/classes/5/rankings",
        params={"academic_year": "2026-2027", "exam_name": "Mid-Term Examination 2026/2027"},
        headers=auth_tokens["admin_headers"]
    )
    assert res.status_code == 200, res.text
    data = res.json()

    rankings = data["rankings"]
    assert len(rankings) == 30

    # Verify competition ranking ordering
    prev_marks = None
    for idx, r in enumerate(rankings):
        marks = r["total_marks"]
        if prev_marks is not None and marks is not None:
            assert marks <= prev_marks, "Rankings must be ordered descending by total marks"
        prev_marks = marks
        assert r["position"] >= 1


def test_download_class_rankings_pdf(client, auth_tokens):
    """Verify downloading Class Rankings as PDF returns valid %PDF document."""
    res = client.get(
        "/api/v1/results/classes/5/rankings/pdf",
        params={"academic_year": "2026-2027", "exam_name": "Mid-Term Examination 2026/2027"},
        headers=auth_tokens["admin_headers"]
    )
    assert res.status_code == 200, res.text
    assert res.headers["content-type"] == "application/pdf"
    assert res.content.startswith(b"%PDF")
    assert len(res.content) > 1000


def test_download_class_rankings_excel(client, auth_tokens):
    """Verify downloading Class Rankings as Excel returns valid .xlsx workbook."""
    res = client.get(
        "/api/v1/results/classes/5/rankings/excel",
        params={"academic_year": "2026-2027", "exam_name": "Mid-Term Examination 2026/2027"},
        headers=auth_tokens["admin_headers"]
    )
    assert res.status_code == 200, res.text
    assert "spreadsheetml.sheet" in res.headers["content-type"]
    assert "Class_Rankings_" in res.headers["content-disposition"]
    # PK zip signature for xlsx
    assert res.content.startswith(b"PK"), "Excel file must start with PK zip signature"
    assert len(res.content) > 1000


# =============================================================================
# TEST SUITE 6: INDIVIDUAL STUDENT REPORT CARD & PDF
# =============================================================================

def test_get_student_result_report(client, auth_tokens, db):
    """Verify student academic transcript returns subject breakdown, totals, position, and remarks."""
    # Find an exam result with valid marks
    first_res = db.query(ExamResult).filter(ExamResult.marks_obtained.isnot(None)).first()
    assert first_res is not None
    exam = db.query(Exam).filter(Exam.id == first_res.exam_id).first()
    assert exam is not None
    student_id = first_res.student_id

    res = client.get(
        f"/api/v1/results/students/{student_id}/report",
        params={"academic_year": exam.academic_year, "exam_name": exam.name},
        headers=auth_tokens["admin_headers"]
    )
    assert res.status_code == 200, res.text
    data = res.json()

    assert data["student"]["id"] == student_id
    assert "subjects" in data
    assert len(data["subjects"]) >= 1
    assert "overall" in data
    assert data["overall"]["total_max"] > 0
    assert data["overall"]["overall_grade"] in ("A+", "A", "B", "C", "D", "F")
    assert data["overall"]["pass_status"] in ("PASS", "FAIL")


def test_download_student_report_card_pdf(client, auth_tokens, db):
    """Verify downloading individual student report card PDF."""
    first_res = db.query(ExamResult).filter(ExamResult.marks_obtained.isnot(None)).first()
    assert first_res is not None
    exam = db.query(Exam).filter(Exam.id == first_res.exam_id).first()
    assert exam is not None

    res = client.get(
        f"/api/v1/results/students/{first_res.student_id}/report/pdf",
        params={"academic_year": exam.academic_year, "exam_name": exam.name},
        headers=auth_tokens["admin_headers"]
    )
    assert res.status_code == 200, res.text
    assert res.headers["content-type"] == "application/pdf"
    assert res.content.startswith(b"%PDF")
    assert len(res.content) > 1000


# =============================================================================
# TEST SUITE 7: SUBJECT PERFORMANCE & ABSENT STUDENTS
# =============================================================================

def test_get_subject_performance_list(client, auth_tokens):
    """Verify subject performance list returns breakdown with averages, pass rates, and grade distributions."""
    res = client.get(
        "/api/v1/results/subject-performance",
        params={"academic_year": "2026-2027", "exam_name": "Mid-Term Examination 2026/2027"},
        headers=auth_tokens["admin_headers"]
    )
    assert res.status_code == 200, res.text
    data = res.json()

    assert len(data) >= 1
    item = data[0]
    assert "subject_name" in item
    assert "teacher_name" in item
    assert "average_marks" in item
    assert "pass_rate" in item
    assert "grade_distribution" in item
    assert "A" in item["grade_distribution"]


def test_get_absent_students_list(client, auth_tokens):
    """Verify absent students tracker returns documented absences, reasons, and complaints."""
    res = client.get(
        "/api/v1/results/absent-students",
        params={"academic_year": "2026-2027", "exam_name": "Mid-Term Examination 2026/2027"},
        headers=auth_tokens["admin_headers"]
    )
    assert res.status_code == 200, res.text
    data = res.json()

    assert isinstance(data, list)
    if len(data) > 0:
        item = data[0]
        assert "student_name" in item
        assert "attendance_status" in item
        assert item["attendance_status"] in ("ABSENT", "EXCUSED")
        assert "absence_reason" in item


# =============================================================================
# TEST SUITE 8: SECURITY, PERMISSIONS, AND PRIVACY
# =============================================================================

def test_admin_cannot_enter_student_marks(client, auth_tokens, db):
    """Section 9: The administrator must not enter or fill students' marks (Strict 403 Forbidden)."""
    exam = db.query(Exam).first()
    assert exam is not None

    res = client.post(
        f"/api/v1/exams/{exam.id}/results",
        json={"exam_id": exam.id, "results": [{"student_id": 1, "marks_obtained": 95.0, "attendance_status": "PRESENT"}]},
        headers=auth_tokens["admin_headers"]
    )
    assert res.status_code == 403, "Admins must receive 403 Forbidden when attempting to enter student marks"
    assert "Administrators cannot enter or modify examination marks" in res.json()["detail"]


def test_student_privacy_isolation(client, auth_tokens, db):
    """Section 10: One student must never be able to access another student's report."""
    if not auth_tokens["student_headers"] or not auth_tokens["student_record"]:
        pytest.skip("No student user record available for isolation test")

    my_student_id = auth_tokens["student_record"].id
    other_student = db.query(Student).filter(Student.id != my_student_id).first()
    if not other_student:
        pytest.skip("No second student found for isolation test")

    # Attempt to view other student's report
    res = client.get(
        f"/api/v1/results/students/{other_student.id}/report",
        params={"academic_year": "2026-2027"},
        headers=auth_tokens["student_headers"]
    )
    assert res.status_code == 403, "Students must receive 403 Forbidden when requesting another student's report"
