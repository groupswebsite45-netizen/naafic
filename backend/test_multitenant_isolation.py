import os
import sys
import psycopg2
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.tenant_provisioner import (
    generate_tenant_database_name,
    create_tenant_database,
    provision_tenant_schema_and_admin,
    verify_tenant_provisioning,
    delete_tenant_database,
    get_tenant_db_url,
)
from app.models.institution import Institution, Subscription, InstitutionPayment
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.user import User
from app.models.system_setting import SystemSetting
from app.services.auth_service import AuthService
from app.schemas.auth import LoginRequest
from app.api.v1.routes.super_admin import build_institution_response, generate_institution_code


def run_multi_tenant_test():
    print("=" * 80)
    print("STARTING SOMROYAL EMS MULTI-TENANT ISOLATION & PROVISIONING TEST")
    print("=" * 80)

    db = SessionLocal()

    test_schools = [
        {
            "name": "Al-Huda Academy",
            "type": "Academy",
            "logo_url": "/uploads/institution_logos/logo_alhuda.png",
            "city": "Mogadishu",
            "address": "KM4, Airport Road",
            "admin_full_name": "Sheik Hassan Omar",
            "admin_username": "admin_alhuda",
            "admin_email": "admin@alhuda.edu.so",
            "admin_password": "Password123!",
        },
        {
            "name": "Waberi Secondary School",
            "type": "Secondary School",
            "logo_url": "/uploads/institution_logos/logo_waberi.png",
            "city": "Mogadishu",
            "address": "21 October Road, Waberi",
            "admin_full_name": "Fadumo Mohamed Warsame",
            "admin_username": "admin_waberi",
            "admin_email": "admin@waberi.edu.so",
            "admin_password": "Password123!",
        },
        {
            "name": "Kulan Primary School",
            "type": "Primary School",
            "logo_url": "/uploads/institution_logos/logo_kulan.png",
            "city": "Kismayo",
            "address": "Via Kismayo Main Blvd",
            "admin_full_name": "Eng. Ali Abdi Shire",
            "admin_username": "admin_kulan",
            "admin_email": "admin@kulan.edu.so",
            "admin_password": "Password123!",
        },
    ]

    provisioned_institutions = []

    try:
        # Step 1: Clean up any old test records if they exist
        print("\n--- STEP 1: Cleaning up any old test school records & databases ---")
        for sc in test_schools:
            existing = db.query(Institution).filter(Institution.name == sc["name"]).first()
            if existing:
                print(f"Found old test record '{existing.name}' ({existing.database_name}), deleting...")
                target_db = existing.database_name
                db.delete(existing)
                db.commit()
                if target_db:
                    try:
                        delete_tenant_database(target_db)
                        print(f"  Dropped database '{target_db}'")
                    except Exception as e:
                        print(f"  Note dropping '{target_db}': {e}")

        # Step 2: Provision School A, School B, and School C
        print("\n--- STEP 2: Registering & Provisioning 3 Independent Schools ---")
        for idx, sc in enumerate(test_schools, 1):
            code = generate_institution_code(db, sc["type"])
            db_name = generate_tenant_database_name(sc["name"], code)
            print(f"\n[School {chr(64 + idx)}] Provisioning '{sc['name']}'...")
            print(f"  - Unique Code: {code}")
            print(f"  - Isolated Database Name: {db_name}")
            print(f"  - Logo Asset: {sc['logo_url']}")
            print(f"  - Administrator: {sc['admin_full_name']} ({sc['admin_username']})")

            # Create Central DB Record
            inst = Institution(
                name=sc["name"],
                type=sc["type"],
                code=code,
                logo_url=sc["logo_url"],
                city=sc["city"],
                address=sc["address"],
                database_name=db_name,
                admin_username=sc["admin_username"],
                admin_email=sc["admin_email"],
                subscription_plan="Professional School",
                subscription_status="ACTIVE",
                status="ACTIVE",
                provisioning_status="PROVISIONING",
            )
            db.add(inst)
            db.commit()
            db.refresh(inst)

            # Create physical database in PostgreSQL
            created = create_tenant_database(db_name)
            assert created, f"Failed to create database {db_name}"
            print(f"  -> Physical PostgreSQL database '{db_name}' created successfully.")

            # Run schema creation and initial admin setup
            admin_dict = {
                "username": sc["admin_username"],
                "email": sc["admin_email"],
                "password": sc["admin_password"],
                "full_name": sc["admin_full_name"],
                "phone_number": "+252 61 1234567",
            }
            inst_info = {
                "name": sc["name"],
                "code": code,
                "type": sc["type"],
                "logo_url": sc["logo_url"],
                "email": sc["admin_email"],
                "phone": "+252 61 1234567",
                "city": sc["city"],
                "address": sc["address"],
            }
            res = provision_tenant_schema_and_admin(
                database_name=db_name,
                admin_data=admin_dict,
                institution_info=inst_info,
            )

            # Verification check
            v_res = verify_tenant_provisioning(db_name, sc["admin_email"])
            assert v_res["verified"], f"Verification failed for {db_name}"

            inst.admin_user_id = res["admin_user_id"]
            inst.provisioning_status = "PROVISIONED"
            db.commit()
            db.refresh(inst)

            provisioned_institutions.append({
                "inst": inst,
                "config": sc,
                "db_name": db_name,
            })
            print(f"  -> Verified complete independence: 0 students, 0 teachers, admin user ID {res['admin_user_id']}.")

        # Step 3: Test Zero Initial Records & Complete Independence
        print("\n--- STEP 3: Verifying Zero Initial Operational Records in all 3 Databases ---")
        for item in provisioned_institutions:
            t_url = get_tenant_db_url(item["db_name"])
            t_eng = create_engine(t_url, pool_pre_ping=True)
            t_sess = sessionmaker(bind=t_eng)()
            try:
                stu_c = t_sess.query(Student).count()
                tea_c = t_sess.query(Teacher).count()
                users_c = t_sess.query(User).count()
                s_name = t_sess.query(SystemSetting).filter(SystemSetting.key == "school_name").first()
                s_logo = t_sess.query(SystemSetting).filter(SystemSetting.key == "logo_url").first()

                print(f"\nChecking [{item['inst'].name}] ({item['db_name']}):")
                print(f"  Students: {stu_c} (Expected: 0)")
                print(f"  Teachers: {tea_c} (Expected: 0)")
                print(f"  Users:    {users_c} (Expected: 1 admin)")
                print(f"  Settings School Name: '{s_name.value if s_name else None}'")
                print(f"  Settings School Logo: '{s_logo.value if s_logo else None}'")

                assert stu_c == 0, f"Error: Students count is {stu_c}, expected 0"
                assert tea_c == 0, f"Error: Teachers count is {tea_c}, expected 0"
                assert users_c == 1, f"Error: Users count is {users_c}, expected 1"
                assert s_name and s_name.value == item["config"]["name"], "Error: School name mismatch"
                assert s_logo and s_logo.value == item["config"]["logo_url"], "Error: School logo mismatch"
                print("  -> PASSED: Clean zero-state verified!")
            finally:
                t_sess.close()
                t_eng.dispose()

        # Step 4: Test Multi-Tenant Authentication & Token Isolation
        print("\n--- STEP 4: Testing Multi-Tenant Authentication & Smart Discovery ---")
        for item in provisioned_institutions:
            auth_svc = AuthService(db)
            login_req = LoginRequest(
                identifier=item["config"]["admin_username"],
                password=item["config"]["admin_password"],
            )
            token_resp = auth_svc.authenticate(login_req)

            print(f"\nLogin as {item['config']['admin_username']}:")
            print(f"  Returned User:        {token_resp.user.full_name} ({token_resp.user.username})")
            print(f"  Returned Institution: {token_resp.institution.name} ({token_resp.institution.code})")
            print(f"  Returned Logo URL:    {token_resp.institution.logo_url}")
            print(f"  Target Database:      {token_resp.institution.database_name}")

            assert token_resp.user.username == item["config"]["admin_username"], "Username mismatch"
            assert token_resp.institution.name == item["config"]["name"], "Institution name mismatch"
            assert token_resp.institution.logo_url == item["config"]["logo_url"], "Institution logo mismatch"
            assert token_resp.institution.database_name == item["db_name"], "Database name mismatch"
            print("  -> PASSED: Correct tenant database, credentials & branding confirmed!")

        # Step 5: Test Data Isolation (Add records to School A only)
        print("\n--- STEP 5: Testing Cross-Tenant Data Isolation ---")
        school_a = provisioned_institutions[0]
        school_b = provisioned_institutions[1]
        school_c = provisioned_institutions[2]

        print(f"Adding 2 Students and 1 Teacher to School A ('{school_a['inst'].name}')...")
        t_url_a = get_tenant_db_url(school_a["db_name"])
        t_eng_a = create_engine(t_url_a, pool_pre_ping=True)
        t_sess_a = sessionmaker(bind=t_eng_a)()

        try:
            s1 = Student(
                admission_number="ADM-001",
                first_name="Ahmed",
                last_name="Hassan",
                gender="MALE",
                status="ACTIVE",
            )
            s2 = Student(
                admission_number="ADM-002",
                first_name="Amina",
                last_name="Ali",
                gender="FEMALE",
                status="ACTIVE",
            )
            t1 = Teacher(
                teacher_number="TCH-2026-001",
                first_name="Farhan",
                last_name="Mohamud",
                gender="Male",
                email="teacher.farhan@alhuda.edu.so",
                status="ACTIVE",
            )
            t_sess_a.add_all([s1, s2, t1])
            t_sess_a.commit()
            print("  -> Inserted records into School A database.")
        finally:
            t_sess_a.close()
            t_eng_a.dispose()

        # Now verify counts in School A, School B, and School C
        resp_a = build_institution_response(school_a["inst"])
        resp_b = build_institution_response(school_b["inst"])
        resp_c = build_institution_response(school_c["inst"])

        print(f"\nLive Counts Check:")
        print(f"  [School A: {resp_a.name}] Students = {resp_a.total_students}, Teachers = {resp_a.total_teachers}")
        print(f"  [School B: {resp_b.name}] Students = {resp_b.total_students}, Teachers = {resp_b.total_teachers}")
        print(f"  [School C: {resp_c.name}] Students = {resp_c.total_students}, Teachers = {resp_c.total_teachers}")

        assert resp_a.total_students == 2 and resp_a.total_teachers == 1, "School A should have 2 students and 1 teacher"
        assert resp_b.total_students == 0 and resp_b.total_teachers == 0, "School B must remain completely empty (0 students, 0 teachers)"
        assert resp_c.total_students == 0 and resp_c.total_teachers == 0, "School C must remain completely empty (0 students, 0 teachers)"
        print("  -> PASSED: Complete data isolation verified! No cross-tenant leakage!")

        print("\n" + "=" * 80)
        print("ALL MULTI-TENANT PROVISIONING & ISOLATION TESTS PASSED WITH 100% SUCCESS!")
        print("=" * 80)

    finally:
        db.close()


if __name__ == "__main__":
    run_multi_tenant_test()
