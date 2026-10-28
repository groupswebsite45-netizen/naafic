import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.core.database import SessionLocal
from app.models.student import Student
from app.models.school_class import SchoolClass

db = SessionLocal()
students = db.query(Student).all()

test_class_names = [
    "grade 7-12subj", "grade 7-test", "grade 8-test", "form 5", "form 6",
    "timetable test class", "grade 9-test-cf", "grade 7 - ce2f", "grade 7 - 7974a8",
    "form 1 - b", "grade 4 - e", "form 5 - a", "form 6 - a"
]

clean_students = []
for s in students:
    class_names = [e.school_class.name.strip().lower() for e in s.enrollments if e.school_class]
    # Check if enrolled in test class
    has_test_class = any(any(t in cname for t in test_class_names) for cname in class_names)
    if not has_test_class and s.enrollments:
        clean_students.append(s)

print(f"Total students with enrollments and NO test classes: {len(clean_students)}")
for s in clean_students:
    enr_summary = [(e.school_class.name, e.school_class.division, e.academic_year, e.status) for e in s.enrollments if e.school_class]
    print(f"ID: {s.id:3d} | Adm: {s.admission_number:18s} | Name: {s.full_name:25s} | Enrs: {enr_summary}")

db.close()
