import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.core.database import SessionLocal
from app.models.student import Student
from app.models.school_class import SchoolClass
from app.models.user import User

db = SessionLocal()

# The proposed 10 Primary Students:
# 5 in Grade 7 - A (Class ID 147, 2026/2027)
# 5 in Grade 8 - A (Class ID 32, 2026/2027)
primary_plan = [
    # Grade 7 - A
    {"id": 22, "name": "Amina Hassan Ibrahim", "adm": "ADM-2026-002", "class_id": 147, "class_name": "Grade 7 - A", "year": "2026/2027", "div": "PRIMARY"},
    {"id": 23, "name": "Liban Abdirahman Elmi", "adm": "ADM-2026-003", "class_id": 147, "class_name": "Grade 7 - A", "year": "2026/2027", "div": "PRIMARY"},
    {"id": 24, "name": "Hafsa Mohamud Adan", "adm": "ADM-2026-004", "class_id": 147, "class_name": "Grade 7 - A", "year": "2026/2027", "div": "PRIMARY"},
    {"id": 1,  "name": "Mushtaaq Ahmed Cali", "adm": "ADM-413501", "class_id": 147, "class_name": "Grade 7 - A", "year": "2026/2027", "div": "PRIMARY"},
    {"id": 244, "name": "Amina Farah", "adm": "ADM-527B23", "class_id": 147, "class_name": "Grade 7 - A", "year": "2026/2027", "div": "PRIMARY"},
    # Grade 8 - A
    {"id": 25, "name": "Zakarie Jama Hussein", "adm": "ADM-2026-005", "class_id": 32, "class_name": "Grade 8 - A", "year": "2026/2027", "div": "PRIMARY"},
    {"id": 26, "name": "Safia Farah Gedi", "adm": "ADM-2026-006", "class_id": 32, "class_name": "Grade 8 - A", "year": "2026/2027", "div": "PRIMARY"},
    {"id": 21, "name": "Mustaf Ali Yusuf", "adm": "ADM-2026-001", "class_id": 32, "class_name": "Grade 8 - A", "year": "2026/2027", "div": "PRIMARY"},
    {"id": 289, "name": "Mustaf Noor", "adm": "ADM-2026-009", "class_id": 32, "class_name": "Grade 8 - A", "year": "2026/2027", "div": "PRIMARY"},
    {"id": 290, "name": "Amina Ibrahim", "adm": "ADM-2026-010", "class_id": 32, "class_name": "Grade 8 - A", "year": "2026/2027", "div": "PRIMARY"},
]

# The proposed 10 Secondary Students:
# 5 in Form 1 - A (Class ID 157, 2026/2027)
# 5 in Form 2 - A (Class ID 56, 2026/2027)
secondary_plan = [
    # Form 1 - A
    {"id": 27, "name": "Khaalid Ibrahim Nur", "adm": "ADM-2026-007", "class_id": 157, "class_name": "Form 1 - A", "year": "2026/2027", "div": "SECONDARY"},
    {"id": 28, "name": "Yasmin Osman Roble", "adm": "ADM-2026-008", "class_id": 157, "class_name": "Form 1 - A", "year": "2026/2027", "div": "SECONDARY"},
    {"id": 29, "name": "Khadija Ali Warsame", "adm": "ADM-562018", "class_id": 157, "class_name": "Form 1 - A", "year": "2026/2027", "div": "SECONDARY"},
    {"id": 30, "name": "Hassan Omar Jama", "adm": "ADM-652157", "class_id": 157, "class_name": "Form 1 - A", "year": "2026/2027", "div": "SECONDARY"},
    {"id": 134, "name": "Dahir Abdi Mohamed", "adm": "ADM-477791", "class_id": 157, "class_name": "Form 1 - A", "year": "2026/2027", "div": "SECONDARY"},
    # Form 2 - A
    {"id": 243, "name": "Fadumo Ali Warsame", "adm": "ADM-869228", "class_id": 56, "class_name": "Form 2 - A", "year": "2026/2027", "div": "SECONDARY"},
    {"id": 74, "name": "Mohamed Ali Mire", "adm": "ADM-PROM-5-1-1580", "class_id": 56, "class_name": "Form 2 - A", "year": "2026/2027", "div": "SECONDARY"},
    {"id": 62, "name": "Abdirashid Nur Elmi", "adm": "ADM-PROM-1-1-1580", "class_id": 56, "class_name": "Form 2 - A", "year": "2026/2027", "div": "SECONDARY"},
    {"id": 63, "name": "Nimo Ahmed Farah", "adm": "ADM-PROM-1-2-1580", "class_id": 56, "class_name": "Form 2 - A", "year": "2026/2027", "div": "SECONDARY"},
    {"id": 64, "name": "Sahra Jama Hussein", "adm": "ADM-PROM-1-3-1580", "class_id": 56, "class_name": "Form 2 - A", "year": "2026/2027", "div": "SECONDARY"},
]

total_students = db.query(Student).count()
keep_ids = [p["id"] for p in primary_plan] + [s["id"] for s in secondary_plan]
assert len(keep_ids) == 20
assert len(set(keep_ids)) == 20

# Check existence in DB
for sid in keep_ids:
    s = db.get(Student, sid)
    assert s is not None, f"Student {sid} does not exist in DB!"

delete_count = total_students - len(keep_ids)
print(f"Total students in DB: {total_students}")
print(f"Retained students: {len(keep_ids)}")
print(f"Students to delete: {delete_count}")
print("Primary Plan (10):")
for idx, p in enumerate(primary_plan, 1):
    print(f" {idx:2d}. {p['name']:25s} | ID: {p['id']:3d} | Adm: {p['adm']:18s} | Class: {p['class_name']} | Year: {p['year']}")
print("Secondary Plan (10):")
for idx, p in enumerate(secondary_plan, 1):
    print(f" {idx:2d}. {p['name']:25s} | ID: {p['id']:3d} | Adm: {p['adm']:18s} | Class: {p['class_name']} | Year: {p['year']}")

db.close()
