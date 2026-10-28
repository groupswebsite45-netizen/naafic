"""Fix remaining subject issues after main cleanup."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.subject import Subject

db = SessionLocal()

# Fix Islamic Studies code (ISL-101 is taken by Arabic & Islamic Studies)
# Use ISL-201 for pure Islamic Studies
isl = db.query(Subject).filter(Subject.id == 58).first()
if isl:
    print(f"Islamic Studies current code: {isl.code}")
    # Check if ISL-201 is free
    conflict = db.query(Subject).filter(Subject.code == "ISL-201", Subject.id != 58).first()
    if not conflict:
        isl.code = "ISL-201"
        print(f"Islamic Studies code updated to ISL-201")
    else:
        print(f"ISL-201 is taken by {conflict.name}")

# Mark Mathematics-Test INACTIVE (it has released results but they should be under Mathematics)
# Cannot merge because subject_id is embedded in exam results — just mark INACTIVE to hide from UI
math_test = db.query(Subject).filter(Subject.id == 52).first()
if math_test:
    math_test.status = "INACTIVE"
    print(f"Mathematics-Test [52] marked INACTIVE")

# Also check Arabic & Islamic Studies [24] — could be renamed for clarity
# Keep it as-is since it has real teacher assignments/exams

db.commit()
print("Done!")
db.close()
