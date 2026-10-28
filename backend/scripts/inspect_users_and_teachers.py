import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.core.database import SessionLocal
from app.models.user import User
from app.models.teacher import Teacher
from app.models.teacher_assignment import TeacherAssignment

db = SessionLocal()
users = db.query(User).all()
print("=== USERS WITH TEACHER ROLE OR TEACHER IN USERNAME ===")
for u in users:
    roles = [r.name for r in u.roles] if hasattr(u, "roles") else []
    if "TEACHER" in roles or "teacher" in u.username.lower():
        t = db.query(Teacher).filter(Teacher.user_id == u.id).first()
        t_email = db.query(Teacher).filter(Teacher.email == u.email).first() if not t and u.email else None
        linked = str(t.id) if t else (f"{t_email.id} (via email)" if t_email else "NONE")
        name = f"{t.first_name} {t.last_name}" if t else (f"{t_email.first_name} {t_email.last_name}" if t_email else "N/A")
        ta_cnt = db.query(TeacherAssignment).filter(TeacherAssignment.teacher_id == (t.id if t else (t_email.id if t_email else None))).count() if (t or t_email) else 0
        print(f"User ID: {u.id:<4} | Username: {u.username:<25} | Email: {u.email:<35} | Linked Teacher ID: {linked:<15} | Name: {name:<20} | Assignments: {ta_cnt}")

db.close()
