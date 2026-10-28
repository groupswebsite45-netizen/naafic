import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.services.class_service import ClassService
from app.repositories.class_repo import ClassRepository
from app.core.database import SessionLocal
db = SessionLocal()
repo = ClassRepository(db)
classes = repo.get_active_classes_with_students()
print(f"Active classes with students: {len(classes)}")
for c in classes:
    print(f"  [{c.id}] {c.name} | year={c.academic_year} | students={c.students_count}")
db.close()
