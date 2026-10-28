"""
Authoritative Database Normalization and Migration Script for Hawlwadaag School Exam & Result System.
Safely cleans test data, normalizes academic years, cleans assignments, and enforces database uniqueness.
"""

import sys
import os
from sqlalchemy import text

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, engine


def run_migration():
    db = SessionLocal()
    print("=== STARTING EXAM & RESULT SYSTEM NORMALIZATION ===")

    try:
        # 1. Clean up student enrollments attached to test classes first
        print("1. Purging student enrollments attached to test classes...")
        with engine.begin() as conn:
            conn.execute(text("""
                DELETE FROM student_enrollments 
                WHERE class_id IN (193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 211, 212, 213);
            """))

            # If student has duplicate enrollment in 2026-2027 when 2026/2027 already exists, delete the 2026-2027 one
            conn.execute(text("""
                DELETE FROM student_enrollments e1
                WHERE e1.academic_year IN ('2026-2027', '2026_2027')
                  AND EXISTS (
                      SELECT 1 FROM student_enrollments e2 
                      WHERE e2.student_id = e1.student_id 
                        AND e2.academic_year = '2026/2027'
                  );
            """))

        # 2. Normalize Academic Years across all tables
        print("2. Normalizing Academic Years to canonical '2026/2027'...")
        with engine.begin() as conn:
            conn.execute(text("UPDATE classes SET academic_year = '2026/2027' WHERE academic_year IN ('2026-2027', '2026_2027');"))
            conn.execute(text("UPDATE exams SET academic_year = '2026/2027' WHERE academic_year IN ('2026-2027', '2026_2027');"))
            conn.execute(text("UPDATE teacher_assignments SET academic_year = '2026/2027' WHERE academic_year IN ('2026-2027', '2026_2027');"))
            conn.execute(text("UPDATE student_enrollments SET academic_year = '2026/2027' WHERE academic_year IN ('2026-2027', '2026_2027');"))
            conn.execute(text("UPDATE result_submissions SET academic_year = '2026/2027' WHERE academic_year IN ('2026-2027', '2026_2027');"))
            conn.execute(text("UPDATE result_release_batches SET academic_year = '2026/2027' WHERE academic_year IN ('2026-2027', '2026_2027');"))
            conn.execute(text("UPDATE system_settings SET value = '2026/2027' WHERE key = 'academic_year_current';"))

        # 3. Archive / Deactivate test classes and remove test assignments
        print("3. Archiving test classes and de-duplicating teacher assignments...")
        with engine.begin() as conn:
            # Set test classes to INACTIVE
            conn.execute(text("""
                UPDATE classes 
                SET status = 'INACTIVE' 
                WHERE id IN (193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 211, 212, 213)
                   OR name LIKE '%Test%' 
                   OR name LIKE '%CONF-%' 
                   OR name LIKE '%DELTA%';
            """))

            # Remove test / duplicate teacher assignments from Class 147 (Grade 7 - A)
            conn.execute(text("""
                DELETE FROM teacher_assignments 
                WHERE class_id = 147 
                  AND subject_id IN (54, 55, 56, 57, 58, 59, 60, 61, 30);
            """))

            # Remove duplicate assignment for Mathematics on Class 147
            conn.execute(text("""
                DELETE FROM teacher_assignments 
                WHERE class_id = 147 
                  AND subject_id = 21 
                  AND teacher_id IN (29, 40);
            """))

            # Activate Integrated Science subject (ID 25)
            conn.execute(text("UPDATE subjects SET status = 'ACTIVE' WHERE id = 25;"))

            # Ensure canonical 5 core assignments for Grade 7 - A (Class 147)
            core_g7_assignments = [
                (18, 147, 21),  # Ahmed Hassan Ali -> Mathematics
                (19, 147, 23),  # Fadumo Mohamed Warsame -> English Language
                (19, 147, 22),  # Fadumo Mohamed Warsame -> Somali Language & Literature
                (20, 147, 24),  # Sheikh Omar Abdirahman -> Arabic & Islamic Studies
                (21, 147, 25),  # Khadija Osman Guled -> Integrated Science
            ]
            for tch_id, cls_id, subj_id in core_g7_assignments:
                res = conn.execute(text(f"""
                    SELECT id FROM teacher_assignments 
                    WHERE teacher_id = {tch_id} AND class_id = {cls_id} AND subject_id = {subj_id} AND academic_year = '2026/2027';
                """)).first()
                if not res:
                    conn.execute(text(f"""
                        INSERT INTO teacher_assignments (teacher_id, class_id, subject_id, academic_year, status, created_at, updated_at)
                        VALUES ({tch_id}, {cls_id}, {subj_id}, '2026/2027', 'ACTIVE', NOW(), NOW());
                    """))
                else:
                    conn.execute(text(f"UPDATE teacher_assignments SET status = 'ACTIVE' WHERE id = {res[0]};"))

        # 4. Clean up test / randomly generated exams from development testing
        print("4. Safely purging generated test exams and duplicates...")
        with engine.begin() as conn:
            # Delete exam results and submissions attached to test classes
            conn.execute(text("""
                DELETE FROM exam_results 
                WHERE exam_id IN (SELECT id FROM exams WHERE class_id IN (193, 194, 195, 196, 197, 198, 199, 200, 207, 208, 209, 211, 212, 213));
            """))
            conn.execute(text("""
                DELETE FROM result_submissions 
                WHERE exam_id IN (SELECT id FROM exams WHERE class_id IN (193, 194, 195, 196, 197, 198, 199, 200, 207, 208, 209, 211, 212, 213));
            """))
            conn.execute(text("""
                DELETE FROM exams 
                WHERE class_id IN (193, 194, 195, 196, 197, 198, 199, 200, 207, 208, 209, 211, 212, 213);
            """))

            # Normalize non-standard exam types (e.g. 'Mid-Term', 'mid_term' -> 'MID_TERM', 'Final' -> 'FINAL', etc.)
            conn.execute(text("UPDATE exams SET exam_type = 'MID_TERM' WHERE exam_type IN ('Mid-Term', 'Mid-Term Exam', 'MID_TERM', 'Midterm');"))
            conn.execute(text("UPDATE exams SET exam_type = 'FINAL' WHERE exam_type IN ('Final', 'Final Examination', 'FINAL', 'Finals');"))
            conn.execute(text("UPDATE exams SET exam_type = 'MONTHLY' WHERE exam_type IN ('Monthly', 'Monthly Test', 'MONTHLY');"))
            conn.execute(text("UPDATE exams SET exam_type = 'QUIZ' WHERE exam_type IN ('Quiz', 'QUIZ');"))

            # Delete any exams with invalid types if any exist
            conn.execute(text("DELETE FROM exam_results WHERE exam_id IN (SELECT id FROM exams WHERE exam_type NOT IN ('MID_TERM', 'FINAL', 'MONTHLY', 'QUIZ'));"))
            conn.execute(text("DELETE FROM result_submissions WHERE exam_id IN (SELECT id FROM exams WHERE exam_type NOT IN ('MID_TERM', 'FINAL', 'MONTHLY', 'QUIZ'));"))
            conn.execute(text("DELETE FROM exams WHERE exam_type NOT IN ('MID_TERM', 'FINAL', 'MONTHLY', 'QUIZ');"))

            # Remove test exams on Class 147 and 32 that were created during rapid testing with random hex hashes
            conn.execute(text("""
                DELETE FROM exam_results 
                WHERE exam_id IN (
                    SELECT id FROM exams 
                    WHERE name ~ '[0-9a-f]{6}' 
                       OR name LIKE '%Test%' 
                       OR name LIKE '%Recall%' 
                       OR name LIKE '%Workflow%' 
                       OR name LIKE '%Return%'
                );
            """))
            conn.execute(text("""
                DELETE FROM result_submissions 
                WHERE exam_id IN (
                    SELECT id FROM exams 
                    WHERE name ~ '[0-9a-f]{6}' 
                       OR name LIKE '%Test%' 
                       OR name LIKE '%Recall%' 
                       OR name LIKE '%Workflow%' 
                       OR name LIKE '%Return%'
                );
            """))
            conn.execute(text("""
                DELETE FROM exams 
                WHERE name ~ '[0-9a-f]{6}' 
                   OR name LIKE '%Test%' 
                   OR name LIKE '%Recall%' 
                   OR name LIKE '%Workflow%' 
                   OR name LIKE '%Return%';
            """))

            # Deduplicate any remaining exams for same (academic_year, class_id, subject_id, exam_type)
            # Keep the lowest ID
            conn.execute(text("""
                DELETE FROM exam_results 
                WHERE exam_id IN (
                    SELECT e1.id FROM exams e1
                    JOIN exams e2 ON e1.academic_year = e2.academic_year
                                 AND e1.class_id = e2.class_id
                                 AND e1.subject_id = e2.subject_id
                                 AND e1.exam_type = e2.exam_type
                                 AND e1.id > e2.id
                );
            """))
            conn.execute(text("""
                DELETE FROM result_submissions 
                WHERE exam_id IN (
                    SELECT e1.id FROM exams e1
                    JOIN exams e2 ON e1.academic_year = e2.academic_year
                                 AND e1.class_id = e2.class_id
                                 AND e1.subject_id = e2.subject_id
                                 AND e1.exam_type = e2.exam_type
                                 AND e1.id > e2.id
                );
            """))
            conn.execute(text("""
                DELETE FROM exams e1
                USING exams e2
                WHERE e1.academic_year = e2.academic_year
                  AND e1.class_id = e2.class_id
                  AND e1.subject_id = e2.subject_id
                  AND e1.exam_type = e2.exam_type
                  AND e1.id > e2.id;
            """))

        # 5. Enforce strict database uniqueness constraint
        print("5. Applying authoritative unique constraint on exams table...")
        with engine.begin() as conn:
            # Drop old constraint if exists
            conn.execute(text("ALTER TABLE exams DROP CONSTRAINT IF EXISTS uq_exam_academic_year_class_subj_type_name;"))
            conn.execute(text("ALTER TABLE exams DROP CONSTRAINT IF EXISTS uq_exam_academic_year_class_subj_type;"))
            # Add new authoritative constraint
            conn.execute(text("""
                ALTER TABLE exams 
                ADD CONSTRAINT uq_exam_academic_year_class_subj_type 
                UNIQUE (academic_year, class_id, subject_id, exam_type);
            """))

        print("=== NORMALIZATION AND MIGRATION COMPLETED SUCCESSFULLY ===")

    except Exception as e:
        print(f"ERROR during migration: {e}")
        db.rollback()
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    run_migration()
