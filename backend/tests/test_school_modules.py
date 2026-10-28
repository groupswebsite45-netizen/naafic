import uuid
from decimal import Decimal
from datetime import date, time
from app.core.config import settings


def get_admin_headers(client):
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"identifier": settings.INITIAL_ADMIN_USERNAME, "password": settings.INITIAL_ADMIN_PASSWORD}
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def get_teacher_headers(client, username="teacher.ahmed"):
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"identifier": username, "password": "Teacher@Hawlwadaag2026"}
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def get_student_headers(client, username="student.mustaf"):
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"identifier": username, "password": "Student@Hawlwadaag2026"}
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# 1. Classes Tests
def test_classes_crud(client):
    headers = get_admin_headers(client)
    unique_code = f"G7-{uuid.uuid4().hex[:6].upper()}"
    sec_code = uuid.uuid4().hex[:4].upper()

    # Create Class
    create_resp = client.post(
        "/api/v1/classes",
        headers=headers,
        json={
            "name": f"Grade 7 Section {unique_code}",
            "code": unique_code,
            "section": sec_code,
            "division": "PRIMARY",
            "level": "Grade 7",
            "academic_year": "2026/2027",
            "capacity": 35,
            "description": "Test grade section"
        }
    )
    assert create_resp.status_code == 201
    class_data = create_resp.json()
    class_id = class_data["id"]
    assert class_data["code"] == unique_code

    # List & Search
    list_resp = client.get(f"/api/v1/classes?query={unique_code}", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 1

    # Update
    update_resp = client.put(
        f"/api/v1/classes/{class_id}",
        headers=headers,
        json={"name": f"Grade 7 Stream Emerald {unique_code}"}
    )
    assert update_resp.status_code == 200

    # Deactivate
    del_resp = client.delete(f"/api/v1/classes/{class_id}", headers=headers)
    assert del_resp.status_code == 200


# 2. Subjects Tests
def test_subjects_crud(client):
    headers = get_admin_headers(client)
    unique_code = f"SCI-{uuid.uuid4().hex[:6].upper()}"

    # Create Subject
    create_resp = client.post(
        "/api/v1/subjects",
        headers=headers,
        json={
            "name": f"General Science {unique_code}",
            "code": unique_code,
            "department": "Sciences",
            "description": "Basic experimental science"
        }
    )
    assert create_resp.status_code == 201
    subj_data = create_resp.json()
    assert subj_data["code"] == unique_code

    # Duplicate code should fail with 409
    dup_resp = client.post(
        "/api/v1/subjects",
        headers=headers,
        json={"name": "Duplicate Subject", "code": unique_code}
    )
    assert dup_resp.status_code == 409


# 3. Timetable Conflict Check
def test_timetable_conflict_prevention(client):
    headers = get_admin_headers(client)

    # 1. Create a fresh class and subject for conflict testing
    hex_id = uuid.uuid4().hex[:6].upper()
    c_code = f"CONF-{hex_id}"
    c_resp = client.post(
        "/api/v1/classes",
        headers=headers,
        json={
            "name": f"Timetable Test Class {hex_id}",
            "code": c_code,
            "section": hex_id,
            "division": "PRIMARY",
            "level": "Grade 7",
            "academic_year": "2026/2027",
            "capacity": 30
        }
    )
    c_id = c_resp.json()["id"]

    subjects = client.get("/api/v1/subjects", headers=headers).json()
    s1_id = subjects[0]["id"]
    s2_id = subjects[1]["id"]

    # Slot 1: Friday 06:00 - 07:00
    slot1_resp = client.post(
        "/api/v1/timetable",
        headers=headers,
        json={
            "class_id": c_id,
            "subject_id": s1_id,
            "teacher_id": None,
            "academic_year": "2025-2026",
            "day_of_week": "Friday",
            "start_time": "06:00:00",
            "end_time": "07:00:00",
            "room": f"Room-{uuid.uuid4().hex[:4]}"
        }
    )
    assert slot1_resp.status_code == 201

    # Overlapping Slot for Same Class -> Must Fail with 409 Conflict
    overlap_resp = client.post(
        "/api/v1/timetable",
        headers=headers,
        json={
            "class_id": c_id,
            "subject_id": s2_id,
            "teacher_id": None,
            "academic_year": "2025-2026",
            "day_of_week": "Friday",
            "start_time": "06:30:00",
            "end_time": "07:30:00",
            "room": "Different Room"
        }
    )
    assert overlap_resp.status_code == 409
    assert "already has" in overlap_resp.json()["error"]["message"]

    # Cleanup created test class and timetable entry
    client.delete(f"/api/v1/classes/{c_id}", headers=headers)


# 4. Fees & Balance Calculation
def test_fee_balance_calculation(client):
    headers = get_admin_headers(client)

    # 1. List student invoices
    res = client.get("/api/v1/fees/invoices", headers=headers).json()
    invoices = res.get("items", res) if isinstance(res, dict) else res
    assert len(invoices) > 0
    invoice = invoices[0]

    initial_balance = invoice["balance_remaining"]
    assert initial_balance >= 0

    # 2. Financial summary
    summary_resp = client.get("/api/v1/fees/summary", headers=headers)
    assert summary_resp.status_code == 200
    summary = summary_resp.json()
    assert summary["total_billed"] > 0
    assert summary["total_collected"] >= 0


# 5. Teacher Portal Isolation
def test_teacher_portal_isolation(client):
    teacher_headers = get_teacher_headers(client, "teacher.ahmed")

    # Teacher dashboard
    dash_resp = client.get("/api/v1/teacher-portal/dashboard", headers=teacher_headers)
    assert dash_resp.status_code == 200
    dash_data = dash_resp.json()
    assert dash_data["teacher"]["teacher_number"] == "TCH-001"
    assert len(dash_data["assigned_classes"]) > 0

    assigned_class_id = dash_data["assigned_classes"][0]["class_id"]

    # Teacher should view students in assigned class
    class_stud_resp = client.get(
        f"/api/v1/teacher-portal/classes/{assigned_class_id}/students",
        headers=teacher_headers
    )
    assert class_stud_resp.status_code == 200
    assert len(class_stud_resp.json()["students"]) > 0

    # Teacher accessing unassigned class (e.g., class_id 9999) -> 403 Forbidden
    unauth_resp = client.get(
        "/api/v1/teacher-portal/classes/9999/students",
        headers=teacher_headers
    )
    assert unauth_resp.status_code == 403


# 6. Student Portal Isolation
def test_student_portal_isolation(client):
    student_headers = get_student_headers(client, "student.mustaf")

    # Student dashboard
    dash_resp = client.get("/api/v1/student-portal/dashboard", headers=student_headers)
    assert dash_resp.status_code == 200
    data = dash_resp.json()
    assert data["student"]["admission_number"] == "ADM-2026-001"
    assert data["total_fees_due"] > 0

    # Student fees
    fees_resp = client.get("/api/v1/student-portal/fees", headers=student_headers)
    assert fees_resp.status_code == 200
    assert len(fees_resp.json()) > 0

    # Student exam results
    exams_resp = client.get("/api/v1/student-portal/exams", headers=student_headers)
    assert exams_resp.status_code == 200

    # Student attempting to access Admin endpoint -> 403 Forbidden
    admin_attempt = client.get("/api/v1/admin/dashboard", headers=student_headers)
    assert admin_attempt.status_code == 403
