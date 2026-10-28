import sys
sys.path.insert(0, ".")
from app.core.database import SessionLocal
from app.models.teacher import Teacher
from app.models.teacher_assignment import TeacherAssignment
from app.models.school_class import SchoolClass
from app.models.subject import Subject
from app.models.exam import Exam, ExamResult
from app.models.result_submission import ResultSubmission
from app.models.student_enrollment import StudentEnrollment
from app.models.student import Student

db = SessionLocal()

print("=" * 70)
print("AUDIT REPORT: DATA INTEGRITY & WORKFLOW ANOMALIES")
print("=" * 70)

# 1. Classes Analysis
print("\n--- 1. CLASSES AUDIT ---")
all_classes = db.query(SchoolClass).order_by(SchoolClass.academic_year, SchoolClass.name).all()
print(f"Total classes: {len(all_classes)}")

# Check duplicate classes by (academic_year normalized, division, level, section)
class_keys = {}
for c in all_classes:
    norm_year = c.academic_year.replace("-", "/")
    key = (norm_year, c.division.upper(), c.level.strip(), (c.section or "").strip())
    class_keys.setdefault(key, []).append(c)

for key, clist in class_keys.items():
    if len(clist) > 1:
        print(f"DUPLICATE CLASS FOUND for key {key}:")
        for c in clist:
            enr = db.query(StudentEnrollment).filter(StudentEnrollment.class_id == c.id).count()
            assigns = db.query(TeacherAssignment).filter(TeacherAssignment.class_id == c.id).count()
            exams = db.query(Exam).filter(Exam.class_id == c.id).count()
            print(f"   ID: {c.id}, Name: '{c.name}', Code: '{c.code}', Year: '{c.academic_year}', Enrolled: {enr}, Assigns: {assigns}, Exams: {exams}")

# 2. Teacher Assignments Audit
print("\n--- 2. TEACHER ASSIGNMENTS AUDIT ---")
all_assigns = db.query(TeacherAssignment).all()
print(f"Total assignments: {len(all_assigns)}")
orphan_assigns = []
for a in all_assigns:
    teacher = db.query(Teacher).filter(Teacher.id == a.teacher_id).first()
    school_class = db.query(SchoolClass).filter(SchoolClass.id == a.class_id).first()
    subject = db.query(Subject).filter(Subject.id == a.subject_id).first()
    if not teacher or not school_class or not subject:
        orphan_assigns.append((a, teacher, school_class, subject))
        print(f"ORPHAN ASSIGNMENT: ID {a.id}, Teacher: {teacher}, Class: {school_class}, Subject: {subject}")

# 3. Exams Audit
print("\n--- 3. EXAMS AUDIT ---")
all_exams = db.query(Exam).all()
print(f"Total exams: {len(all_exams)}")
for e in all_exams:
    teacher = db.query(Teacher).filter(Teacher.id == e.teacher_id).first() if e.teacher_id else None
    school_class = db.query(SchoolClass).filter(SchoolClass.id == e.class_id).first()
    subject = db.query(Subject).filter(Subject.id == e.subject_id).first()
    norm_year = e.academic_year.replace("-", "/")
    
    # Check if there is an active teacher assignment
    assign = None
    if teacher:
        assign = db.query(TeacherAssignment).filter(
            TeacherAssignment.teacher_id == teacher.id,
            TeacherAssignment.class_id == e.class_id,
            TeacherAssignment.subject_id == e.subject_id,
            TeacherAssignment.status == "ACTIVE"
        ).first()
    
    subs = db.query(ResultSubmission).filter(ResultSubmission.exam_id == e.id).all()
    results = db.query(ExamResult).filter(ExamResult.exam_id == e.id).all()
    
    has_issue = False
    reasons = []
    if not school_class:
        has_issue = True
        reasons.append("Orphan class_id")
    if not subject:
        has_issue = True
        reasons.append("Orphan subject_id")
    if not teacher:
        has_issue = True
        reasons.append("No teacher_id")
    elif not assign:
        reasons.append("No matching active TeacherAssignment")
        
    print(f"Exam ID {e.id:3d} | '{e.name}' | {e.academic_year} | Class: {school_class.name if school_class else 'NONE'} ({e.class_id}) | Subj: {subject.name if subject else 'NONE'} ({e.subject_id}) | Teacher: {teacher.full_name if teacher else 'NONE'} ({e.teacher_id}) | Assign Match: {'YES' if assign else 'NO'} | Subs: {len(subs)} | Results: {len(results)} | Flags: {', '.join(reasons) if reasons else 'OK'}")

# 4. Result Submissions Audit
print("\n--- 4. RESULT SUBMISSIONS AUDIT ---")
all_subs = db.query(ResultSubmission).all()
print(f"Total result submissions: {len(all_subs)}")
for s in all_subs:
    exam = db.query(Exam).filter(Exam.id == s.exam_id).first()
    teacher = db.query(Teacher).filter(Teacher.id == s.teacher_id).first()
    school_class = db.query(SchoolClass).filter(SchoolClass.id == s.class_id).first()
    subject = db.query(Subject).filter(Subject.id == s.subject_id).first()
    results = db.query(ExamResult).filter(ExamResult.submission_id == s.id).all()
    
    issues = []
    if not exam:
        issues.append("Orphan exam_id")
    if not teacher:
        issues.append("Orphan teacher_id")
    if not school_class:
        issues.append("Orphan class_id")
    if not subject:
        issues.append("Orphan subject_id")
    if exam and teacher and exam.teacher_id != teacher.id:
        issues.append(f"Teacher mismatch (Exam teacher {exam.teacher_id} vs Sub teacher {teacher.id})")
        
    print(f"Sub ID {s.id:3d} | Exam: {s.exam_name} ({s.exam_id}) | Status: {s.status:10s} | Class: {school_class.name if school_class else 'NONE'} ({s.class_id}) | Subj: {subject.name if subject else 'NONE'} ({s.subject_id}) | Teacher: {teacher.full_name if teacher else 'NONE'} ({s.teacher_id}) | Results: {len(results)} | Flags: {', '.join(issues) if issues else 'OK'}")

db.close()
