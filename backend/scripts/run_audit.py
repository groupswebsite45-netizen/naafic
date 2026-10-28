"""Full database audit script for the SMS system."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.school_class import SchoolClass
from app.models.subject import Subject
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.models.teacher import Teacher
from app.models.teacher_assignment import TeacherAssignment
from app.models.exam import Exam, ExamResult
from app.models.result_submission import ResultSubmission
from collections import defaultdict

db = SessionLocal()

print("=" * 60)
print("COMPLETE DATABASE AUDIT REPORT")
print("=" * 60)

# =========================
# CLASSES
# =========================
print("\n[CLASSES]")
classes = db.query(SchoolClass).order_by(SchoolClass.academic_year, SchoolClass.division, SchoolClass.level, SchoolClass.section).all()
print(f"Total classes: {len(classes)}")

empty_classes = []
test_classes = []
legit_classes = []

TEST_PATTERNS = ["test", "timetable", "demo", "sample", "fake", "999", "temp", "temporary"]

for c in classes:
    active_students = db.query(StudentEnrollment).filter(
        StudentEnrollment.class_id == c.id,
        StudentEnrollment.status == "ACTIVE"
    ).count()
    ta_count = db.query(TeacherAssignment).filter(TeacherAssignment.class_id == c.id).count()
    exam_count = db.query(Exam).filter(Exam.class_id == c.id).count()
    
    is_test = any(p in (c.name or "").lower() or p in (c.code or "").lower() for p in TEST_PATTERNS)
    
    info = {
        "id": c.id, "name": c.name, "code": c.code, "division": c.division,
        "level": c.level, "section": c.section, "year": c.academic_year,
        "status": c.status, "students": active_students, "tas": ta_count, "exams": exam_count
    }
    
    if is_test:
        test_classes.append(info)
    elif active_students == 0:
        empty_classes.append(info)
    else:
        legit_classes.append(info)

print(f"\n  LEGITIMATE CLASSES (have active students):")
for c in legit_classes:
    print(f"    [{c['id']}] {c['name']!r} | div={c['division']} | year={c['year']} | students={c['students']} | tas={c['tas']} | exams={c['exams']} | status={c['status']}")

print(f"\n  EMPTY CLASSES (0 active students):")
for c in empty_classes:
    print(f"    [{c['id']}] {c['name']!r} | div={c['division']} | year={c['year']} | students={c['students']} | tas={c['tas']} | exams={c['exams']} | status={c['status']}")

print(f"\n  TEST/TEMP CLASSES:")
for c in test_classes:
    print(f"    [{c['id']}] {c['name']!r} | code={c['code']} | status={c['status']}")

# =========================
# SUBJECTS
# =========================
print("\n[SUBJECTS]")
subjects = db.query(Subject).order_by(Subject.name).all()
print(f"Total subjects: {len(subjects)}")

VALID_SUBJECTS = {
    "Mathematics": "MAT-101",
    "English Language": "ENG-101",
    "Somali Language & Literature": "SOM-101",
    "Islamic Studies": "ISL-101",
    "Physics": "PHY-101",
    "Chemistry": "CHE-101",
    "Biology": "BIO-101",
}

TEST_SUB_PATTERNS = ["test", "astronomy", "sci-", "g9-", "-tst", "sample", "fake", "999", "random", "temp",
                     "general science sci", "somali literature", "advanced astronomy"]

valid_subs = []
test_subs = []
other_subs = []

for s in subjects:
    ta_count = db.query(TeacherAssignment).filter(TeacherAssignment.subject_id == s.id).count()
    exam_count = db.query(Exam).filter(Exam.subject_id == s.id).count()
    
    name_lower = (s.name or "").lower()
    code_lower = (s.code or "").lower()
    is_test = any(p in name_lower or p in code_lower for p in TEST_SUB_PATTERNS)
    is_valid = s.name in VALID_SUBJECTS
    
    info = {
        "id": s.id, "name": s.name, "code": s.code, "division": s.division,
        "status": s.status, "tas": ta_count, "exams": exam_count
    }
    
    if is_valid:
        valid_subs.append(info)
    elif is_test:
        test_subs.append(info)
    else:
        other_subs.append(info)

print(f"\n  VALID SUBJECTS ({len(valid_subs)}):")
for s in valid_subs:
    print(f"    [{s['id']}] {s['name']!r} | code={s['code']} | div={s['division']} | tas={s['tas']} | exams={s['exams']} | status={s['status']}")

print(f"\n  TEST/GENERATED SUBJECTS ({len(test_subs)}) - CANDIDATES FOR REMOVAL:")
for s in test_subs:
    print(f"    [{s['id']}] {s['name']!r} | code={s['code']} | tas={s['tas']} | exams={s['exams']} | status={s['status']}")

print(f"\n  OTHER ACTIVE SUBJECTS (school uses but not in 7 core):")
for s in other_subs:
    print(f"    [{s['id']}] {s['name']!r} | code={s['code']} | tas={s['tas']} | exams={s['exams']} | status={s['status']}")

# =========================
# STUDENTS
# =========================
print("\n[STUDENTS & ENROLLMENTS]")
total_students = db.query(Student).count()
active_students = db.query(Student).filter(Student.status == "ACTIVE").count()
total_enrollments = db.query(StudentEnrollment).count()
active_enrollments = db.query(StudentEnrollment).filter(StudentEnrollment.status == "ACTIVE").count()
print(f"  Total students: {total_students} | Active: {active_students}")
print(f"  Total enrollments: {total_enrollments} | Active: {active_enrollments}")

# Students without active enrollment
unenrolled = db.query(Student).filter(Student.status == "ACTIVE").all()
unenrolled_students = []
for st in unenrolled:
    has_enr = db.query(StudentEnrollment).filter(
        StudentEnrollment.student_id == st.id,
        StudentEnrollment.status == "ACTIVE"
    ).first()
    if not has_enr:
        unenrolled_students.append(st)
print(f"  Active students without active enrollment: {len(unenrolled_students)}")

# =========================
# TEACHER ASSIGNMENTS
# =========================
print("\n[TEACHER ASSIGNMENTS]")
tas = db.query(TeacherAssignment).all()
active_tas = db.query(TeacherAssignment).filter(TeacherAssignment.status == "ACTIVE").all()
print(f"  Total: {len(tas)} | Active: {len(active_tas)}")

# Check assignments referencing non-existent classes or subjects
orphan_tas = []
for ta in tas:
    c = db.query(SchoolClass).filter(SchoolClass.id == ta.class_id).first()
    s = db.query(Subject).filter(Subject.id == ta.subject_id).first()
    t = db.query(Teacher).filter(Teacher.id == ta.teacher_id).first()
    if not c or not s or not t:
        orphan_tas.append({
            "id": ta.id, "teacher_id": ta.teacher_id, "class_id": ta.class_id,
            "subject_id": ta.subject_id, "year": ta.academic_year,
            "missing": ("class" if not c else "") + ("subject" if not s else "") + ("teacher" if not t else "")
        })

print(f"  Orphan assignments (missing class/subject/teacher): {len(orphan_tas)}")
for o in orphan_tas:
    print(f"    [{o['id']}] teacher={o['teacher_id']}, class={o['class_id']}, subject={o['subject_id']}, missing={o['missing']}")

# =========================
# EXAMS & SUBMISSIONS
# =========================
print("\n[EXAMS & RESULT SUBMISSIONS]")
total_exams = db.query(Exam).count()
total_submissions = db.query(ResultSubmission).count()
submitted = db.query(ResultSubmission).filter(ResultSubmission.status == "SUBMITTED").count()
approved = db.query(ResultSubmission).filter(ResultSubmission.status == "APPROVED").count()
released = db.query(ResultSubmission).filter(ResultSubmission.status == "RELEASED").count()
print(f"  Total exams: {total_exams}")
print(f"  Total submissions: {total_submissions} | Submitted: {submitted} | Approved: {approved} | Released: {released}")

db.close()

print("\n" + "=" * 60)
print("AUDIT COMPLETE")
print("=" * 60)
