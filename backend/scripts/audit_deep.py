import sys
from app.core.database import SessionLocal
from app.models.teacher import Teacher
from app.models.teacher_assignment import TeacherAssignment
from app.models.school_class import SchoolClass
from app.models.subject import Subject
from app.models.exam import Exam, ExamResult
from app.models.result_submission import ResultSubmission
from app.models.student_enrollment import StudentEnrollment

db = SessionLocal()

print("=" * 60)
print("ALL CLASSES IN DB:")
print("=" * 60)
for c in db.query(SchoolClass).order_by(SchoolClass.academic_year, SchoolClass.name, SchoolClass.id).all():
    enr = db.query(StudentEnrollment).filter(StudentEnrollment.class_id == c.id).count()
    assigns = db.query(TeacherAssignment).filter(TeacherAssignment.class_id == c.id).count()
    exams = db.query(Exam).filter(Exam.class_id == c.id).count()
    print(f"Class ID {c.id:3d} | Year: {c.academic_year:10s} | Name: {c.name:15s} | Code: {c.code:15s} | Div: {c.division:10s} | Level: {c.level:10s} | Sec: {c.section or '':3s} | Enrolled: {enr:2d} | Assigns: {assigns:2d} | Exams: {exams:2d}")

print("\n" + "=" * 60)
print("ALL TEACHERS AND ASSIGNMENTS:")
print("=" * 60)
for t in db.query(Teacher).order_by(Teacher.id).all():
    t_assigns = db.query(TeacherAssignment).filter(TeacherAssignment.teacher_id == t.id).all()
    print(f"\nTeacher ID {t.id} | No: {t.teacher_number} | Name: {t.full_name} | UserID: {t.user_id} | Status: {t.status} | Assignments Count: {len(t_assigns)}")
    for a in t_assigns:
        c_name = a.school_class.name if a.school_class else f"Class #{a.class_id} (ORPHAN)"
        s_name = a.subject.name if a.subject else f"Subject #{a.subject_id} (ORPHAN)"
        print(f"   -> Assign ID {a.id:3d} | Class ID {a.class_id:3d} ({c_name}) | Subj ID {a.subject_id:3d} ({s_name}) | Year: {a.academic_year} | Status: {a.status}")

print("\n" + "=" * 60)
print("ALL EXAMS:")
print("=" * 60)
for e in db.query(Exam).order_by(Exam.id).all():
    t_name = e.teacher.full_name if e.teacher else "NO TEACHER"
    c_name = e.school_class.name if e.school_class else "NO CLASS"
    s_name = e.subject.name if e.subject else "NO SUBJECT"
    subs = db.query(ResultSubmission).filter(ResultSubmission.exam_id == e.id).count()
    results = db.query(ExamResult).filter(ExamResult.exam_id == e.id).count()
    print(f"Exam ID {e.id:3d} | Name: {e.name:35s} | Type: {e.exam_type:12s} | Year: {e.academic_year:10s} | Teacher: {t_name:25s} (ID {e.teacher_id}) | Class: {c_name:15s} (ID {e.class_id}) | Subj: {s_name:25s} (ID {e.subject_id}) | Status: {e.status:10s} | Subs: {subs} | Results: {results}")

print("\n" + "=" * 60)
print("ALL RESULT SUBMISSIONS:")
print("=" * 60)
for s in db.query(ResultSubmission).order_by(ResultSubmission.id).all():
    tch = s.teacher.full_name if s.teacher else "NO TEACHER"
    cls = s.school_class.name if s.school_class else "NO CLASS"
    sb = s.subject.name if s.subject else "NO SUBJECT"
    results = db.query(ExamResult).filter(ExamResult.submission_id == s.id).count()
    print(f"Sub ID {s.id:3d} | Exam ID {s.exam_id:3d} ({s.exam_name:30s}) | Class ID {s.class_id:3d} ({cls:15s}) | Subj ID {s.subject_id:3d} ({sb:25s}) | Teacher ID {s.teacher_id:3d} ({tch:25s}) | Year: {s.academic_year:10s} | Status: {s.status:12s} | Exp: {s.expected_students:2d} | Comp: {s.completed_students:2d} | Results in DB: {results}")
