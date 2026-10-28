import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.core.database import SessionLocal
from app.models.school_class import SchoolClass
from app.models.student_enrollment import StudentEnrollment
from app.models.teacher_assignment import TeacherAssignment
from app.models.exam import Exam
from app.models.timetable import Timetable
from app.models.attendance import Attendance
from app.models.fee import FeeStructure

db = SessionLocal()
classes = db.query(SchoolClass).order_by(SchoolClass.academic_year, SchoolClass.division, SchoolClass.level, SchoolClass.section).all()
print(f"Total Classes: {len(classes)}")
header = f"{'ID':4} | {'Name':25} | {'Code':15} | {'Div':10} | {'Level':10} | {'Sec':6} | {'Year':10} | {'Stat':8} | Enr | TAs | Exm | Tt | Att | Fee"
print(header)
print("-" * len(header))
for c in classes:
    enr = db.query(StudentEnrollment).filter(StudentEnrollment.class_id == c.id, StudentEnrollment.status == 'ACTIVE').count()
    ta = db.query(TeacherAssignment).filter(TeacherAssignment.class_id == c.id).count()
    ex = db.query(Exam).filter(Exam.class_id == c.id).count()
    tt = db.query(Timetable).filter(Timetable.class_id == c.id).count()
    att = db.query(Attendance).filter(Attendance.class_id == c.id).count()
    fs = db.query(FeeStructure).filter(FeeStructure.class_id == c.id).count()
    print(f"{c.id:4d} | {str(c.name):25s} | {str(c.code):15s} | {str(c.division):10s} | {str(c.level):10s} | {str(c.section):6s} | {str(c.academic_year):10s} | {str(c.status):8s} | {enr:3d} | {ta:3d} | {ex:3d} | {tt:2d} | {att:3d} | {fs:3d}")
db.close()
