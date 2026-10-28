import sys
import os
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from sqlalchemy import text
from app.core.database import SessionLocal

def migrate():
    db = SessionLocal()
    try:
        print("Checking and adding columns to 'exams' table...")
        db.execute(text("""
            ALTER TABLE exams 
            ADD COLUMN IF NOT EXISTS teacher_id INTEGER REFERENCES teachers(id) ON DELETE SET NULL,
            ADD COLUMN IF NOT EXISTS instructions TEXT;
        """))
        
        # Link existing exams to assigned teacher if available
        db.execute(text("""
            UPDATE exams e
            SET teacher_id = ta.teacher_id
            FROM teacher_assignments ta
            WHERE e.class_id = ta.class_id 
              AND e.subject_id = ta.subject_id 
              AND e.teacher_id IS NULL
              AND ta.status = 'ACTIVE';
        """))

        # Consolidate any duplicate exams before creating constraint
        dupes = db.execute(text("""
            SELECT academic_year, class_id, subject_id, exam_type, name, array_agg(id ORDER BY id ASC) as ids
            FROM exams
            GROUP BY academic_year, class_id, subject_id, exam_type, name
            HAVING count(*) > 1
        """)).fetchall()

        for d in dupes:
            canonical_id = d.ids[0]
            redundant_ids = d.ids[1:]
            print(f"Consolidating duplicate exams for {d.name} ({d.academic_year}): keeping canonical ID {canonical_id}, removing {redundant_ids}")
            for r_id in redundant_ids:
                # Point results/submissions to canonical ID if any
                db.execute(text(f"UPDATE exam_results SET exam_id = {canonical_id} WHERE exam_id = {r_id}"))
                db.execute(text(f"UPDATE result_submissions SET exam_id = {canonical_id} WHERE exam_id = {r_id}"))
                db.execute(text(f"DELETE FROM exams WHERE id = {r_id}"))

        # Create unique constraint if not exists
        db.execute(text("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint WHERE conname = 'uq_exam_academic_year_class_subj_type_name'
                ) THEN
                    ALTER TABLE exams
                    ADD CONSTRAINT uq_exam_academic_year_class_subj_type_name 
                    UNIQUE (academic_year, class_id, subject_id, exam_type, name);
                END IF;
            END $$;
        """))

        db.commit()
        print("Successfully migrated 'exams' table.")
    except Exception as e:
        db.rollback()
        print(f"Migration error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
