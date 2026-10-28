import sys
import os
sys.path.insert(0, os.path.abspath("."))
from app.core.database import SessionLocal
from app.models.fee import FeeStructure, StudentFee, FeePayment
from app.models.school_class import SchoolClass
from app.models.student import Student

db = SessionLocal()

print("=== 1. FEE STRUCTURES ===")
for fs in db.query(FeeStructure).order_by(FeeStructure.id).all():
    inv_count = db.query(StudentFee).filter(StudentFee.fee_structure_id == fs.id).count()
    pay_count = db.query(FeePayment).join(StudentFee, FeePayment.student_fee_id == StudentFee.id).filter(StudentFee.fee_structure_id == fs.id).count()
    c_name = fs.school_class.name if fs.school_class else "None"
    print(f"ID: {fs.id:3d} | Name: {fs.name:<32} | AY: {fs.academic_year} | Class: {c_name} (ID: {fs.class_id}) | Amt: {fs.amount:6.2f} | Invoices: {inv_count:2d} | Payments: {pay_count:2d} | Status: {fs.status}")

print("\n=== 2. INVOICES BREAKDOWN ===")
total_inv = db.query(StudentFee).count()
orphan_inv = db.query(StudentFee).filter(StudentFee.fee_structure_id.is_(None)).count()
attached_inv = db.query(StudentFee).filter(StudentFee.fee_structure_id.is_not(None)).count()
print(f"Total Invoices: {total_inv} | Orphan (fee_structure_id is NULL): {orphan_inv} | Attached: {attached_inv}")

print("\n=== 3. PAYMENTS BREAKDOWN ===")
total_pay = db.query(FeePayment).count()
orphan_struct_pay = db.query(FeePayment).join(StudentFee, FeePayment.student_fee_id == StudentFee.id).filter(StudentFee.fee_structure_id.is_(None)).count()
attached_struct_pay = db.query(FeePayment).join(StudentFee, FeePayment.student_fee_id == StudentFee.id).filter(StudentFee.fee_structure_id.is_not(None)).count()
print(f"Total Payments: {total_pay} | Payments on Orphan Invoices: {orphan_struct_pay} | Payments on Attached Invoices: {attached_struct_pay}")

print("\n=== 4. STUDENTS SUMMARY ===")
students = db.query(Student).all()
print(f"Total Students: {len(students)}")
for s in students:
    enr_classes = [f"{e.school_class.name} ({e.academic_year})" for e in s.enrollments if e.status == "ACTIVE" and e.school_class]
    inv_c = db.query(StudentFee).filter(StudentFee.student_id == s.id).count()
    pay_c = db.query(FeePayment).filter(FeePayment.student_id == s.id).count()
    print(f"ID: {s.id:3d} | Adm: {s.admission_number:<12} | Name: {s.full_name:<25} | Classes: {enr_classes} | Invoices: {inv_c} | Payments: {pay_c}")

db.close()
