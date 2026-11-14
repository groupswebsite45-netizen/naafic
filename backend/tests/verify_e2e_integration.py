import requests
import json
import psycopg2
import uuid

BASE_URL = "http://127.0.0.1:8000/api/v1"
DB_PARAMS = {
    "dbname": "hawlwadaag_school_db",
    "user": "postgres",
    "password": "123",
    "host": "localhost",
    "port": "5432"
}

def run_e2e_verification():
    print("==================================================")
    print("HAWLWADAAG SCHOOL MANAGEMENT - E2E INTEGRATION TEST")
    print("==================================================")

    uid = uuid.uuid4().hex[:6].upper()

    # 1. Admin Login
    print("\n[1/7] Logging in as ADMIN...")
    res = requests.post(f"{BASE_URL}/auth/login", json={
        "identifier": "admin",
        "password": "Admin@Hawlwadaag2026"
    })
    assert res.status_code == 200, f"Admin login failed: {res.text}"
    admin_data = res.json()
    admin_token = admin_data["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("[OK] Admin authenticated successfully. Token received.")

    # 2. Admin Dashboard Overview
    print("\n[2/7] Checking Admin Dashboard metrics from PostgreSQL...")
    res = requests.get(f"{BASE_URL}/admin/dashboard", headers=admin_headers)
    assert res.status_code == 200, f"Failed overview: {res.text}"
    overview = res.json()
    metrics = overview["metrics"]
    print(f"[OK] Real metrics retrieved: Students: {metrics['total_students']}, Teachers: {metrics['total_teachers']}, Classes: {metrics['total_classes']}, Outstanding Fees: ${metrics['total_fees_outstanding']:.2f}")

    # 3. Create Class & Subject
    print("\n[3/7] Admin creating Class & Subject...")
    class_code = f"G8-E2E-{uid}"
    res = requests.post(f"{BASE_URL}/classes", json={
        "name": f"Grade 8 E2E {uid}",
        "code": class_code,
        "division": "PRIMARY",
        "level": "Grade 8",
        "section": uid[:2],
        "academic_year": "2026/2027",
        "capacity": 45,
        "status": "ACTIVE"
    }, headers=admin_headers)
    assert res.status_code == 201, f"Create class failed: {res.text}"
    cls = res.json()
    class_id = cls["id"]
    print(f"[OK] Class created: {cls['name']} (ID: {class_id})")

    subject_code = f"SOM-{uid}"
    res = requests.post(f"{BASE_URL}/subjects", json={
        "name": f"Somali Literature {uid}",
        "code": subject_code,
        "department": "Languages",
        "status": "ACTIVE"
    }, headers=admin_headers)
    assert res.status_code == 201, f"Create subject failed: {res.text}"
    subj = res.json()
    subject_id = subj["id"]
    print(f"[OK] Subject created: {subj['name']} (ID: {subject_id})")

    # 4. Create Teacher & Student with Portal Accounts
    print("\n[4/7] Admin registering Teacher & Student with Portal Accounts...")
    teacher_number = f"TCH-{uid}"
    teacher_username = f"teacher_{uid}"
    teacher_password = "TeacherPassword2026"
    res = requests.post(f"{BASE_URL}/teachers", json={
        "teacher_number": teacher_number,
        "first_name": "Khadar",
        "last_name": "Warsame",
        "gender": "Male",
        "email": f"khadar.{uid}@hawlwadaagschool.edu.so",
        "qualification": "B.Ed Somali Language",
        "create_portal_account": True,
        "portal_username": teacher_username,
        "portal_password": teacher_password
    }, headers=admin_headers)
    assert res.status_code == 201, f"Create teacher failed: {res.text}"
    teacher = res.json()
    teacher_id = teacher["id"]
    print(f"[OK] Teacher registered with user account: {teacher['first_name']} {teacher['last_name']} (ID: {teacher_id})")

    # Assign teacher to class & subject
    res = requests.post(f"{BASE_URL}/teachers/{teacher_id}/assignments", json={
        "class_id": class_id,
        "subject_id": subject_id,
        "academic_year": "2026/2027"
    }, headers=admin_headers)
    assert res.status_code == 201, f"Assign teacher failed: {res.text}"
    print(f"[OK] Teacher assigned to Class {cls['name']} & Subject {subj['name']}")

    student_adm = f"ADM-{uid}"
    student_username = f"student_{uid}"
    student_password = "StudentPassword2026"
    res = requests.post(f"{BASE_URL}/students", json={
        "admission_number": student_adm,
        "first_name": "Amina",
        "last_name": "Farah",
        "gender": "Female",
        "guardian_name": "Farah Jama",
        "guardian_phone": "+252615999999",
        "initial_class_id": class_id,
        "academic_year": "2026/2027",
        "create_portal_account": True,
        "portal_username": student_username,
        "portal_password": student_password
    }, headers=admin_headers)
    assert res.status_code == 201, f"Create student failed: {res.text}"
    student = res.json()
    student_id = student["id"]
    print(f"[OK] Student registered & enrolled: {student['first_name']} {student['last_name']} (ID: {student_id})")

    # 5. Teacher Portal Test
    print("\n[5/7] Testing TEACHER Portal Access & Role Authorization...")
    res = requests.post(f"{BASE_URL}/auth/login", json={
        "identifier": teacher_username,
        "password": teacher_password
    })
    assert res.status_code == 200, f"Teacher login failed: {res.text}"
    teacher_auth = res.json()
    teacher_token = teacher_auth["access_token"]
    teacher_headers = {"Authorization": f"Bearer {teacher_token}"}

    # Verify teacher dashboard
    res = requests.get(f"{BASE_URL}/teacher-portal/dashboard", headers=teacher_headers)
    assert res.status_code == 200, f"Teacher dashboard failed: {res.text}"
    t_dash = res.json()
    print(f"[OK] Teacher portal loaded. Assigned classes count: {t_dash['total_classes']}")

    # Verify teacher cannot access admin endpoint (RBAC Protection)
    res = requests.get(f"{BASE_URL}/admin/audit-logs", headers=teacher_headers)
    assert res.status_code == 403, f"Expected 403 Forbidden for teacher accessing admin settings, got {res.status_code}"
    print("[OK] RBAC Enforced: Teacher blocked from administrative settings (403 Forbidden).")

    # 6. Student Portal Test
    print("\n[6/7] Testing STUDENT Portal Access & Isolation...")
    res = requests.post(f"{BASE_URL}/auth/login", json={
        "identifier": student_username,
        "password": student_password
    })
    assert res.status_code == 200, f"Student login failed: {res.text}"
    student_auth = res.json()
    student_token = student_auth["access_token"]
    student_headers = {"Authorization": f"Bearer {student_token}"}

    res = requests.get(f"{BASE_URL}/student-portal/dashboard", headers=student_headers)
    assert res.status_code == 200, f"Student dashboard failed: {res.text}"
    s_dash = res.json()
    print(f"[OK] Student portal loaded for: {s_dash['student']['first_name']} {s_dash['student']['last_name']}")

    # Verify student cannot access admin or teacher endpoints
    res = requests.get(f"{BASE_URL}/teacher-portal/dashboard", headers=student_headers)
    assert res.status_code == 403, f"Expected 403 for student accessing teacher portal, got {res.status_code}"
    print("[OK] RBAC Enforced: Student blocked from teacher portal (403 Forbidden).")

    # 7. Direct PostgreSQL Persistence Verification
    print("\n[7/7] Verifying direct PostgreSQL persistence across tables...")
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()

    cur.execute("SELECT name, code FROM classes WHERE code = %s;", (class_code,))
    class_row = cur.fetchone()
    assert class_row is not None, "Class not found in PostgreSQL!"
    print(f"[OK] PostgreSQL verified: classes -> {class_row[0]} ({class_row[1]})")

    cur.execute("SELECT first_name, last_name, teacher_number FROM teachers WHERE teacher_number = %s;", (teacher_number,))
    teacher_row = cur.fetchone()
    assert teacher_row is not None, "Teacher not found in PostgreSQL!"
    print(f"[OK] PostgreSQL verified: teachers -> {teacher_row[0]} {teacher_row[1]} ({teacher_row[2]})")

    cur.execute("SELECT first_name, last_name, admission_number FROM students WHERE admission_number = %s;", (student_adm,))
    student_row = cur.fetchone()
    assert student_row is not None, "Student not found in PostgreSQL!"
    print(f"[OK] PostgreSQL verified: students -> {student_row[0]} {student_row[1]} ({student_row[2]})")

    cur.close()
    conn.close()

    print("\n==================================================")
    print("ALL END-TO-END & POSTGRESQL VERIFICATIONS PASSED!")
    print("==================================================")

if __name__ == "__main__":
    run_e2e_verification()
