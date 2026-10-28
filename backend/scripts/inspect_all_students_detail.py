import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from collections import defaultdict
from app.core.database import SessionLocal
from app.models.student import Student

db = SessionLocal()
students = db.query(Student).all()
print(f"Total students: {len(students)}")

prefixes = defaultdict(list)
for s in students:
    parts = s.admission_number.split("-")
    p = parts[1] if len(parts) > 1 else "OTHER"
    prefixes[p].append(s)

for p, slist in sorted(prefixes.items()):
    print(f"Prefix '{p}': {len(slist)} students. Examples: {[s.admission_number + ' (' + s.full_name + ')' for s in slist[:3]]}")
db.close()
