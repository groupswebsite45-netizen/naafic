from app.core.database import SessionLocal
from app.models.school_class import SchoolClass
from app.models.student_enrollment import StudentEnrollment
from app.models.teacher_assignment import TeacherAssignment
from app.models.exam import Exam, ExamResult
from app.models.timetable import Timetable
from app.models.attendance import Attendance
from app.models.fee import FeeStructure

db = SessionLocal()

print("ID | Academic Year | Name | Section | Code | Enr | TA | Exam | TT | Att | Fee")
print("-" * 80)
for c in db.query(SchoolClass).order_by(SchoolClass.academic_year, SchoolClass.name, SchoolClass.id).all():
    enr = db.query(StudentEnrollment).filter(StudentEnrollment.class_id == c.id).count()
    ta = db.query(TeacherAssignment).filter(TeacherAssignment.class_id == c.id).count()
    ex = db.query(Exam).filter(Exam.class_id == c.id).count()
    tt = db.query(Timetable).filter(Timetable.class_id == c.id).count()
    att = db.query(Attendance).filter(Attendance.class_id == c.id).count()
    fee = db.query(FeeStructure).filter(FeeStructure.class_id == c.id).count()
    print(f"{c.id:3d} | {c.academic_year:10s} | {c.name:20s} | {str(c.section):12s} | {c.code:15s} | {enr:3d} | {ta:2d} | {ex:4d} | {tt:2d} | {att:3d} | {fee:3d}")

db.close()
