"""
Database Reset Script — Hawlwadaag School Management System

Cleans all registered operational records (Classes, Students, Teachers, Subjects,
Attendance, Fees, Invoices, Exams, Results, Timetables, Enrollments, Import Logs, Portal Accounts)
while preserving the primary System Administrator, Core Roles, and System Settings
so you can start registering everything completely fresh.
"""
import sys
import os
from sqlalchemy import text

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal, engine, Base
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.role import Role
from app.models.user import User
from app.models.user_role import UserRole
from app.models.system_setting import SystemSetting

def clear_all_data():
    print("=" * 70)
    print("STARTING FRESH DATABASE RESET")
    print("=" * 70)

    db = SessionLocal()
    try:
        # 1. Disable triggers / foreign keys or delete in reverse-dependency order with CASCADE
        tables_to_truncate = [
            "student_result_views",
            "result_submissions",
            "exam_results",
            "exams",
            "attendances",
            "fee_payments",
            "student_fees",
            "fee_structures",
            "timetables",
            "teacher_assignments",
            "student_import_logs",
            "student_enrollments",
            "students",
            "teachers",
            "subjects",
            "classes",
            "notifications",
            "audit_logs",
            "sessions",
        ]

        print("\n1. Truncating operational tables and resetting auto-increment sequences...")
        for tbl in tables_to_truncate:
            try:
                db.execute(text(f"TRUNCATE TABLE {tbl} RESTART IDENTITY CASCADE;"))
                print(f"   [CLEARED] {tbl}")
            except Exception as e:
                db.rollback()
                # Table might not exist or slightly different name, let's try DELETE
                try:
                    db.execute(text(f"DELETE FROM {tbl};"))
                    print(f"   [DELETED] {tbl}")
                except Exception as inner_e:
                    print(f"   [SKIP] Table {tbl} not present or: {inner_e}")
                db.commit()

        db.commit()

        # 2. Clean up non-admin users from users and user_roles
        print("\n2. Cleaning up non-admin user accounts...")
        admin_username = settings.INITIAL_ADMIN_USERNAME.lower().strip()
        admin_email = settings.INITIAL_ADMIN_EMAIL.lower().strip()

        admin_user = db.query(User).filter(
            (User.username == admin_username) | (User.email == admin_email)
        ).first()

        admin_id = admin_user.id if admin_user else None

        if admin_id:
            db.execute(text("DELETE FROM user_roles WHERE user_id != :admin_id"), {"admin_id": admin_id})
            db.execute(text("DELETE FROM users WHERE id != :admin_id"), {"admin_id": admin_id})
        else:
            db.execute(text("DELETE FROM user_roles"))
            db.execute(text("DELETE FROM users"))

        db.commit()
        print("   [CLEARED] All student, teacher, and temporary user portal accounts.")

        # 3. Ensure core Roles exist
        print("\n3. Verifying System Roles...")
        roles_data = [
            ("ADMIN", "System and school administrator with full management access", True),
            ("TEACHER", "Academic faculty member managing attendance, schedule and grades", True),
            ("STUDENT", "Enrolled student accessing timetable, fees, and exam results", True),
            ("PARENT", "Parent or legal guardian monitoring student progress", True),
            ("STAFF", "Administrative and supporting school staff", True),
        ]
        created_roles = {}
        for r_name, r_desc, is_sys in roles_data:
            role = db.query(Role).filter(Role.name == r_name).first()
            if not role:
                role = Role(name=r_name, description=r_desc, is_system=is_sys)
                db.add(role)
                db.commit()
                db.refresh(role)
            created_roles[r_name] = role
        print("   [OK] System roles verified.")

        # 4. Ensure System Settings exist
        print("\n4. Verifying System Settings...")
        default_settings = [
            ("school_name", "Hawlwadaag Primary and Secondary School", "Official school institution name", True),
            ("school_short_name", "Hawlwadaag School", "Abbreviated school name", True),
            ("school_motto", "Excellence in Education and Character", "Official school motto", True),
            ("school_email", "info@hawlwadaagschool.edu.so", "Official contact email", True),
            ("school_phone", "+252 61 0000000", "Official contact phone number", True),
            ("school_address", "Hawlwadaag District, Mogadishu, Somalia", "Physical campus location", True),
            ("primary_color", "#1e3a8a", "Primary school theme branding color", True),
            ("secondary_color", "#0284c7", "Secondary theme branding color", True),
            ("academic_year_current", "2026/2027", "Current active academic year", True),
        ]
        for k, v, d, p in default_settings:
            s = db.query(SystemSetting).filter(SystemSetting.key == k).first()
            if not s:
                s = SystemSetting(key=k, value=v, description=d, is_public=p)
                db.add(s)
            elif k == "academic_year_current":
                s.value = "2026/2027"
        db.commit()
        print("   [OK] System settings verified.")

        # 5. Ensure Admin user exists with correct password
        print("\n5. Verifying Admin User...")
        admin = db.query(User).filter(
            (User.username == admin_username) | (User.email == admin_email)
        ).first()

        if not admin:
            admin = User(
                email=admin_email,
                username=admin_username,
                hashed_password=get_password_hash(settings.INITIAL_ADMIN_PASSWORD),
                full_name=settings.INITIAL_ADMIN_FULL_NAME,
                phone_number="+252 61 1234567",
                is_active=True,
                is_superuser=True
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
        else:
            admin.hashed_password = get_password_hash(settings.INITIAL_ADMIN_PASSWORD)
            admin.is_active = True
            admin.is_superuser = True
            db.commit()

        # Ensure Admin has ADMIN role
        admin_role = created_roles.get("ADMIN")
        if admin_role:
            ur = db.query(UserRole).filter(UserRole.user_id == admin.id, UserRole.role_id == admin_role.id).first()
            if not ur:
                ur = UserRole(user_id=admin.id, role_id=admin_role.id)
                db.add(ur)
                db.commit()

        print(f"   [OK] Admin User: {admin.username} ({admin.email})")

        print("\n" + "=" * 70)
        print("DATABASE CLEARED SUCCESSFULLY! READY FOR FRESH REGISTRATION.")
        print("=" * 70)

    finally:
        db.close()

if __name__ == "__main__":
    clear_all_data()
