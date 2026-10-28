from app.core.database import SessionLocal
from app.models.school_class import SchoolClass
from app.models.subject import Subject
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.models.teacher_assignment import TeacherAssignment
from app.models.exam import Exam, ExamResult
from app.models.timetable import Timetable
from app.models.attendance import Attendance
from collections import defaultdict

db = SessionLocal()

print("==================================================")
print("1. CLASSES AUDIT")
print("==================================================")
classes = db.query(SchoolClass).order_by(SchoolClass.academic_year, SchoolClass.name).all()
print(f"Total Classes in DB: {len(classes)}")

# Group classes by (academic_year, name, section)
class_groups = defaultdict(list)
for c in classes:
    enr_count = db.query(StudentEnrollment).filter(StudentEnrollment.class_id == c.id).count()
    ta_count = db.query(TeacherAssignment).filter(TeacherAssignment.class_id == c.id).count()
    ex_count = db.query(Exam).filter(Exam.class_id == c.id).count()
    tt_count = db.query(Timetable).filter(Timetable.class_id == c.id).count()
    att_count = db.query(Attendance).filter(Attendance.class_id == c.id).count()
    print(f"[{c.id}] Name: '{c.name}', Code: '{c.code}', Section: '{c.section}', Year: '{c.academic_year}', Status: '{c.status}' | Students: {enr_count}, TAs: {ta_count}, Exams: {ex_count}, Timetable: {tt_count}, Attendance: {att_count}")
    norm_name = c.name.strip().lower()
    norm_sec = (c.section or "").strip().lower()
    class_groups[(c.academic_year, norm_name, norm_sec)].append(c)

print("\n--- Potential Duplicate Class Groups ---")
for key, grp in class_groups.items():
    if len(grp) > 1:
        print(f"DUPLICATE GROUP: Year={key[0]}, Name={key[1]}, Section={key[2]} -> IDs: {[c.id for c in grp]}")

print("\n==================================================")
print("2. SUBJECTS AUDIT")
print("==================================================")
subjects = db.query(Subject).order_by(Subject.name).all()
print(f"Total Subjects in DB: {len(subjects)}")
subj_names = defaultdict(list)
for s in subjects:
    ta_count = db.query(TeacherAssignment).filter(TeacherAssignment.subject_id == s.id).count()
    ex_count = db.query(Exam).filter(Exam.subject_id == s.id).count()
    print(f"[{s.id}] Name: '{s.name}', Code: '{s.code}', Dept: '{s.department}', Status: '{s.status}' | TAs: {ta_count}, Exams: {ex_count}")
    subj_names[s.name.strip().lower()].append(s)

print("\n--- Potential Duplicate Subject Groups ---")
for name, grp in subj_names.items():
    if len(grp) > 1:
        print(f"DUPLICATE SUBJECT: Name={name} -> IDs: {[s.id for s in grp]}")

print("\n==================================================")
print("3. STUDENTS & ENROLLMENTS AUDIT")
print("==================================================")
students = db.query(Student).all()
print(f"Total Students in DB: {len(students)}")
adm_numbers = defaultdict(list)
for st in students:
    adm_numbers[st.admission_number.strip().upper()].append(st)

print("Duplicate Admission Numbers:")
dup_adms = {k: v for k, v in adm_numbers.items() if len(v) > 1}
if dup_adms:
    for adm, grp in dup_adms.items():
        print(f"DUPLICATE ADM: {adm} -> Student IDs: {[s.id for s in grp]}")
else:
    print("None. All admission numbers are unique.")

enrollments = db.query(StudentEnrollment).all()
print(f"Total Enrollments in DB: {len(enrollments)}")
student_year_enrollments = defaultdict(list)
for enr in enrollments:
    if enr.status == "ACTIVE":
        student_year_enrollments[(enr.student_id, enr.academic_year)].append(enr)

print("Duplicate Active Enrollments in Same Academic Year:")
dup_enrs = {k: v for k, v in student_year_enrollments.items() if len(v) > 1}
if dup_enrs:
    for (sid, ayr), grp in dup_enrs.items():
        print(f"DUPLICATE ACTIVE ENROLLMENT: Student {sid}, Year {ayr} -> Enrollment IDs: {[e.id for e in grp]}, Classes: {[e.class_id for e in grp]}")
else:
    print("None. Each student has at most 1 active enrollment per academic year.")

print("\n==================================================")
print("4. TEACHER ASSIGNMENTS AUDIT")
print("==================================================")
tas = db.query(TeacherAssignment).all()
print(f"Total Teacher Assignments: {len(tas)}")
ta_groups = defaultdict(list)
for ta in tas:
    ta_groups[(ta.class_id, ta.subject_id, ta.academic_year)].append(ta)

print("Duplicate Class-Subject-Year Teacher Assignments:")
dup_tas = {k: v for k, v in ta_groups.items() if len(v) > 1}
if dup_tas:
    for (cid, sid, ayr), grp in dup_tas.items():
        print(f"DUPLICATE TA: Class {cid}, Subject {sid}, Year {ayr} -> TA IDs: {[t.id for t in grp]}")
else:
    print("None.")

db.close()
