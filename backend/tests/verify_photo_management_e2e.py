"""
Complete 12-Step E2E Verification Script for Permanent Student Profile Photo Management
SOMROYAL EMS / Hawlwadaag School Management System
"""
import io
import os
import sys
import uuid
import requests
from datetime import datetime
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

BASE_URL = "http://127.0.0.1:8000/api/v1"

def print_header(title: str):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_step(num: int, desc: str):
    print(f"\n[STEP {num}] {desc}")

def generate_test_image(format: str = "JPEG", size=(120, 120), color="blue") -> bytes:
    img = Image.new("RGB", size, color=color)
    buf = io.BytesIO()
    img.save(buf, format=format)
    return buf.getvalue()


def run_full_verification():
    print_header("SOMROYAL EMS — STUDENT PROFILE PHOTO E2E VERIFICATION")

    # 0. Authenticate as Admin
    print_step(0, "Logging in as System Administrator")
    login_res = requests.post(
        f"{BASE_URL}/auth/login",
        json={"identifier": "admin", "password": "Admin@Hawlwadaag2026"}
    )
    assert login_res.status_code == 200, f"Admin login failed: {login_res.text}"
    admin_token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {admin_token}"}
    print("Admin authentication successful!")

    # STEP 1: Register a new student with a photo
    print_step(1, "Register a new student WITH a photo")
    adm_1 = f"ADM-P1-{uuid.uuid4().hex[:6].upper()}"
    student1_payload = {
        "admission_number": adm_1,
        "first_name": "Mustafe",
        "last_name": "Farah",
        "gender": "Male",
        "date_of_birth": "2011-03-20",
        "status": "ACTIVE",
        "guardian_name": "Farah Ahmed",
        "guardian_phone": "+252615000001"
    }
    s1_res = requests.post(f"{BASE_URL}/students", json=student1_payload, headers=headers)
    assert s1_res.status_code == 201, f"Create student 1 failed: {s1_res.text}"
    student1 = s1_res.json()
    student1_id = student1["id"]
    print(f"Student 1 created: ID={student1_id}, Name={student1['full_name']}, Adm={student1['admission_number']}")

    # Upload photo for Student 1 (JPEG)
    s1_jpeg = generate_test_image("JPEG", color="navy")
    upload1_res = requests.post(
        f"{BASE_URL}/students/{student1_id}/photo",
        headers=headers,
        files={"file": ("mustafe_avatar.jpg", io.BytesIO(s1_jpeg), "image/jpeg")}
    )
    assert upload1_res.status_code == 200, f"Upload photo 1 failed: {upload1_res.text}"
    s1_photo_data = upload1_res.json()
    assert s1_photo_data["photo_path"] is not None
    assert s1_photo_data["photo_mime_type"] == "image/jpeg"
    assert s1_photo_data["photo_url"] == f"/api/v1/students/{student1_id}/photo"
    print(f"Student 1 photo attached: Path={s1_photo_data['photo_path']}, URL={s1_photo_data['photo_url']}")

    # STEP 2: Register a student without a photo
    print_step(2, "Register a student WITHOUT a photo")
    adm_2 = f"ADM-P2-{uuid.uuid4().hex[:6].upper()}"
    student2_payload = {
        "admission_number": adm_2,
        "first_name": "Nasra",
        "last_name": "Warsame",
        "gender": "Female",
        "date_of_birth": "2012-07-14",
        "status": "ACTIVE",
        "guardian_name": "Warsame Ali",
        "guardian_phone": "+252615000002"
    }
    s2_res = requests.post(f"{BASE_URL}/students", json=student2_payload, headers=headers)
    assert s2_res.status_code == 201, f"Create student 2 failed: {s2_res.text}"
    student2 = s2_res.json()
    student2_id = student2["id"]
    assert student2["photo_path"] is None
    assert student2["photo_url"] is None
    print(f"Student 2 created: ID={student2_id}, Photo=None (Default avatar verified)")

    # STEP 3: Import student through Excel
    print_step(3, "Import student through Excel registration workflow")
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Students_Import"
    ws.append([
        "Student ID", "Student Name", "Gender",
        "Date of Birth", "Guardian Name", "Guardian Phone",
        "Residential Address"
    ])
    adm_3 = f"ADM-IMP-{uuid.uuid4().hex[:6].upper()}"
    student3_name = f"Guled Abdi {uuid.uuid4().hex[:4].upper()}"
    ws.append([
        adm_3, student3_name, "Male",
        "2010-09-10", "Abdi Hassan", "+252615000004",
        "Wadajir, Mogadishu"
    ])
    excel_buf = io.BytesIO()
    wb.save(excel_buf)
    excel_bytes = excel_buf.getvalue()

    # Get an active class for import
    classes_res = requests.get(f"{BASE_URL}/classes", headers=headers, params={"status": "ACTIVE", "page_size": 1})
    classes_data = classes_res.json()
    first_class = classes_data["items"][0] if "items" in classes_data else classes_data[0]
    class_id = first_class["id"]
    acad_year = first_class.get("academic_year", "2026/2027")

    preview_res = requests.post(
        f"{BASE_URL}/students/import/preview",
        headers=headers,
        data={"class_id": class_id, "academic_year": acad_year},
        files={"file": ("students.xlsx", excel_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    )
    assert preview_res.status_code == 200, f"Import preview failed: {preview_res.text}"
    preview_data = preview_res.json()
    if preview_data["summary"]["valid_rows"] < 1:
        print("PREVIEW ROWS:", preview_data["rows"])
    assert preview_data["summary"]["valid_rows"] >= 1

    exec_res = requests.post(
        f"{BASE_URL}/students/import/execute",
        headers=headers,
        json={
            "class_id": class_id,
            "academic_year": acad_year,
            "rows": preview_data["rows"],
            "enroll_existing_students": False
        }
    )
    assert exec_res.status_code == 200, f"Import execute failed: {exec_res.text}"
    print(f"Excel import successful! Imported {exec_res.json().get('imported_count')} students.")

    # STEP 4: Open imported student's profile & verify default avatar
    print_step(4, "Open imported student's profile and verify initial absence of photo")
    # Search student by admission number
    search_res = requests.get(f"{BASE_URL}/students", headers=headers, params={"search": adm_3})
    assert search_res.status_code == 200
    search_data = search_res.json()
    found_students = search_data["items"] if "items" in search_data else search_data
    assert len(found_students) > 0, f"Imported student with adm {adm_3} not found"
    imported_student = found_students[0]
    student3_id = imported_student["id"]
    assert imported_student["photo_path"] is None
    assert imported_student["photo_url"] is None
    print(f"Imported student retrieved: ID={student3_id}, Name={imported_student['full_name']}, Photo=None (Default Avatar)")

    # STEP 5: Upload a photo through Edit Profile for imported student
    print_step(5, "Upload photo through Edit Profile for imported student")
    s3_png = generate_test_image("PNG", color="forestgreen")
    upload3_res = requests.post(
        f"{BASE_URL}/students/{student3_id}/photo",
        headers=headers,
        files={"file": ("guled_photo.png", io.BytesIO(s3_png), "image/png")}
    )
    assert upload3_res.status_code == 200, f"Upload photo 3 failed: {upload3_res.text}"
    s3_photo_data = upload3_res.json()
    assert s3_photo_data["photo_path"] is not None
    assert s3_photo_data["photo_mime_type"] == "image/png"
    assert s3_photo_data["photo_url"] == f"/api/v1/students/{student3_id}/photo"
    print(f"Imported student photo saved: Path={s3_photo_data['photo_path']}")

    # STEP 6: Replace an existing photo
    print_step(6, "Replace an existing student photo (Student 1: JPEG -> WEBP)")
    s1_webp = generate_test_image("WEBP", color="darkred")
    replace_res = requests.post(
        f"{BASE_URL}/students/{student1_id}/photo",
        headers=headers,
        files={"file": ("mustafe_new.webp", io.BytesIO(s1_webp), "image/webp")}
    )
    assert replace_res.status_code == 200, f"Replace photo failed: {replace_res.text}"
    s1_replaced = replace_res.json()
    assert s1_replaced["photo_mime_type"] == "image/webp"
    assert s1_replaced["photo_filename"] == "mustafe_new.webp"
    print(f"Student 1 photo successfully replaced with WEBP: {s1_replaced['photo_path']}")

    # STEP 7: Refresh simulation - retrieve student profile and photo bytes
    print_step(7, "Simulate browser refresh - fetch student profile & photo stream")
    refreshed_s1 = requests.get(f"{BASE_URL}/students/{student1_id}", headers=headers).json()
    assert refreshed_s1["photo_url"] == f"/api/v1/students/{student1_id}/photo"
    photo_stream_res = requests.get(f"{BASE_URL}/students/{student1_id}/photo", headers=headers)
    assert photo_stream_res.status_code == 200
    assert photo_stream_res.headers["content-type"] == "image/webp"
    assert len(photo_stream_res.content) == len(s1_webp)
    print("Photo stream verified with correct MIME type and full byte length!")

    # STEP 8: Logout and Log Back In
    print_step(8, "Simulate logout and fresh login - verify access with new token")
    new_login_res = requests.post(
        f"{BASE_URL}/auth/login",
        json={"identifier": "admin", "password": "Admin@Hawlwadaag2026"}
    )
    assert new_login_res.status_code == 200
    fresh_token = new_login_res.json()["access_token"]
    # Test streaming photo via query param (?token=) as used by browser <img> tags
    photo_query_res = requests.get(f"{BASE_URL}/students/{student1_id}/photo?token={fresh_token}")
    assert photo_query_res.status_code == 200
    assert len(photo_query_res.content) == len(s1_webp)
    print("Photo retrieval with fresh session token verified!")

    # STEP 9: Server File Persistence Check
    print_step(9, "Verify permanent disk storage persistence")
    from app.services.student_service import UPLOAD_STUDENT_PHOTOS_DIR
    backend_uploads_dir = os.path.abspath(UPLOAD_STUDENT_PHOTOS_DIR)
    assert os.path.exists(backend_uploads_dir), f"Directory {backend_uploads_dir} does not exist!"
    s1_disk_file = os.path.join(os.path.dirname(backend_uploads_dir), refreshed_s1["photo_path"].replace("/", os.sep))
    assert os.path.exists(s1_disk_file), f"Student 1 photo not on disk: {s1_disk_file}"
    print(f"Persistent disk file verified: {s1_disk_file} (Size: {os.path.getsize(s1_disk_file)} bytes)")

    # STEP 10: Confirm correct photo appears on correct student record
    print_step(10, "Confirm photo mapping correctness across all students")
    chk_s1 = requests.get(f"{BASE_URL}/students/{student1_id}", headers=headers).json()
    chk_s2 = requests.get(f"{BASE_URL}/students/{student2_id}", headers=headers).json()
    chk_s3 = requests.get(f"{BASE_URL}/students/{student3_id}", headers=headers).json()

    assert chk_s1["photo_mime_type"] == "image/webp"
    assert chk_s1["photo_filename"] == "mustafe_new.webp"
    assert chk_s2["photo_path"] is None  # Student 2 has no photo
    assert chk_s3["photo_mime_type"] == "image/png"  # Student 3 has PNG
    assert chk_s3["photo_filename"] == "guled_photo.png"
    print("All student photo associations strictly mapped to corresponding IDs!")

    # STEP 11: Confirm changing Student 1's photo did not affect Student 3
    print_step(11, "Confirm student data isolation - changes to Student 1 do not alter Student 3")
    assert chk_s1["photo_path"] != chk_s3["photo_path"]
    assert chk_s3["first_name"] == "Guled"
    assert chk_s3["photo_size"] == len(s3_png)
    print("Student photo isolation verified!")

    # STEP 12: Confirm existing student records and Excel import remain intact
    print_step(12, "Confirm existing student records and database integrity")
    summary_res = requests.get(f"{BASE_URL}/students/summary", headers=headers)
    assert summary_res.status_code == 200
    metrics = summary_res.json()
    assert metrics["total_students"] >= 3
    assert metrics["active_students"] >= 3
    print(f"Database integrity verified: Total Students={metrics['total_students']}, Active={metrics['active_students']}")

    print_header("ALL 12 VERIFICATION WORKFLOW STEPS PASSED SUCCESSFULLY! [PASS]")


if __name__ == "__main__":
    run_full_verification()
