"""
Safe Database Cleanup Script for Hawlwadaag SMS
================================================
Decisions:
1. Form 5-A, Form 6-A → mark INACTIVE (students preserved, admin re-enrolls)
2. Grade 7-12Subj → migrate unique students to Grade 7-A, then mark INACTIVE
3. Keep all school-used active subjects (Arabic, Computer, etc.), remove only test/generated
4. Merge 'math' [1] into 'Mathematics' [21]
5. Normalize subject codes for 7 core subjects
6. Mark all empty/test classes INACTIVE

SAFE: No student records are deleted. No real exam results are deleted.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date
from app.core.database import SessionLocal
from app.models.school_class import SchoolClass
from app.models.subject import Subject
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.models.teacher import Teacher
from app.models.teacher_assignment import TeacherAssignment
from app.models.exam import Exam, ExamResult
from app.models.result_submission import ResultSubmission

db = SessionLocal()

changes = []

def log_change(action, entity_type, entity_id, name, details=""):
    msg = f"[{action}] {entity_type} ID={entity_id} '{name}': {details}"
    changes.append(msg)
    print(msg)

print("=" * 70)
print("HAWLWADAAG SMS — SAFE DATABASE CLEANUP")
print("=" * 70)

# =============================================================================
# STEP 1: Mark test/temp classes INACTIVE
# =============================================================================
print("\n[STEP 1] Marking test classes as INACTIVE...")

TEST_CLASS_IDS = [178, 175, 176]  # Grade 9-Test-CF, Grade 7-Test, Grade 8-Test
for cid in TEST_CLASS_IDS:
    c = db.query(SchoolClass).filter(SchoolClass.id == cid).first()
    if c and c.status != "INACTIVE":
        old_status = c.status
        c.status = "INACTIVE"
        log_change("DEACTIVATED", "Class", c.id, c.name, f"was {old_status}, 0 students, test class")

# =============================================================================
# STEP 2: Mark Form 5-A, Form 6-A INACTIVE (out-of-spec secondary classes)
# =============================================================================
print("\n[STEP 2] Marking Form 5-A, Form 6-A as INACTIVE (out-of-spec)...")

OUT_OF_SPEC_CLASS_IDS = [59, 60]  # Form 5-A, Form 6-A
for cid in OUT_OF_SPEC_CLASS_IDS:
    c = db.query(SchoolClass).filter(SchoolClass.id == cid).first()
    if c and c.status != "INACTIVE":
        student_count = db.query(StudentEnrollment).filter(
            StudentEnrollment.class_id == cid,
            StudentEnrollment.status == "ACTIVE"
        ).count()
        c.status = "INACTIVE"
        log_change("DEACTIVATED", "Class", c.id, c.name, 
                   f"out-of-spec (Form 5/6 not in Secondary spec). {student_count} students preserved, admin must re-enroll.")

# =============================================================================
# STEP 3: Handle Grade 7-12Subj [177] — migrate unique students to Grade 7-A [147]
# =============================================================================
print("\n[STEP 3] Handling Grade 7-12Subj [177] — migrating unique students to Grade 7-A [147]...")

SRC_CLASS_ID = 177  # Grade 7-12Subj (dev test class)
DST_CLASS_ID = 147  # Grade 7 - A (real class)
DST_YEAR = "2026/2027"

src_class = db.query(SchoolClass).filter(SchoolClass.id == SRC_CLASS_ID).first()
dst_class = db.query(SchoolClass).filter(SchoolClass.id == DST_CLASS_ID).first()

if src_class and dst_class:
    # Get all students enrolled in the source class
    src_enrollments = db.query(StudentEnrollment).filter(
        StudentEnrollment.class_id == SRC_CLASS_ID,
        StudentEnrollment.status == "ACTIVE"
    ).all()
    
    migrated = 0
    skipped = 0
    
    for enr in src_enrollments:
        # Check if this student is already enrolled in Grade 7-A for same year
        already_in_dst = db.query(StudentEnrollment).filter(
            StudentEnrollment.student_id == enr.student_id,
            StudentEnrollment.class_id == DST_CLASS_ID,
            StudentEnrollment.status == "ACTIVE"
        ).first()
        
        if already_in_dst:
            # Already enrolled in real class — just mark this enrollment as TRANSFERRED
            enr.status = "TRANSFERRED"
            enr.end_date = date.today()
            skipped += 1
            print(f"  Student {enr.student_id} already in Grade 7-A — marking src enrollment TRANSFERRED")
        else:
            # Check if student has any other active enrollment for this year
            other_active = db.query(StudentEnrollment).filter(
                StudentEnrollment.student_id == enr.student_id,
                StudentEnrollment.academic_year == DST_YEAR,
                StudentEnrollment.status == "ACTIVE",
                StudentEnrollment.class_id != SRC_CLASS_ID
            ).first()
            
            if other_active:
                # Has enrollment in another real class — just transfer away from src
                enr.status = "TRANSFERRED"
                enr.end_date = date.today()
                skipped += 1
                print(f"  Student {enr.student_id} enrolled elsewhere in {DST_YEAR} — marking src TRANSFERRED")
            else:
                # Unique to this test class — move to Grade 7-A
                enr.class_id = DST_CLASS_ID
                enr.academic_year = DST_YEAR
                migrated += 1
                print(f"  Student {enr.student_id} migrated from Grade 7-12Subj → Grade 7-A")
    
    log_change("MIGRATED", "Class", SRC_CLASS_ID, src_class.name,
               f"migrated={migrated} students to Grade 7-A, skipped={skipped} (already enrolled elsewhere)")
    
    # Delete orphan teacher assignments for this test class
    orphan_tas = db.query(TeacherAssignment).filter(
        TeacherAssignment.class_id == SRC_CLASS_ID
    ).all()
    
    for ta in orphan_tas:
        print(f"  Deleting TA ID={ta.id} (teacher={ta.teacher_id}, subject={ta.subject_id}) from test class")
        db.delete(ta)
    
    log_change("DELETED_TAs", "Class", SRC_CLASS_ID, src_class.name,
               f"removed {len(orphan_tas)} teacher assignments from test class")
    
    # Mark source class INACTIVE
    src_class.status = "INACTIVE"
    log_change("DEACTIVATED", "Class", SRC_CLASS_ID, src_class.name, 
               "dev/test duplicate of Grade 7-A, all students migrated")

# =============================================================================
# STEP 4: Handle Grade 7 [179] (malformed — no section) 
# =============================================================================
print("\n[STEP 4] Handling Grade 7 [179] (malformed class, no section)...")

MALFORMED_CLASS_ID = 179  # 'Grade 7' with no section
mal_class = db.query(SchoolClass).filter(SchoolClass.id == MALFORMED_CLASS_ID).first()

if mal_class:
    mal_students = db.query(StudentEnrollment).filter(
        StudentEnrollment.class_id == MALFORMED_CLASS_ID,
        StudentEnrollment.status == "ACTIVE"
    ).all()
    
    migrated = 0
    for enr in mal_students:
        # Try to move to Grade 7-A [147]
        already_in_dst = db.query(StudentEnrollment).filter(
            StudentEnrollment.student_id == enr.student_id,
            StudentEnrollment.class_id == DST_CLASS_ID,
            StudentEnrollment.status == "ACTIVE"
        ).first()
        
        if already_in_dst:
            enr.status = "TRANSFERRED"
            enr.end_date = date.today()
        else:
            # Check if student already has an enrollment for this academic year (different class)
            year_conflict = db.query(StudentEnrollment).filter(
                StudentEnrollment.student_id == enr.student_id,
                StudentEnrollment.academic_year == DST_YEAR,
                StudentEnrollment.status == "ACTIVE",
                StudentEnrollment.class_id != MALFORMED_CLASS_ID
            ).first()
            
            if year_conflict:
                # Student already enrolled somewhere for this year, just mark this one TRANSFERRED
                enr.status = "TRANSFERRED"
                enr.end_date = date.today()
                print(f"  Student {enr.student_id} already enrolled in class {year_conflict.class_id} for {DST_YEAR} - marking malformed enrollment TRANSFERRED")
            else:
                enr.class_id = DST_CLASS_ID
                enr.academic_year = DST_YEAR
                migrated += 1
                print(f"  Student {enr.student_id} migrated from Grade 7 (no section) -> Grade 7-A")
    
    # Delete teacher assignments
    mal_tas = db.query(TeacherAssignment).filter(TeacherAssignment.class_id == MALFORMED_CLASS_ID).all()
    for ta in mal_tas:
        print(f"  Deleting TA ID={ta.id} from malformed Grade 7")
        db.delete(ta)
    
    mal_class.status = "INACTIVE"
    log_change("DEACTIVATED", "Class", MALFORMED_CLASS_ID, mal_class.name,
               f"malformed (no section), {migrated} students migrated to Grade 7-A")

# =============================================================================
# STEP 5: Mark all empty old-year classes INACTIVE
# =============================================================================
print("\n[STEP 5] Marking empty old-year/current-year classes INACTIVE...")

EMPTY_CLASS_IDS = [180, 26, 27, 28, 30, 173, 35, 36, 161, 146, 159]

for cid in EMPTY_CLASS_IDS:
    c = db.query(SchoolClass).filter(SchoolClass.id == cid).first()
    if not c:
        continue
    
    # Double-check: confirm still 0 active students
    active_students = db.query(StudentEnrollment).filter(
        StudentEnrollment.class_id == cid,
        StudentEnrollment.status == "ACTIVE"
    ).count()
    
    if active_students > 0:
        print(f"  SKIP: Class [{cid}] {c.name!r} now has {active_students} students (from migration). Not marking inactive.")
        continue
    
    ta_count = db.query(TeacherAssignment).filter(TeacherAssignment.class_id == cid).count()
    
    if c.status != "INACTIVE":
        c.status = "INACTIVE"
        log_change("DEACTIVATED", "Class", c.id, c.name,
                   f"0 active students, {ta_count} TAs, year={c.academic_year}")

# =============================================================================
# STEP 6: Mark 'math' [1] INACTIVE and migrate assignments/exams to Mathematics [21]
# =============================================================================
print("\n[STEP 6] Merging 'math' [1] into 'Mathematics' [21]...")

MATH_OLD_ID = 1   # 'math' code=MAT-101
MATH_NEW_ID = 21  # 'Mathematics' code=MATH-101

old_math = db.query(Subject).filter(Subject.id == MATH_OLD_ID).first()
new_math = db.query(Subject).filter(Subject.id == MATH_NEW_ID).first()

if old_math and new_math:
    # Migrate teacher assignments
    old_tas = db.query(TeacherAssignment).filter(TeacherAssignment.subject_id == MATH_OLD_ID).all()
    for ta in old_tas:
        # Check if duplicate would be created
        dup = db.query(TeacherAssignment).filter(
            TeacherAssignment.teacher_id == ta.teacher_id,
            TeacherAssignment.class_id == ta.class_id,
            TeacherAssignment.subject_id == MATH_NEW_ID,
            TeacherAssignment.academic_year == ta.academic_year
        ).first()
        
        if dup:
            print(f"  TA {ta.id}: duplicate would exist, deleting old TA")
            db.delete(ta)
        else:
            ta.subject_id = MATH_NEW_ID
            print(f"  TA {ta.id}: migrated from math→Mathematics")
    
    # Migrate exams
    old_exams = db.query(Exam).filter(Exam.subject_id == MATH_OLD_ID).all()
    for ex in old_exams:
        ex.subject_id = MATH_NEW_ID
        print(f"  Exam {ex.id} '{ex.name}': migrated from math→Mathematics")
    
    # Migrate exam results
    old_results = db.query(ExamResult).filter(ExamResult.subject_id == MATH_OLD_ID).all()
    for r in old_results:
        r.subject_id = MATH_NEW_ID
    
    # Migrate result submissions
    old_subs = db.query(ResultSubmission).filter(ResultSubmission.subject_id == MATH_OLD_ID).all()
    for s in old_subs:
        s.subject_id = MATH_NEW_ID
    
    old_math.status = "INACTIVE"
    log_change("MERGED", "Subject", MATH_OLD_ID, "'math'",
               f"migrated {len(old_tas)} TAs, {len(old_exams)} exams into Mathematics [21], then marked INACTIVE")

# =============================================================================
# STEP 7: Mark test/generated subjects INACTIVE
# =============================================================================
print("\n[STEP 7] Marking test/generated subjects INACTIVE...")

# These are safe to mark INACTIVE — all already INACTIVE except the ones below
TEST_SUBJECT_PATTERNS_NAMES = [
    "advanced astronomy",
    "general science sci",
    "g9-",
    "mathematics-test",
    "physics-test", 
    "advanced physics laboratory",
    "somali literature 527b23",
    "integrated science",
]
TEST_SUBJECT_PATTERNS_CODES = [
    "sub-", "g9-s", "math-tst", "phys-tst", "test-sub", "som-527b23", "sci-101"
]

subjects = db.query(Subject).all()
marked_inactive = 0

for s in subjects:
    name_lower = (s.name or "").lower()
    code_lower = (s.code or "").lower()
    
    is_test = (
        any(p in name_lower for p in TEST_SUBJECT_PATTERNS_NAMES) or
        any(p in code_lower for p in TEST_SUBJECT_PATTERNS_CODES)
    )
    
    if is_test and s.status == "ACTIVE":
        # Double-check no real exams with submitted/released results
        has_real_results = db.query(ExamResult).join(Exam).filter(
            Exam.subject_id == s.id,
            ExamResult.status.in_(["SUBMITTED", "APPROVED", "RELEASED"])
        ).first()
        
        if has_real_results:
            print(f"  SKIP: Subject [{s.id}] {s.name!r} has submitted/released results — keeping ACTIVE")
            continue
        
        s.status = "INACTIVE"
        marked_inactive += 1
        log_change("DEACTIVATED", "Subject", s.id, s.name, "test/generated subject")

print(f"  Total test subjects marked INACTIVE: {marked_inactive}")

# =============================================================================
# STEP 8: Normalize codes for the 7 core subjects
# =============================================================================
print("\n[STEP 8] Normalizing subject codes for 7 core subjects...")

CODE_UPDATES = [
    (58, "ISL-101"),   # Islamic Studies: ISL-12S → ISL-101
    (26, "PHY-101"),   # Physics: PHY-201 → PHY-101
    (27, "CHE-101"),   # Chemistry: CHEM-201 → CHE-101
    (28, "BIO-101"),   # Biology: BIO-201 → BIO-101
]

for subj_id, new_code in CODE_UPDATES:
    s = db.query(Subject).filter(Subject.id == subj_id).first()
    if s and s.code != new_code:
        old_code = s.code
        # Check no conflict
        conflict = db.query(Subject).filter(Subject.code == new_code, Subject.id != subj_id).first()
        if conflict:
            print(f"  SKIP: Code {new_code} already used by {conflict.name} [{conflict.id}]")
            continue
        s.code = new_code
        log_change("CODE_UPDATED", "Subject", s.id, s.name, f"{old_code} → {new_code}")

# =============================================================================
# STEP 9: Set subject divisions correctly
# =============================================================================
print("\n[STEP 9] Ensuring subject divisions are correct...")

# Core subjects that apply to ALL levels
ALL_DIVISION_SUBJECT_IDS = [21, 23, 22, 58]  # Mathematics, English Language, Somali, Islamic Studies
for sid in ALL_DIVISION_SUBJECT_IDS:
    s = db.query(Subject).filter(Subject.id == sid).first()
    if s and s.division != "ALL":
        old_div = s.division
        s.division = "ALL"
        log_change("DIVISION_FIXED", "Subject", s.id, s.name, f"{old_div} → ALL")

# Secondary-only subjects
SECONDARY_SUBJECT_IDS = [26, 27, 28]  # Physics, Chemistry, Biology
for sid in SECONDARY_SUBJECT_IDS:
    s = db.query(Subject).filter(Subject.id == sid).first()
    if s and s.division != "SECONDARY":
        old_div = s.division
        s.division = "SECONDARY"
        log_change("DIVISION_FIXED", "Subject", s.id, s.name, f"{old_div} → SECONDARY")

# =============================================================================
# COMMIT ALL CHANGES
# =============================================================================
print("\n[COMMITTING ALL CHANGES TO POSTGRESQL...]")
try:
    db.commit()
    print("✅ All changes committed successfully.")
except Exception as e:
    db.rollback()
    print(f"❌ ROLLBACK: Error during commit: {e}")
    raise

# =============================================================================
# FINAL VERIFICATION
# =============================================================================
print("\n" + "=" * 70)
print("POST-CLEANUP VERIFICATION")
print("=" * 70)

active_classes = db.query(SchoolClass).filter(SchoolClass.status == "ACTIVE").all()
print(f"\nActive classes after cleanup: {len(active_classes)}")
for c in sorted(active_classes, key=lambda x: (x.academic_year, x.division, x.level, x.section or "")):
    active_students = db.query(StudentEnrollment).filter(
        StudentEnrollment.class_id == c.id,
        StudentEnrollment.status == "ACTIVE"
    ).count()
    print(f"  [{c.id}] {c.name!r} | div={c.division} | year={c.academic_year} | students={active_students}")

active_subjects = db.query(Subject).filter(Subject.status == "ACTIVE").all()
print(f"\nActive subjects after cleanup: {len(active_subjects)}")
for s in sorted(active_subjects, key=lambda x: x.name):
    print(f"  [{s.id}] {s.name!r} | code={s.code} | div={s.division}")

db.close()

print("\n" + "=" * 70)
print(f"CLEANUP COMPLETE — {len(changes)} changes made")
print("=" * 70)
print("\nChanges made:")
for c in changes:
    print(f"  {c}")
