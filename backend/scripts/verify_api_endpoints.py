import sys
import os

# Ensure backend root in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.student import Student

client = TestClient(app)

def run_api_verification():
    print("==================================================")
    print("VERIFYING API ENDPOINTS & LIVE PORTAL CONTRACTS")
    print("==================================================")

    # 1. Admin login
    res = client.post("/api/v1/auth/login", json={"identifier": "admin", "password": "Admin@Hawlwadaag2026"})
    assert res.status_code == 200, f"Admin login failed: {res.text}"
    admin_token = res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("[OK] Admin login successful.")

    # 2. Student Summary
    res = client.get("/api/v1/students/summary?academic_year=2026/2027", headers=admin_headers)
    assert res.status_code == 200, f"Summary failed: {res.text}"
    summary = res.json()
    print(f"[OK] Student Summary (2026/2027): {summary}")
    assert summary["total_students"] == 20, f"Expected 20 total students, got {summary['total_students']}"
    assert summary["active_students"] == 20, f"Expected 20 active students, got {summary['active_students']}"
    assert summary["inactive_students"] == 0, f"Expected 0 inactive students, got {summary['inactive_students']}"
    assert summary["unassigned_students"] == 0, f"Expected 0 unassigned students, got {summary['unassigned_students']}"

    # 3. List Students
    res = client.get("/api/v1/students?academic_year=2026/2027&limit=50", headers=admin_headers)
    assert res.status_code == 200, f"List students failed: {res.text}"
    students_data = res.json()
    items = students_data if isinstance(students_data, list) else students_data.get("items", [])
    print(f"[OK] Listed {len(items)} students for academic year 2026/2027.")
    assert len(items) == 20, f"Expected exactly 20 students, got {len(items)}"

    # 4. Class Filter Options for Admin Students
    res = client.get("/api/v1/students/class-filter-options?academic_year=2026/2027", headers=admin_headers)
    assert res.status_code == 200, f"Class filter options failed: {res.text}"
    filter_classes = res.json()
    print(f"[OK] Class filter options returned {len(filter_classes)} active classes with students:")
    for fc in filter_classes:
        print(f"     [{fc['id']}] {fc['name']} ({fc['division']}, {fc['academic_year']}) - {fc['students_count']} students")
    
    assert len(filter_classes) == 4, f"Expected exactly 4 active classes, got {len(filter_classes)}"
    c_names = set(c["name"] for c in filter_classes)
    assert c_names == {"Grade 7 - A", "Grade 8 - A", "Form 1 - A", "Form 2 - A"}

    # 5. Fees Classes - Primary & Secondary Isolation
    res_p = client.get("/api/v1/fees/classes?academic_year=2026/2027&education_level=PRIMARY", headers=admin_headers)
    assert res_p.status_code == 200
    p_classes = res_p.json()
    print(f"[OK] Fees Primary classes ({len(p_classes)}): {[c['name'] for c in p_classes]}")
    for pc in p_classes:
        assert pc["division"] == "PRIMARY"
        assert "Grade" in pc["name"]
        assert "Form" not in pc["name"]

    res_s = client.get("/api/v1/fees/classes?academic_year=2026/2027&education_level=SECONDARY", headers=admin_headers)
    assert res_s.status_code == 200
    s_classes = res_s.json()
    print(f"[OK] Fees Secondary classes ({len(s_classes)}): {[c['name'] for c in s_classes]}")
    for sc in s_classes:
        assert sc["division"] == "SECONDARY"
        assert "Form" in sc["name"]
        assert "Grade" not in sc["name"]

    # 6. Outstanding Fees Audit
    res_out = client.get("/api/v1/fees/outstanding?academic_year=2026/2027", headers=admin_headers)
    assert res_out.status_code == 200
    out_data = res_out.json()
    print(f"[OK] Outstanding Fees Total Students: {out_data['total_students']}")
    # Ensure no deleted student appears
    db = SessionLocal()
    valid_ids = set(s.id for s in db.query(Student.id).all())
    db.close()
    for item in out_data.get("items", []):
        assert item["student_id"] in valid_ids, f"Deleted student {item['student_id']} in outstanding list!"

    # 7. Student Portal Access for all 20 students
    print("\n--- Verifying Student Portal Authentication for Retained 20 Students ---")
    db = SessionLocal()
    all_retained = db.query(Student).order_by(Student.id).all()
    for st in all_retained:
        assert st.user is not None, f"Student {st.id} missing user object!"
        username = st.user.username
        # Authenticate
        login_res = client.post("/api/v1/auth/login", json={"identifier": username, "password": "Student@Hawlwadaag2026"})
        assert login_res.status_code == 200, f"Login failed for {username}: {login_res.text}"
        st_token = login_res.json()["access_token"]
        st_headers = {"Authorization": f"Bearer {st_token}"}

        # Check profile
        prof_res = client.get("/api/v1/student-portal/profile", headers=st_headers)
        assert prof_res.status_code == 200
        prof = prof_res.json()
        assert prof["admission_number"] == st.admission_number
        assert prof["full_name"] == st.full_name
        print(f"  [OK] Portal user verified: {username:25s} -> {st.full_name} ({st.admission_number})")
    db.close()

    print("\n==================================================")
    print("[ALL API ENDPOINT & CONTRACT VERIFICATIONS PASSED!]")
    print("==================================================")

if __name__ == "__main__":
    run_api_verification()
