import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.core.database import SessionLocal
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.models.school_class import SchoolClass

db = SessionLocal()

# Valid Primary classes:
primary_classes = db.query(SchoolClass).filter(
    SchoolClass.division == "PRIMARY",
    SchoolClass.status == "ACTIVE",
    SchoolClass.academic_year.in_(["2026/2027", "2026-2027"]),
    SchoolClass.level.in_([f"Grade {i}" for i in range(1, 9)])
).all()
primary_class_ids = [c.id for c in primary_classes]
print(f"Valid Primary Classes: {[(c.id, c.name, c.code) for c in primary_classes]}")

primary_enrs = db.query(StudentEnrollment).filter(
    StudentEnrollment.class_id.in_(primary_class_ids),
    StudentEnrollment.status == "ACTIVE",
    StudentEnrollment.academic_year.in_(["2026/2027", "2026-2027"])
).all()
print(f"Total Active Enrollments in Valid Primary Classes: {len(primary_enrs)}")

# Valid Secondary classes:
secondary_classes = db.query(SchoolClass).filter(
    SchoolClass.division == "SECONDARY",
    SchoolClass.status == "ACTIVE",
    SchoolClass.academic_year.in_(["2026/2027", "2026-2027"]),
    SchoolClass.level.in_([f"Form {i}" for i in range(1, 5)])
).all()
secondary_class_ids = [c.id for c in secondary_classes]
print(f"Valid Secondary Classes: {[(c.id, c.name, c.code) for c in secondary_classes]}")

secondary_enrs = db.query(StudentEnrollment).filter(
    StudentEnrollment.class_id.in_(secondary_class_ids),
    StudentEnrollment.status == "ACTIVE",
    StudentEnrollment.academic_year.in_(["2026/2027", "2026-2027"])
).all()
print(f"Total Active Enrollments in Valid Secondary Classes: {len(secondary_enrs)}")

db.close()
