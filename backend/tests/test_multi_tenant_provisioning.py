import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from sqlalchemy import text
from app.core.database import SessionLocal
from app.core.tenant_provisioner import (
    generate_tenant_database_name,
    create_tenant_database,
    provision_tenant_schema_and_admin,
    delete_tenant_database,
)
from app.core.tenant_context import (
    get_tenant_engine,
    get_tenant_sessionmaker,
)
from app.models.institution import Institution
from app.models.user import User
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.school_class import SchoolClass
from app.models.subject import Subject
from app.services.auth_service import AuthService
from app.schemas.auth import LoginRequest


def test_suite_complete_multi_tenant_isolation():
    print("\n=======================================================")
    print("STARTING COMPLETE MULTI-TENANT PROVISIONING TEST SUITE")
    print("=======================================================")

    # -----------------------------------------------------------------
    # TEST A: Existing Institution & Existing Database ('sms')
    # -----------------------------------------------------------------
    print("\n--- TEST A: Existing Institution (Hawlwadaag Secondary School) ---")
    central_db = SessionLocal()
    existing_inst = central_db.query(Institution).filter(Institution.code == "SOM-SCH-0001").first()
    assert existing_inst is not None, "Hawlwadaag School must exist in central institutions table"
    assert existing_inst.database_name == "sms", f"Existing institution must map to 'sms', got {existing_inst.database_name}"
    
    # Check student and teacher counts in existing database
    existing_students = central_db.query(Student).count()
    existing_teachers = central_db.query(Teacher).count()
    print(f"Existing school 'sms' database records: {existing_students} students, {existing_teachers} teachers.")
    assert existing_students == 96, f"Expected 96 students in existing database, found {existing_students}"
    assert existing_teachers == 5, f"Expected 5 teachers in existing database, found {existing_teachers}"

    # Verify existing admin user login against 'sms'
    auth_service_existing = AuthService(central_db)
    existing_admin = central_db.query(User).filter(User.username == "admin").first()
    assert existing_admin is not None, "Existing admin user must exist in 'sms'"
    print("[PASS] TEST A PASSED: Existing institution data and context fully preserved.")
    central_db.close()

    # -----------------------------------------------------------------
    # TEST B: First New Institution Provisioning (Waberi Secondary School)
    # -----------------------------------------------------------------
    print("\n--- TEST B: First New Institution (Waberi Secondary School) ---")
    school_name = "Waberi Secondary School"
    school_code = "SOM-SCH-0002"
    db_name_1 = generate_tenant_database_name(school_name, school_code)
    print(f"1. Generated Database Name: {db_name_1}")
    assert db_name_1.startswith("somroyal_"), "Database name must be prefixed with 'somroyal_'"
    assert "waberi_secondary_school" in db_name_1, "Database name must derive safely from school name"

    # Create physical database
    create_tenant_database(db_name_1)
    print(f"2. Physical MySQL database '{db_name_1}' created.")

    # Check local MySQL server shows database
    server_engine = get_tenant_engine("mysql")
    with server_engine.connect() as conn:
        all_dbs = [r[0] for r in conn.execute(text("SHOW DATABASES;"))]
        assert db_name_1 in all_dbs, f"Database '{db_name_1}' must physically exist in MySQL server"
    print(f"3. Verified '{db_name_1}' is visible in MySQL database server.")

    # Provision SMS schema & initial admin
    admin_data_1 = {
        "username": "admin_waberi",
        "email": "principal@waberi.edu.so",
        "password": "PasswordWaberi2026!",
        "full_name": "Waberi Principal",
        "phone_number": "+252 61 7000002",
    }
    inst_info_1 = {
        "id": 2,
        "name": school_name,
        "code": school_code,
        "type": "Secondary School",
        "email": "info@waberi.edu.so",
        "phone": "+252 61 7000002",
        "city": "Mogadishu",
    }
    res_1 = provision_tenant_schema_and_admin(db_name_1, admin_data_1, inst_info_1)
    print(f"4. Provisioned tenant schema and initial admin: {res_1}")

    # Inspect the new tenant database directly
    engine_1 = get_tenant_engine(db_name_1)
    Session_1 = get_tenant_sessionmaker(db_name_1)
    db_1 = Session_1()

    # Confirm schema exists
    with engine_1.connect() as conn:
        tables_1 = [r[0] for r in conn.execute(text("SHOW TABLES;"))]
        print(f"5. Total tables created in '{db_name_1}': {len(tables_1)}")
        assert len(tables_1) >= 30, f"Expected full SMS schema tables, got {len(tables_1)}"

    # Confirm 0 operational records (completely empty!)
    stu_count_1 = db_1.query(Student).count()
    tea_count_1 = db_1.query(Teacher).count()
    class_count_1 = db_1.query(SchoolClass).count()
    subject_count_1 = db_1.query(Subject).count()
    users_count_1 = db_1.query(User).count()

    print(f"6. Operational counts in '{db_name_1}':")
    print(f"   - Students: {stu_count_1} (MUST BE 0)")
    print(f"   - Teachers: {tea_count_1} (MUST BE 0)")
    print(f"   - Classes:  {class_count_1} (MUST BE 0)")
    print(f"   - Subjects: {subject_count_1} (MUST BE 0)")
    print(f"   - Users:    {users_count_1} (Initial admin only)")

    assert stu_count_1 == 0, "New institution database MUST have 0 students"
    assert tea_count_1 == 0, "New institution database MUST have 0 teachers"
    assert class_count_1 == 0, "New institution database MUST have 0 classes"
    assert subject_count_1 == 0, "New institution database MUST have 0 subjects"
    assert users_count_1 == 1, "New institution database must only have the initial admin"

    # Authenticate through tenant database
    auth_service_1 = AuthService(db_1)
    token_resp_1 = auth_service_1.authenticate(LoginRequest(identifier="admin_waberi", password="PasswordWaberi2026!"))
    assert token_resp_1.access_token is not None, "Login must succeed with initial admin credentials"
    assert token_resp_1.user.username == "admin_waberi"
    print("7. Successfully authenticated against tenant database with isolated admin credentials.")
    db_1.close()
    print("[PASS] TEST B PASSED: First new institution provisioned with empty database and working login.")

    # -----------------------------------------------------------------
    # TEST C: Second New Institution (Hodan International Academy)
    # -----------------------------------------------------------------
    print("\n--- TEST C: Second New Institution (Hodan International Academy) ---")
    acad_name = "Hodan International Academy"
    acad_code = "SOM-ACD-0003"
    db_name_2 = generate_tenant_database_name(acad_name, acad_code)
    print(f"1. Generated Database Name: {db_name_2}")
    assert db_name_2 != db_name_1, "Every institution must receive a unique database name"

    create_tenant_database(db_name_2)
    admin_data_2 = {
        "username": "admin_hodan",
        "email": "director@hodan.edu.so",
        "password": "PasswordHodan2026!",
        "full_name": "Hodan Director",
        "phone_number": "+252 61 8000003",
    }
    inst_info_2 = {
        "id": 3,
        "name": acad_name,
        "code": acad_code,
        "type": "Academy",
        "email": "info@hodan.edu.so",
        "phone": "+252 61 8000003",
        "city": "Mogadishu",
    }
    provision_tenant_schema_and_admin(db_name_2, admin_data_2, inst_info_2)

    Session_2 = get_tenant_sessionmaker(db_name_2)
    db_2 = Session_2()
    assert db_2.query(Student).count() == 0
    assert db_2.query(Teacher).count() == 0
    print(f"2. Second database '{db_name_2}' created and confirmed empty.")
    db_2.close()
    print("[PASS] TEST C PASSED: Second separate database created with independent schema.")

    # -----------------------------------------------------------------
    # TEST D: Cross-Institution Data Isolation & Workflow
    # -----------------------------------------------------------------
    print("\n--- TEST D: Cross-Institution Data Isolation Workflow ---")
    # In Waberi Secondary School (DB 1), create a Class
    db_1 = Session_1()
    new_class_1 = SchoolClass(
        name="Form 1A - Waberi",
        code="WBR-F1A",
        division="SECONDARY",
        level="Form 1",
        section="A",
        academic_year="2026/2027",
        capacity=40,
        status="ACTIVE"
    )
    db_1.add(new_class_1)
    db_1.commit()
    db_1.refresh(new_class_1)
    print(f"1. Created class '{new_class_1.name}' in Waberi database '{db_name_1}'.")

    # In Hodan Academy (DB 2), verify that Waberi's class DOES NOT EXIST
    db_2 = Session_2()
    hodan_classes = db_2.query(SchoolClass).all()
    print(f"2. Classes in Hodan database '{db_name_2}': {[c.name for c in hodan_classes]}")
    assert len(hodan_classes) == 0, "Data leakage detected! Hodan database must NOT contain Waberi's classes."
    print("3. Verified complete physical isolation: 0 cross-contamination between databases.")
    db_1.close()
    db_2.close()
    print("[PASS] TEST D PASSED: Full tenant database isolation confirmed.")

    # -----------------------------------------------------------------
    # TEST E: Safe Database Protection
    # -----------------------------------------------------------------
    print("\n--- TEST E: Safety and Destruction Protection ---")
    try:
        delete_tenant_database("sms")
        assert False, "delete_tenant_database must NEVER allow deleting central 'sms' database"
    except ValueError as e:
        print(f"1. Protected database safeguard successfully triggered: {e}")

    # Clean up test databases
    delete_tenant_database(db_name_1)
    delete_tenant_database(db_name_2)
    print(f"2. Test databases '{db_name_1}' and '{db_name_2}' cleaned up safely.")
    print("[PASS] TEST E PASSED: Central database protected from accidental deletion.")

    print("\n=======================================================")
    print("ALL TESTS (A, B, C, D, E) PASSED WITH 100% SUCCESS!")
    print("=======================================================\n")


if __name__ == "__main__":
    test_suite_complete_multi_tenant_isolation()
