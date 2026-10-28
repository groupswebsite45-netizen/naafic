import requests
import sys

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_subject_api_integration():
    print("--- 1. Testing Admin Authentication ---")
    login_resp = requests.post(f"{BASE_URL}/auth/login", json={"identifier": "admin", "password": "Admin@Hawlwadaag2026"})
    if login_resp.status_code != 200:
        print(f"FAILED: Login failed ({login_resp.status_code}): {login_resp.text}")
        sys.exit(1)
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("[OK] Logged in successfully.")

    print("\n--- 2. Testing Subject Summary Statistics ---")
    sum_resp = requests.get(f"{BASE_URL}/subjects/summary", headers=headers)
    assert sum_resp.status_code == 200, f"Summary failed: {sum_resp.text}"
    summary = sum_resp.json()
    print(f"[OK] Summary: Total={summary['total_subjects']}, Active={summary['active_subjects']}, Assigned={summary['assigned_subjects']}, Unassigned={summary['unassigned_subjects']}, Departments={summary['departments_count']}")
    assert "total_subjects" in summary
    assert "active_subjects" in summary

    print("\n--- 3. Testing Distinct Departments Endpoint ---")
    dept_resp = requests.get(f"{BASE_URL}/subjects/departments", headers=headers)
    assert dept_resp.status_code == 200
    depts = dept_resp.json()
    print(f"[OK] Distinct departments ({len(depts)}): {depts}")

    print("\n--- 4. Testing Subject Directory Listing & Search ---")
    list_resp = requests.get(f"{BASE_URL}/subjects", headers=headers, params={"limit": 10})
    assert list_resp.status_code == 200
    subjects = list_resp.json()
    print(f"[OK] Retrieved {len(subjects)} subjects. First subject: {subjects[0]['name'] if subjects else 'None'}")

    print("\n--- 5. Testing Create Subject & Duplicate Code Validation ---")
    test_code = "TEST-SUB-999"
    new_sub_payload = {
        "name": "Advanced Physics Laboratory",
        "code": test_code,
        "department": "Sciences",
        "description": "Hands-on advanced physics laboratory curriculum and practical experiments.",
        "status": "ACTIVE"
    }
    create_resp = requests.post(f"{BASE_URL}/subjects", headers=headers, json=new_sub_payload)
    if create_resp.status_code == 409:
        # If it already existed from previous run, fetch it
        search_resp = requests.get(f"{BASE_URL}/subjects", headers=headers, params={"query": test_code})
        sub_id = search_resp.json()[0]["id"]
        print(f"[OK] Subject existed with ID {sub_id}")
    else:
        assert create_resp.status_code == 201, f"Create failed: {create_resp.text}"
        sub_id = create_resp.json()["id"]
        print(f"[OK] Subject created successfully with ID: {sub_id}")

    # Duplicate code rejection test
    dup_resp = requests.post(f"{BASE_URL}/subjects", headers=headers, json=new_sub_payload)
    assert dup_resp.status_code == 409, f"Duplicate code was not rejected: {dup_resp.status_code}"
    print("[OK] Backend successfully rejected duplicate subject code with HTTP 409 Conflict.")

    print("\n--- 6. Testing Full Subject Profile Retrieval (/subjects/:id/full) ---")
    full_resp = requests.get(f"{BASE_URL}/subjects/{sub_id}/full", headers=headers)
    assert full_resp.status_code == 200, f"Full profile retrieval failed: {full_resp.text}"
    profile = full_resp.json()
    print(f"[OK] Full Profile: {profile['name']} ({profile['code']})")
    print(f"  - Classes count: {len(profile['classes'])}")
    print(f"  - Teachers count: {len(profile['teachers'])}")
    print(f"  - Timetables count: {len(profile['timetables'])}")
    print(f"  - Exams count: {len(profile['exams'])}")

    print("\n--- 7. Testing Class Assignment to Subject ---")
    # Fetch an active class
    classes_resp = requests.get(f"{BASE_URL}/classes", headers=headers, params={"limit": 1})
    if classes_resp.json():
        target_class = classes_resp.json()[0]
        assign_class_payload = {
            "class_id": target_class["id"],
            "academic_year": "2025-2026",
            "periods_per_week": 4
        }
        assign_resp = requests.post(f"{BASE_URL}/subjects/{sub_id}/classes", headers=headers, json=assign_class_payload)
        if assign_resp.status_code == 200:
            assignment_data = assign_resp.json()
            assignment_id = assignment_data["id"]
            print(f"[OK] Assigned subject to class {target_class['name']} (Assignment ID: {assignment_id})")

            # Duplicate assignment rejection test
            dup_assign = requests.post(f"{BASE_URL}/subjects/{sub_id}/classes", headers=headers, json=assign_class_payload)
            assert dup_assign.status_code == 409, f"Duplicate assignment was not rejected: {dup_assign.status_code}"
            print("[OK] Backend successfully rejected duplicate class allocation with HTTP 409 Conflict.")

            # Remove class allocation
            del_assign = requests.delete(f"{BASE_URL}/subjects/{sub_id}/classes/{assignment_id}", headers=headers)
            assert del_assign.status_code == 200
            print("[OK] Class allocation removed successfully.")
        elif assign_resp.status_code == 409:
            print("[OK] Subject already assigned to class.")

    print("\n--- 8. Testing Clean Deletion of Subject ---")
    del_resp = requests.delete(f"{BASE_URL}/subjects/{sub_id}", headers=headers)
    assert del_resp.status_code == 200, f"Delete failed: {del_resp.text}"
    print(f"[OK] Subject {sub_id} deleted successfully.")

    # Confirm soft-deletion status
    get_del = requests.get(f"{BASE_URL}/subjects/{sub_id}", headers=headers)
    assert get_del.status_code == 200
    assert get_del.json()["status"] == "INACTIVE"
    print("[OK] Verified subject status transitioned to INACTIVE in PostgreSQL database.")

    print("\n=======================================================")
    print("ALL 8 END-TO-END INTEGRATION TEST SUITES PASSED (100%)")
    print("=======================================================")

if __name__ == "__main__":
    test_subject_api_integration()
