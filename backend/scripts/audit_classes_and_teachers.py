import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.core.database import SessionLocal
from app.models.school_class import SchoolClass
from app.models.student_enrollment import StudentEnrollment
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.teacher_assignment import TeacherAssignment
from app.models.subject import Subject
from app.models.exam import Exam, ExamResult
from app.models.user import User
from app.models.fee import StudentFee
from sqlalchemy import func

db = SessionLocal()

print("==================================================")
print("1. CLASSES AUDIT")
print("==================================================")
classes = db.query(SchoolClass).order_by(SchoolClass.id).all()
for c in classes:
    enr_cnt = db.query(StudentEnrollment).filter(StudentEnrollment.class_id == c.id, StudentEnrollment.status == 'ACTIVE').count()
    ta_cnt = db.query(TeacherAssignment).filter(TeacherAssignment.class_id == c.id).count()
    ex_cnt = db.query(Exam).filter(Exam.class_id == c.id).count()
    fee_cnt = db.query(StudentFee).filter(StudentFee.class_id == c.id).count()
    print(f"ID: {c.id:<4} | Name: {c.name:<25} | Code: {c.code:<15} | Div: {c.division:<10} | Year: {c.academic_year:<10} | Status: {c.status:<8} | Enr: {enr_cnt} | TA: {ta_cnt} | Exam: {ex_cnt} | Fee: {fee_cnt}")

print("\n==================================================")
print("2. ACTIVE ENROLLMENTS PER CLASS (ACADEMIC YEAR 2026/2027)")
print("==================================================")
enrs = (
    db.query(SchoolClass.id, SchoolClass.name, func.count(StudentEnrollment.id))
    .join(StudentEnrollment, SchoolClass.id == StudentEnrollment.class_id)
    .filter(StudentEnrollment.status == 'ACTIVE', StudentEnrollment.academic_year == '2026/2027')
    .group_by(SchoolClass.id, SchoolClass.name)
    .all()
)
for row in enrs:
    print(f"Class ID {row[0]}: {row[1]} -> {row[2]} active students")

print("\n==================================================")
print("3. TEACHERS & TEACHER PROFILES")
print("==================================================")
teachers = db.query(Teacher).order_by(Teacher.id).all()
for t in teachers:
    u = db.query(User).filter(User.id == t.user_id).first() if t.user_id else None
    ta_list = db.query(TeacherAssignment).filter(TeacherAssignment.teacher_id == t.id).all()
    u_str = f"User {u.id} ({u.username})" if u else "NO USER"
    print(f"Teacher ID: {t.id:<3} | {u_str:<25} | Name: {t.first_name} {t.last_name:<20} | Status: {t.status} | Assignments: {len(ta_list)}")
    for ta in ta_list:
        sub = db.query(Subject).filter(Subject.id == ta.subject_id).first()
        cls = db.query(SchoolClass).filter(SchoolClass.id == ta.class_id).first()
        s_name = sub.name if sub else f"Subj {ta.subject_id}"
        c_name = cls.name if cls else f"Class {ta.class_id}"
        print(f"   * TA ID {ta.id:<3}: Subj [{ta.subject_id}] {s_name:<28} -> Class [{ta.class_id}] {c_name:<15} | Year: {ta.academic_year} | Status: {ta.status}")

print("\n==================================================")
print("4. EXAMS IN DATABASE")
print("==================================================")
exams = db.query(Exam).order_by(Exam.id).all()
print(f"Total Exams: {len(exams)}")
for e in exams:
    cls = db.query(SchoolClass).filter(SchoolClass.id == e.class_id).first()
    sub = db.query(Subject).filter(Subject.id == e.subject_id).first()
    t = db.query(Teacher).filter(Teacher.id == e.teacher_id).first() if e.teacher_id else None
    c_name = cls.name if cls else f"Class {e.class_id}"
    s_name = sub.name if sub else f"Subj {e.subject_id}"
    t_name = f"{t.first_name} {t.last_name} (TID {e.teacher_id})" if t else f"TID {e.teacher_id}"
    res_cnt = db.query(ExamResult).filter(ExamResult.exam_id == e.id).count()
    print(f"Exam ID: {e.id:<4} | Name: {e.name:<35} | Class: [{e.class_id}] {c_name:<15} | Subj: [{e.subject_id}] {s_name:<20} | Teacher: {t_name:<30} | Status: {e.status:<10} | Year: {e.academic_year:<10} | Results: {res_cnt}")

db.close()
