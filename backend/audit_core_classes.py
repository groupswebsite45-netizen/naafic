from app.core.database import SessionLocal
from app.models.school_class import SchoolClass

db = SessionLocal()
for c in db.query(SchoolClass).filter(~SchoolClass.code.like("%PROM%"), ~SchoolClass.code.like("%TST%"), ~SchoolClass.code.like("%TCF%")).order_by(SchoolClass.academic_year, SchoolClass.name).all():
    print(f"[{c.id:3d}] Year: {c.academic_year:10s} | Name: {c.name:20s} | Section: {str(c.section):12s} | Code: {c.code}")

db.close()
