import requests
import openpyxl
import io
import uuid

BASE_URL = "http://127.0.0.1:8000/api/v1"

# 1. Login as Admin
login_res = requests.post(f"{BASE_URL}/auth/login", json={"identifier": "admin", "password": "Admin@Hawlwadaag2026"})
print(f"Login Status: {login_res.status_code}")
assert login_res.status_code == 200, f"Login failed: {login_res.text}"
token = login_res.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. Get active Primary classes
classes_res = requests.get(f"{BASE_URL}/classes?division=PRIMARY&academic_year=2026%2F2027&status=ACTIVE", headers=headers)
print(f"Get Classes Status: {classes_res.status_code}")
classes_data = classes_res.json()
classes = classes_data if isinstance(classes_data, list) else classes_data.get("items", [])
assert len(classes) > 0, "No active primary classes found"
target_class = classes[0]
print(f"Target Class: {target_class['name']} (ID: {target_class['id']})")

# 3. Test Template Download
tmpl_res = requests.get(f"{BASE_URL}/admin/students/import/template", headers=headers)
print(f"Template Download Status: {tmpl_res.status_code} ({len(tmpl_res.content)} bytes)")
assert tmpl_res.status_code == 200

# 4. Generate 10 Test Students in Excel
tag = uuid.uuid4().hex[:6].upper()
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Students_Import"
headers_row = [
    "First Name *",
    "Middle Name",
    "Last Name *",
    "Gender *",
    "Date of Birth (YYYY-MM-DD)",
    "Guardian Name *",
    "Guardian Phone *",
    "Guardian Email",
    "Guardian Relationship",
    "Student Phone",
    "Residential Address",
    "Admission # (Optional)",
]
ws.append(headers_row)

for i in range(1, 11):
    ws.append([
        f"Khadar{i}",
        "Ali",
        f"Warsame{tag}",
        "Male" if i % 2 != 0 else "Female",
        "2012-05-15",
        f"Ali Warsame {tag}",
        f"061599{i:04d}",
        f"guardian{i}@{tag.lower()}.so",
        "Father",
        f"061588{i:04d}",
        "Hawlwadaag, Mogadishu",
        f"ADM-LIVE-{tag}-{i:03d}",
    ])

excel_buffer = io.BytesIO()
wb.save(excel_buffer)
excel_buffer.seek(0)
excel_bytes = excel_buffer.getvalue()

# 5. POST Preview on /admin/students/import/preview
files = {
    "file": (f"students_{tag}.xlsx", excel_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
}
data = {
    "class_id": str(target_class["id"]),
    "academic_year": "2026/2027",
    "academic_year_id": "2026/2027",
}

print(f"\n--- Testing POST {BASE_URL}/admin/students/import/preview ---")
prev_res = requests.post(
    f"{BASE_URL}/admin/students/import/preview",
    headers=headers,
    files=files,
    data=data,
)
print(f"Preview Status: {prev_res.status_code}")
print(f"Preview Response Body: {prev_res.text[:400]}")
assert prev_res.status_code == 200, f"Preview failed: {prev_res.text}"
prev_json = prev_res.json()
print(f"Preview Summary: total_rows={prev_json['total_rows']}, valid_rows={prev_json['valid_rows']}, errors={prev_json['error_rows']}")
assert prev_json["valid_rows"] == 10

# 6. POST Execute on /admin/students/import/execute
exec_payload = {
    "class_id": target_class["id"],
    "academic_year": "2026/2027",
    "file_name": f"students_{tag}.xlsx",
    "rows": prev_json["rows"],
    "enroll_existing_students": False,
}
print(f"\n--- Testing POST {BASE_URL}/admin/students/import/execute ---")
exec_res = requests.post(
    f"{BASE_URL}/admin/students/import/execute",
    headers=headers,
    json=exec_payload,
)
print(f"Execute Status: {exec_res.status_code}")
print(f"Execute Response Body: {exec_res.text}")
assert exec_res.status_code == 200
exec_json = exec_res.json()
assert exec_json["imported_count"] == 10

# 7. Check Fees endpoint sees the newly enrolled students
print(f"\n--- Testing Fees integration for Class ID {target_class['id']} ---")
fees_res = requests.get(
    f"{BASE_URL}/fees/classes/{target_class['id']}/students?academic_year=2026%2F2027",
    headers=headers,
)
print(f"Fees Class Students Status: {fees_res.status_code}")
fees_json = fees_res.json()
print(f"Total Enrolled Students in Fees for {target_class['name']}: {fees_json['total_students']}")
assert fees_json["total_students"] >= 10

# 8. Re-upload duplicate file
excel_buffer.seek(0)
files_dup = {
    "file": (f"students_{tag}.xlsx", excel_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
}
prev_dup_res = requests.post(
    f"{BASE_URL}/admin/students/import/preview",
    headers=headers,
    files=files_dup,
    data=data,
)
print(f"\nDuplicate Preview Status: {prev_dup_res.status_code}")
prev_dup_json = prev_dup_res.json()
print(f"Duplicate Preview Rows: valid={prev_dup_json['valid_rows']}, already_exists={prev_dup_json['already_exists_rows']}")
assert prev_dup_json["already_exists_rows"] == 10
assert prev_dup_json["valid_rows"] == 0

print("\n>>> ALL LIVE HTTP CHECKS PASSED 100% SUCCESSFULLY! <<<")
