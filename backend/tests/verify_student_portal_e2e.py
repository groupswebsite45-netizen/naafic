import requests
import sys

BASE_URL = "http://127.0.0.1:8000/api/v1"

def print_step(title):
    print(f"\n{'='*70}\n[TEST STEP] {title}\n{'='*70}")

def run_tests():
    # 1. Admin Login
    print_step("1. Authenticating as Admin")
    admin_login_res = requests.post(f"{BASE_URL}/auth/login", json={
        "identifier": "admin",
        "password": "Admin@Hawlwadaag2026"
    })
    assert admin_login_res.status_code == 200, f"Admin login failed: {admin_login_res.text}"
    admin_token = admin_login_res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("Admin login SUCCESS")

    # 2. Find or pick two students
    print_step("2. Locating two test students in database")
    students_res = requests.get(f"{BASE_URL}/students?limit=20", headers=admin_headers)
    assert students_res.status_code == 200, f"Failed to list students: {students_res.text}"
    students = students_res.json()
    assert len(students) >= 2, f"Expected at least 2 students, got {len(students)}"

    # Let's locate Suleiman and Rahma or two distinct students
    student_a = next((s for s in students if "suleiman" in (s.get("first_name") or "").lower() or "19" in s.get("admission_number", "")), students[0])
    student_b = next((s for s in students if s["id"] != student_a["id"]), students[1])

    print(f"Student A: ID={student_a['id']}, Name={student_a.get('first_name')} {student_a.get('last_name')}, Adm={student_a.get('admission_number')}")
    print(f"Student B: ID={student_b['id']}, Name={student_b.get('first_name')} {student_b.get('last_name')}, Adm={student_b.get('admission_number')}")

    # 3. Test Auto-suggest Portal Username endpoint
    print_step("3. Testing GET /{student_id}/account/suggest-username")
    sugg_res_a = requests.get(f"{BASE_URL}/students/{student_a['id']}/account/suggest-username", headers=admin_headers)
    assert sugg_res_a.status_code == 200, f"Suggest username failed: {sugg_res_a.text}"
    suggested_uname_a = sugg_res_a.json()["suggested_username"]
    print(f"Suggested username for Student A: {suggested_uname_a} (length={len(suggested_uname_a)})")
    assert len(suggested_uname_a) >= 3, f"Suggested username too short: {suggested_uname_a}"

    sugg_res_b = requests.get(f"{BASE_URL}/students/{student_b['id']}/account/suggest-username", headers=admin_headers)
    assert sugg_res_b.status_code == 200, f"Suggest username failed: {sugg_res_b.text}"
    suggested_uname_b = sugg_res_b.json()["suggested_username"]
    print(f"Suggested username for Student B: {suggested_uname_b} (length={len(suggested_uname_b)})")
    assert len(suggested_uname_b) >= 3, f"Suggested username too short: {suggested_uname_b}"

    # 4. Test Invalid Username Validations (< 3 characters and invalid chars)
    print_step("4. Testing invalid username rejections (e.g. '20', spaces, <3 chars)")
    # Raw 20 check on auth login
    invalid_login = requests.post(f"{BASE_URL}/auth/login", json={"identifier": "20", "password": "AnyPassword123"})
    assert invalid_login.status_code == 422, f"Expected 422 for 2-char login, got {invalid_login.status_code}"
    print("Login rejected 2-char username '20' with 422 Unprocessable Entity (min_length=3 enforced)")

    # 5. Activate Portal Account for Student A
    print_step("5. Activating Portal Account for Student A")
    # If student already has account, let's update password and username to ensure predictable testing
    profile_a = requests.get(f"{BASE_URL}/students/{student_a['id']}/profile", headers=admin_headers).json()
    username_a = f"suleiman19"
    pwd_a = "Student@Hawlwadaag2026"

    if not profile_a.get("has_portal_access"):
        act_res = requests.post(
            f"{BASE_URL}/students/{student_a['id']}/account",
            json={"username": username_a, "password": pwd_a},
            headers=admin_headers
        )
        assert act_res.status_code in (200, 201), f"Account creation failed: {act_res.text}"
        print(f"Portal account created for Student A: {act_res.json()}")
    else:
        # Reset username and password
        requests.patch(f"{BASE_URL}/students/{student_a['id']}/account/username", json={"username": username_a}, headers=admin_headers)
        requests.post(f"{BASE_URL}/students/{student_a['id']}/account/reset-password", json={"password": pwd_a}, headers=admin_headers)
        requests.patch(f"{BASE_URL}/students/{student_a['id']}/account/status", json={"is_active": True}, headers=admin_headers)
        print(f"Portal account for Student A updated to username={username_a}")

    # 6. Activate Portal Account for Student B
    print_step("6. Activating Portal Account for Student B")
    profile_b = requests.get(f"{BASE_URL}/students/{student_b['id']}/profile", headers=admin_headers).json()
    username_b = f"rahma20"
    pwd_b = "Student@Hawlwadaag2026"

    if not profile_b.get("has_portal_access"):
        act_res_b = requests.post(
            f"{BASE_URL}/students/{student_b['id']}/account",
            json={"username": username_b, "password": pwd_b},
            headers=admin_headers
        )
        assert act_res_b.status_code in (200, 201), f"Account creation failed: {act_res_b.text}"
        print(f"Portal account created for Student B: {act_res_b.json()}")
    else:
        requests.patch(f"{BASE_URL}/students/{student_b['id']}/account/username", json={"username": username_b}, headers=admin_headers)
        requests.post(f"{BASE_URL}/students/{student_b['id']}/account/reset-password", json={"password": pwd_b}, headers=admin_headers)
        requests.patch(f"{BASE_URL}/students/{student_b['id']}/account/status", json={"is_active": True}, headers=admin_headers)
        print(f"Portal account for Student B updated to username={username_b}")

    # 7. Test Duplicate Username rejection (409)
    print_step("7. Testing Duplicate Username rejection (attempting to set Student B's username to Student A's username)")
    dup_res = requests.patch(
        f"{BASE_URL}/students/{student_b['id']}/account/username",
        json={"username": username_a},
        headers=admin_headers
    )
    assert dup_res.status_code == 409, f"Expected 409 conflict for duplicate username, got {dup_res.status_code}: {dup_res.text}"
    print(f"Duplicate username correctly rejected with 409: {dup_res.json()}")

    # 8. Test Student A Login
    print_step("8. Testing Student A Login (username=suleiman19)")
    login_a_res = requests.post(f"{BASE_URL}/auth/login", json={
        "identifier": username_a,
        "password": pwd_a
    })
    assert login_a_res.status_code == 200, f"Student A login failed: {login_a_res.text}"
    token_a = login_a_res.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}
    print(f"Student A Login Successful! Role: {login_a_res.json().get('role')}")

    # 9. Verify Student A Portal Endpoints and Identity
    print_step("9. Verifying Student A Portal Endpoints & Data Ownership")
    me_a = requests.get(f"{BASE_URL}/auth/me", headers=headers_a).json()
    u_data_a = me_a.get("user", {})
    print(f"Auth /me: User ID={u_data_a.get('id')}, Username={u_data_a.get('username')}, Roles={u_data_a.get('roles')}")

    profile_portal_a = requests.get(f"{BASE_URL}/student-portal/profile", headers=headers_a)
    assert profile_portal_a.status_code == 200, f"Student A profile failed: {profile_portal_a.text}"
    pdata_a = profile_portal_a.json()
    print(f"Student Portal Profile: ID={pdata_a['id']}, Name={pdata_a.get('first_name')} {pdata_a.get('last_name')}, Adm={pdata_a.get('admission_number')}")
    assert pdata_a['id'] == student_a['id'], f"Student A profile ID mismatch! Expected {student_a['id']}, got {pdata_a['id']}"

    dash_a = requests.get(f"{BASE_URL}/student-portal/dashboard", headers=headers_a)
    assert dash_a.status_code == 200, f"Student A dashboard failed: {dash_a.text}"
    print("Student A Dashboard loaded successfully.")

    fees_a = requests.get(f"{BASE_URL}/student-portal/fees", headers=headers_a)
    assert fees_a.status_code == 200, f"Student A fees failed: {fees_a.text}"

    att_a = requests.get(f"{BASE_URL}/student-portal/attendance", headers=headers_a)
    assert att_a.status_code == 200, f"Student A attendance failed: {att_a.text}"

    exams_a = requests.get(f"{BASE_URL}/student-portal/exams", headers=headers_a)
    assert exams_a.status_code == 200, f"Student A exams failed: {exams_a.text}"

    res_a = requests.get(f"{BASE_URL}/student-portal/results", headers=headers_a)
    assert res_a.status_code == 200, f"Student A results failed: {res_a.text}"

    tt_a = requests.get(f"{BASE_URL}/student-portal/timetable", headers=headers_a)
    assert tt_a.status_code == 200, f"Student A timetable failed: {tt_a.text}"

    subj_a = requests.get(f"{BASE_URL}/student-portal/subjects", headers=headers_a)
    assert subj_a.status_code == 200, f"Student A subjects failed: {subj_a.text}"

    # 10. Test Student B Login and Isolation
    print_step("10. Testing Student B Login & IDOR Isolation")
    login_b_res = requests.post(f"{BASE_URL}/auth/login", json={
        "identifier": username_b,
        "password": pwd_b
    })
    assert login_b_res.status_code == 200, f"Student B login failed: {login_b_res.text}"
    token_b = login_b_res.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}
    print(f"Student B Login Successful! Role: {login_b_res.json().get('role')}")

    profile_portal_b = requests.get(f"{BASE_URL}/student-portal/profile", headers=headers_b)
    assert profile_portal_b.status_code == 200, f"Student B profile failed: {profile_portal_b.text}"
    pdata_b = profile_portal_b.json()
    print(f"Student Portal Profile B: ID={pdata_b['id']}, Name={pdata_b.get('first_name')} {pdata_b.get('last_name')}, Adm={pdata_b.get('admission_number')}")
    assert pdata_b['id'] == student_b['id'], f"Student B profile ID mismatch! Expected {student_b['id']}, got {pdata_b['id']}"
    assert pdata_b['id'] != pdata_a['id'], "Student A and Student B should NOT have the same ID!"

    # 11. Test IDOR Protection: Student cannot query admin endpoints or manipulate student_id
    print_step("11. Testing IDOR Protection & Role Authorization Guards")
    # Student attempting to access admin student list
    admin_probe = requests.get(f"{BASE_URL}/students", headers=headers_a)
    assert admin_probe.status_code == 403, f"Expected 403 for student accessing /students, got {admin_probe.status_code}"
    print("Student accessing /students: 403 Forbidden (PROTECTED)")

    # Student attempting to query another student's record /students/{student_b['id']}
    student_probe = requests.get(f"{BASE_URL}/students/{student_b['id']}", headers=headers_a)
    assert student_probe.status_code == 403, f"Expected 403 for student querying another student, got {student_probe.status_code}"
    print(f"Student A querying /students/{student_b['id']}: 403 Forbidden (IDOR PROTECTED)")

    # Student querying another student's full profile
    profile_probe = requests.get(f"{BASE_URL}/students/{student_b['id']}/profile", headers=headers_a)
    assert profile_probe.status_code == 403, f"Expected 403 for student querying another profile, got {profile_probe.status_code}"
    print(f"Student A querying /students/{student_b['id']}/profile: 403 Forbidden (IDOR PROTECTED)")

    # Student querying their own record /students/{student_a['id']}
    own_probe = requests.get(f"{BASE_URL}/students/{student_a['id']}", headers=headers_a)
    assert own_probe.status_code == 200, f"Expected 200 for student querying own record, got {own_probe.status_code}"
    print(f"Student A querying own /students/{student_a['id']}: 200 OK")

    # 12. Test Disable Portal Access & Re-enable
    print_step("12. Testing Admin Disable Portal Access")
    dis_res = requests.patch(
        f"{BASE_URL}/students/{student_a['id']}/account/status",
        json={"is_active": False},
        headers=admin_headers
    )
    assert dis_res.status_code == 200, f"Disable failed: {dis_res.text}"
    print("Portal disabled by Admin.")

    # Login should now fail because account is inactive
    login_disabled = requests.post(f"{BASE_URL}/auth/login", json={
        "identifier": username_a,
        "password": pwd_a
    })
    assert login_disabled.status_code in (400, 401, 403), f"Expected login rejection for disabled account, got {login_disabled.status_code}"
    print(f"Disabled account login correctly rejected with {login_disabled.status_code}: {login_disabled.text}")

    # Re-enable
    en_res = requests.patch(
        f"{BASE_URL}/students/{student_a['id']}/account/status",
        json={"is_active": True},
        headers=admin_headers
    )
    assert en_res.status_code == 200, f"Re-enable failed: {en_res.text}"
    login_re = requests.post(f"{BASE_URL}/auth/login", json={
        "identifier": username_a,
        "password": pwd_a
    })
    assert login_re.status_code == 200, "Login failed after re-enabling portal!"
    print("Portal re-enabled and student login succeeds.")

    # 13. Test Reset Password
    print_step("13. Testing Password Reset")
    new_pwd = "NewSecureStudentPass2026!"
    rst_res = requests.post(
        f"{BASE_URL}/students/{student_a['id']}/account/reset-password",
        json={"password": new_pwd},
        headers=admin_headers
    )
    assert rst_res.status_code == 200, f"Reset password failed: {rst_res.text}"
    # Old password should fail
    fail_login = requests.post(f"{BASE_URL}/auth/login", json={"identifier": username_a, "password": pwd_a})
    assert fail_login.status_code in (400, 401), f"Old password should fail, got {fail_login.status_code}"
    # New password should succeed
    succ_login = requests.post(f"{BASE_URL}/auth/login", json={"identifier": username_a, "password": new_pwd})
    assert succ_login.status_code == 200, f"New password login failed: {succ_login.text}"
    print("Password reset verified: Old password rejected, new password authenticated.")

    # Restore default test password
    requests.post(
        f"{BASE_URL}/students/{student_a['id']}/account/reset-password",
        json={"password": pwd_a},
        headers=admin_headers
    )

    # 14. Verify Admin & Teacher Logins are not broken
    print_step("14. Verifying Admin and Teacher Logins remain fully operational")
    admin_test = requests.post(f"{BASE_URL}/auth/login", json={"identifier": "admin", "password": "Admin@Hawlwadaag2026"})
    assert admin_test.status_code == 200, "Admin login failed!"
    print("Admin login: PASS")

    teacher_test = requests.post(f"{BASE_URL}/auth/login", json={"identifier": "teacher.fadumo", "password": "Teacher@Hawlwadaag2026"})
    if teacher_test.status_code == 200:
        print("Teacher login (teacher.fadumo): PASS")
    else:
        print(f"Teacher login returned {teacher_test.status_code}: {teacher_test.text}")

    print_step("ALL STUDENT PORTAL TESTS PASSED SUCCESSFULLY! [PASS]")

if __name__ == "__main__":
    try:
        run_tests()
    except Exception as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
