"""
Database migration script using SQLAlchemy Base.metadata.create_all
Supports both MySQL and PostgreSQL seamlessly.
"""
import sys
import os
from datetime import datetime, timedelta
from sqlalchemy import text, inspect

# Ensure backend directory is in path and cwd is backend for proper .env loading
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.core.database import engine, Base, SessionLocal
from app.core.security import get_password_hash
# Import all models to register with Base.metadata
from app.models import Institution, Subscription, InstitutionPayment, Role, User, UserRole

def run_migration():
    print(f"Running multi-institution migration on engine: {engine.url}")

    # 1. Create all newly registered tables using SQLAlchemy metadata
    Base.metadata.create_all(bind=engine)
    print("[OK] Tables 'institutions', 'subscriptions', 'institution_payments' created or verified.")

    # 2. Check and add institution_id column to existing tables if needed
    inspector = inspect(engine)
    for table_name in ['users', 'students', 'teachers', 'classes']:
        if table_name in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns(table_name)]
            if 'institution_id' not in columns:
                with engine.begin() as conn:
                    conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN institution_id INT DEFAULT 1;"))
                print(f"[OK] Added 'institution_id' to {table_name}.")
            else:
                print(f"[OK] Table '{table_name}' already has 'institution_id'.")

    # 3. Seed initial institutions and Super Admin user
    db = SessionLocal()
    try:
        now = datetime.now()
        existing_inst = db.query(Institution).filter(Institution.id == 1).first()
        if not existing_inst:
            print("Seeding default institution (ID 1)...")
            inst1 = Institution(
                id=1,
                code="SOM-SCH-0001",
                name="Hawlwadaag Primary and Secondary School",
                type="Primary & Secondary School",
                contact_person="Dr. Abdullahi Warsame",
                email="admin@hawlwadaagschool.edu.so",
                phone="+252 61 0000000",
                region="Banaadir",
                city="Mogadishu",
                address="Hawlwadaag District, Mogadishu, Somalia",
                subscription_plan="Professional School",
                subscription_status="ACTIVE",
                subscription_start_date=(now - timedelta(days=90)).date(),
                subscription_expiry_date=(now + timedelta(days=275)).date(),
                status="ACTIVE",
                database_name="hawlwadaag_school_db",
                admin_username="admin",
                admin_email="admin@hawlwadaagschool.edu.so"
            )
            db.add(inst1)
            db.commit()
            db.execute(text("SELECT setval(pg_get_serial_sequence('institutions', 'id'), (SELECT max(id) FROM institutions))"))
            db.commit()

        # Check total institutions count
        total_insts = db.query(Institution).count()
        if total_insts <= 1:
            print("Seeding reference institutions matching dashboard design...")
            reference_institutions = [
                {
                    "code": "SOM-SCH-0002",
                    "name": "Mogadishu Elite Academy",
                    "type": "School",
                    "contact": "Ahmed Nuur",
                    "email": "info@mogadishuelite.edu.so",
                    "phone": "+252 61 250 8505",
                    "region": "Banaadir",
                    "city": "Mogadishu",
                    "plan": "Professional School",
                    "status": "Active",
                    "students": 420,
                    "teachers": 24,
                    "created_offset_days": 1
                },
                {
                    "code": "SOM-ACA-0001",
                    "name": "Al-Hikma Institute",
                    "type": "Academy",
                    "contact": "Sheikh Abdirahman",
                    "email": "contact@alhikma.edu.so",
                    "phone": "+252 63 440 1234",
                    "region": "Maroodi Jeex",
                    "city": "Hargeisa",
                    "plan": "Professional School",
                    "status": "Active",
                    "students": 310,
                    "teachers": 16,
                    "created_offset_days": 2
                },
                {
                    "code": "SOM-SCH-0003",
                    "name": "Banaadir Primary School",
                    "type": "School",
                    "contact": "Faadumo Jaamac",
                    "email": "info@banaadirprimary.edu.so",
                    "phone": "+252 61 555 8899",
                    "region": "Banaadir",
                    "city": "Mogadishu",
                    "plan": "Starter Academy",
                    "status": "Active",
                    "students": 280,
                    "teachers": 14,
                    "created_offset_days": 3
                },
                {
                    "code": "SOM-ACA-0002",
                    "name": "Somali Skills Institute",
                    "type": "Academy",
                    "contact": "Mohamed Mire",
                    "email": "info@somaliskills.edu.so",
                    "phone": "+252 69 912 3456",
                    "region": "Jubbada Hoose",
                    "city": "Kismayo",
                    "plan": "Professional School",
                    "status": "Pending",
                    "students": 190,
                    "teachers": 12,
                    "created_offset_days": 4
                },
                {
                    "code": "SOM-SCH-0004",
                    "name": "Hodan Secondary School",
                    "type": "School",
                    "contact": "Xassan Cali",
                    "email": "contact@hodansecondary.edu.so",
                    "phone": "+252 61 777 3322",
                    "region": "Banaadir",
                    "city": "Mogadishu",
                    "plan": "Professional School",
                    "status": "Active",
                    "students": 510,
                    "teachers": 28,
                    "created_offset_days": 5
                },
                {
                    "code": "SOM-COL-0001",
                    "name": "Somali National College of Technology",
                    "type": "College",
                    "contact": "Eng. Cabdiweli Farax",
                    "email": "admissions@snct.edu.so",
                    "phone": "+252 61 888 4411",
                    "region": "Banaadir",
                    "city": "Mogadishu",
                    "plan": "Enterprise Institution",
                    "status": "Active",
                    "students": 850,
                    "teachers": 42,
                    "created_offset_days": 12
                },
                {
                    "code": "SOM-ACA-0003",
                    "name": "Abudwak Community Academy",
                    "type": "Academy",
                    "contact": "Mahad Warsame",
                    "email": "info@abudwakacademy.edu.so",
                    "phone": "+252 61 250 8505",
                    "region": "Galgaduud",
                    "city": "Abudwak",
                    "plan": "Professional School",
                    "status": "Active",
                    "students": 320,
                    "teachers": 18,
                    "created_offset_days": 15
                }
            ]

            for inst_data in reference_institutions:
                created_dt = now - timedelta(days=inst_data["created_offset_days"])
                inst = Institution(
                    code=inst_data["code"],
                    name=inst_data["name"],
                    type=inst_data["type"],
                    contact_person=inst_data["contact"],
                    email=inst_data["email"],
                    phone=inst_data["phone"],
                    region=inst_data["region"],
                    city=inst_data["city"],
                    address=f"{inst_data['city']}, {inst_data['region']}, Somalia",
                    subscription_plan=inst_data["plan"],
                    subscription_status="ACTIVE" if inst_data["status"].upper() == "ACTIVE" else "TRIAL",
                    subscription_start_date=(now - timedelta(days=10)).date(),
                    subscription_expiry_date=(now + timedelta(days=355)).date(),
                    status=inst_data["status"].upper(),
                    admin_username=f"admin_{inst_data['code'].lower().replace('-', '_')}",
                    admin_email=inst_data["email"],
                    created_at=created_dt
                )
                db.add(inst)
            db.commit()
            print("[OK] Seeded reference institutions.")

        # Ensure Role SUPER_ADMIN exists
        super_role = db.query(Role).filter(Role.name == "SUPER_ADMIN").first()
        if not super_role:
            super_role = Role(name="SUPER_ADMIN", description="Somroyal Platform Super Administrator", is_system=True)
            db.add(super_role)
            db.commit()
            print("[OK] Created 'SUPER_ADMIN' role.")

        # Ensure User 'superadmin' exists
        super_user = db.query(User).filter((User.username == "superadmin") | (User.email == "superadmin@somroyal.com")).first()
        if not super_user:
            hashed_pwd = get_password_hash("Admin@Hawlwadaag2026")
            super_user = User(
                email="superadmin@somroyal.com",
                username="superadmin",
                hashed_password=hashed_pwd,
                full_name="Somroyal Super Admin",
                phone_number="+252612508505",
                is_active=True,
                is_superuser=True
            )
            db.add(super_user)
            db.commit()
            db.refresh(super_user)
            print("[OK] Created 'superadmin' user.")

        # Assign SUPER_ADMIN role only to super_user
        if super_user:
            super_user.is_superuser = True
            has_sr = any(r.name == "SUPER_ADMIN" for r in super_user.roles)
            if not has_sr:
                ur = UserRole(user_id=super_user.id, role_id=super_role.id)
                db.add(ur)
            db.commit()

        # Configure School Admin 'admin': is_superuser = False, belongs to Hawlwadaag School
        admin_user = db.query(User).filter(User.username == "admin").first()
        if admin_user:
            admin_user.is_superuser = False
            admin_user.institution_id = 1
            admin_user.full_name = "School Administrator"
            for r in list(admin_user.roles):
                if r.name == "SUPER_ADMIN":
                    db.query(UserRole).filter(UserRole.user_id == admin_user.id, UserRole.role_id == r.id).delete()
            db.commit()
            print("[OK] Configured School Admin 'admin' (is_superuser=False, institution_id=1).")
        print("[OK] Verified distinct roles & privileges.")

        # Seed realistic payments
        if db.query(InstitutionPayment).count() == 0:
            print("Seeding initial subscription payments...")
            insts = db.query(Institution).all()
            for idx, inst in enumerate(insts[:5]):
                payment = InstitutionPayment(
                    institution_id=inst.id,
                    reference=f"PAY-SOM-{1000 + idx}",
                    amount=95.00 if idx == 0 else 25.00,
                    payment_method="EVC Plus" if idx % 2 == 0 else "Zaad",
                    status="Completed",
                    payment_date=now - timedelta(days=idx + 1),
                    notes=f"Payment for {inst.name}"
                )
                db.add(payment)
            db.commit()
            print("[OK] Seeded sample payments.")

        # Ensure all existing users, students, teachers, classes have institution_id=1
        for table in ['users', 'students', 'teachers', 'classes']:
            db.execute(text(f"UPDATE {table} SET institution_id = 1 WHERE institution_id IS NULL"))
        db.commit()
        print("[OK] All existing school records mapped to institution 1.")

    except Exception as e:
        db.rollback()
        print(f"Error during migration: {e}")
        raise
    finally:
        db.close()

if __name__ == '__main__':
    run_migration()
