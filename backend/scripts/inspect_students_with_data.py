import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.core.database import SessionLocal
from app.models.student import Student
from app.models.fee import StudentFee, FeePayment
from app.models.exam import ExamResult
from app.models.attendance import Attendance

db = SessionLocal()
students = db.query(Student).all()

# Find students that have exam results or attendance or fee records:
with_data = []
for s in students:
    exams_cnt = db.query(ExamResult).filter(ExamResult.student_id == s.id).count()
    att_cnt = db.query(Attendance).filter(Attendance.student_id == s.id).count()
    fee_cnt = db.query(StudentFee).filter(StudentFee.student_id == s.id).count()
    pay_cnt = db.query(FeePayment).filter(FeePayment.student_id == s.id).count()
    enrs = [(e.school_class.name if e.school_class else "None", e.school_class.division if e.school_class else "None", e.academic_year, e.status) for e in s.enrollments]
    if exams_cnt > 0 or att_cnt > 0 or fee_cnt > 0 or pay_cnt > 0:
        with_data.append((s, exams_cnt, att_cnt, fee_cnt, pay_cnt, enrs))

print(f"Total students with exam/att/fee/pay records: {len(with_data)}")
print(f"{'ID':3} | {'Adm':15} | {'Name':25} | {'Exm':3} | {'Att':3} | {'Fee':3} | {'Pay':3} | {'Enrollments'}")
print("-" * 90)
for s, exm, att, fee, pay, enrs in with_data:
    print(f"{s.id:3d} | {s.admission_number:15s} | {s.full_name:25s} | {exm:3d} | {att:3d} | {fee:3d} | {pay:3d} | {enrs}")

db.close()
