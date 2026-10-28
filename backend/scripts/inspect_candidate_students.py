import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.core.database import SessionLocal
from app.models.school_class import SchoolClass
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.models.user import User

db = SessionLocal()

print("=== VALID PRIMARY CLASSES IN 2026/2027 ===")
# Valid primary classes: Grade 1 - Grade 8, division PRIMARY, status ACTIVE, academic_year '2026/2027'
primary_classes = db.query(SchoolClass).filter(
    SchoolClass.division == "PRIMARY",
    SchoolClass.status == "ACTIVE",
    SchoolClass.academic_year.in_(["2026/2027", "2026-2027"]),
    SchoolClass.level.in_([f"Grade {i}" for i in range(1, 9)])
).order_by(SchoolClass.name).all()

for c in primary_classes:
    enrs = db.query(StudentEnrollment).filter(
        StudentEnrollment.class_id == c.id,
        StudentEnrollment.status == "ACTIVE"
    ).all()
    print(f"\nClass [{c.id}] {c.name} ({c.code}, Level: {c.level}, Sec: {c.section}, Year: {c.academic_year}) - Active Students: {len(enrs)}")
    for e in enrs:
        s = e.student
        print(f"   Student ID: {s.id:3d} | Adm: {s.admission_number:15s} | Name: {s.full_name:25s} | User: {s.user_id} | Status: {s.status}")

print("\n=== VALID SECONDARY CLASSES IN 2026/2027 ===")
# Valid secondary classes: Form 1 - Form 4, division SECONDARY, status ACTIVE, academic_year '2026/2027'
secondary_classes = db.query(SchoolClass).filter(
    SchoolClass.division == "SECONDARY",
    SchoolClass.status == "ACTIVE",
    SchoolClass.academic_year.in_(["2026/2027", "2026-2027"]),
    SchoolClass.level.in_([f"Form {i}" for i in range(1, 5)])
).order_by(SchoolClass.name).all()

for c in secondary_classes:
    enrs = db.query(StudentEnrollment).filter(
        StudentEnrollment.class_id == c.id,
        StudentEnrollment.status == "ACTIVE"
    ).all()
    print(f"\nClass [{c.id}] {c.name} ({c.code}, Level: {c.level}, Sec: {c.section}, Year: {c.academic_year}) - Active Students: {len(enrs)}")
    for e in enrs[:15]:  # Show first 15
        s = e.student
        print(f"   Student ID: {s.id:3d} | Adm: {s.admission_number:15s} | Name: {s.full_name:25s} | User: {s.user_id} | Status: {s.status}")

db.close()
