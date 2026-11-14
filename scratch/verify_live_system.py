import sys, os
from pathlib import Path
import requests

BACKEND_DIR = Path("backend").resolve()
sys.path.insert(0, str(BACKEND_DIR))
from dotenv import load_dotenv
load_dotenv(BACKEND_DIR / ".env")

from app.core.database import engine
from sqlalchemy import text, inspect

BASE_URL = "http://127.0.0.1:8000/api/v1"

print("==================== DATABASE INTEGRITY CHECK ====================")
with engine.connect() as conn:
    inspector = inspect(conn)
    tables = inspector.get_table_names()
    total_violations = 0
    for table in tables:
        cols = [c["name"] for c in inspector.get_columns(table)]
        year_cols = [c for c in cols if "year" in c.lower() or "academic" in c.lower()]
        for yc in year_cols:
            cnt = conn.execute(text(f"SELECT count(*) FROM {table} WHERE {yc} != '2026/2027'")).scalar()
            if cnt > 0:
                print(f"VIOLATION: {table}.{yc} has {cnt} rows != '2026/2027'")
                total_violations += cnt
    
    if total_violations == 0:
        print("DATABASE CHECK PASSED: 100% of rows across all tables have academic_year = '2026/2027'!")
    else:
        print(f"DATABASE CHECK FAILED with {total_violations} violations!")
        sys.exit(1)

print("\n==================== LIVE API ENDPOINTS CHECK ====================")
# 1. Admin login
login_res = requests.post(f"{BASE_URL}/auth/login", json={"identifier": "admin", "password": "Admin@Hawlwadaag2026"})
assert login_res.status_code == 200, f"Admin login failed: {login_res.text}"
admin_token = login_res.json()["access_token"]
headers = {"Authorization": f"Bearer {admin_token}"}
print("Admin Login: SUCCESS")

# 2. Exams Filter Options
res = requests.get(f"{BASE_URL}/exams/filter-options", headers=headers)
assert res.status_code == 200, f"Exams filter options failed: {res.text}"
ay = res.json().get("academic_years", [])
print(f"GET /exams/filter-options -> academic_years: {ay}")
assert ay == ["2026/2027"], f"Expected ['2026/2027'], got {ay}"

# 3. Timetables Filter Options
res = requests.get(f"{BASE_URL}/timetable/filter-options", headers=headers)
assert res.status_code == 200, f"Timetables filter options failed: {res.text}"
ay = res.json().get("academic_years", [])
print(f"GET /timetable/filter-options -> academic_years: {ay}")
assert ay == ["2026/2027"], f"Expected ['2026/2027'], got {ay}"

# 4. Results Filter Options
res = requests.get(f"{BASE_URL}/results/filter-options", headers=headers)
assert res.status_code == 200, f"Results filter options failed: {res.text}"
ay = res.json().get("academic_years", [])
print(f"GET /results/filter-options -> academic_years: {ay}")
assert ay == ["2026/2027"], f"Expected ['2026/2027'], got {ay}"

# 5. Admin Attendance Filter Options
res = requests.get(f"{BASE_URL}/admin/attendance/filter-options", headers=headers)
assert res.status_code == 200, f"Attendance filter options failed: {res.text}"
ay = res.json().get("academic_years", [])
print(f"GET /admin/attendance/filter-options -> academic_years: {ay}")
assert ay == ["2026/2027"], f"Expected ['2026/2027'], got {ay}"

# 6. Class Promotion Suggested Mappings
res = requests.get(f"{BASE_URL}/class-promotions/suggested-mappings", headers=headers)
assert res.status_code == 200, f"Class promotion suggested mappings failed: {res.text}"
ay = res.json().get("academic_years", [])
src_yr = res.json().get("source_academic_year")
tgt_yr = res.json().get("target_academic_year")
print(f"GET /class-promotions/suggested-mappings -> academic_years: {ay}, source: {src_yr}, target: {tgt_yr}")
assert ay == ["2026/2027"], f"Expected ['2026/2027'], got {ay}"
assert src_yr == "2026/2027" and tgt_yr == "2026/2027", f"Expected 2026/2027, got {src_yr}, {tgt_yr}"

# 7. Student Login & Academic Years
login_std = requests.post(f"{BASE_URL}/auth/login", json={"identifier": "std_farhan", "password": "Student@Hawlwadaag2026"})
assert login_std.status_code == 200, f"Student login failed: {login_std.text}"
std_token = login_std.json()["access_token"]
std_headers = {"Authorization": f"Bearer {std_token}"}
res = requests.get(f"{BASE_URL}/student-portal/academic-years", headers=std_headers)
if res.status_code == 404:
    res = requests.get(f"{BASE_URL}/student/portal/academic-years", headers=std_headers)
print(f"GET Student Portal academic-years -> {res.json()}")
assert res.json() == ["2026/2027"], f"Expected ['2026/2027'], got {res.json()}"
res_dash = requests.get(f"{BASE_URL}/student-portal/dashboard", headers=std_headers)
print("Student Portal Dashboard status:", res_dash.status_code)
assert res_dash.status_code == 200

# 8. Teacher Login & Academic Years
login_tch = requests.post(f"{BASE_URL}/auth/login", json={"identifier": "teacher_math", "password": "Teacher@Hawlwadaag2026"})
assert login_tch.status_code == 200, f"Teacher login failed: {login_tch.text}"
tch_token = login_tch.json()["access_token"]
tch_headers = {"Authorization": f"Bearer {tch_token}"}
res = requests.get(f"{BASE_URL}/teacher-portal/exam-options", headers=tch_headers)
print(f"GET Teacher Portal exam-options -> academic_years: {res.json().get('academic_years')}")
assert res.json().get("academic_years") == ["2026/2027"]

print("\n==================== VERIFICATION SUMMARY ====================")
print("SUCCESS: 100% of all checks passed!")
print("- Database: ONLY '2026/2027' across every table and record.")
print("- All dropdowns, filters, selection lists, and APIs return ONLY '2026/2027'.")
print("- All roles (Admin, Teacher, Student) unified under '2026/2027'.")
