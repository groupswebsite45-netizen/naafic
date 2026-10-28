import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.core.database import SessionLocal
from app.models.student import Student
from app.models.school_class import SchoolClass

db = SessionLocal()

# Find all test class IDs:
test_classes = db.query(SchoolClass).filter(
    (SchoolClass.name.ilike("%test%")) |
    (SchoolClass.name.ilike("%12subj%")) |
    (SchoolClass.name.ilike("%form 5%")) |
    (SchoolClass.name.ilike("%form 6%")) |
    (SchoolClass.name.in_(["Form 1", "Form 2", "Form 3", "Form 4", "Form 5", "Form 6", "Grade 7", "Grade 8"])) |
    (SchoolClass.status == "INACTIVE")
).all()
test_class_ids = set(c.id for c in test_classes)
print(f"Test/Inactive class IDs count: {len(test_class_ids)}: {[c.name for c in test_classes]}")

candidates = []
for s in db.query(Student).all():
    enr_class_ids = set(e.class_id for e in s.enrollments)
    if not enr_class_ids.intersection(test_class_ids):
        candidates.append(s)

print(f"\nTotal Students never enrolled in any test/inactive class: {len(candidates)}")
for s in candidates:
    enrs = [(e.school_class.name, e.school_class.division, e.academic_year, e.status) for e in s.enrollments]
    print(f"ID: {s.id:3d} | Adm: {s.admission_number:15s} | Name: {s.full_name:25s} | User: {s.user_id} | Enrs: {enrs}")

db.close()
