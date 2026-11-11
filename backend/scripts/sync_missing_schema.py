import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import engine
from sqlalchemy import text

statements = [
    "ALTER TABLE classes ADD COLUMN IF NOT EXISTS division VARCHAR(20) DEFAULT 'PRIMARY';",
    "ALTER TABLE classes ADD COLUMN IF NOT EXISTS level VARCHAR(50);",
    "ALTER TABLE classes ALTER COLUMN section TYPE VARCHAR(50);",
    "CREATE INDEX IF NOT EXISTS ix_classes_division ON classes(division);",
    "CREATE INDEX IF NOT EXISTS ix_classes_level ON classes(level);",
    "CREATE INDEX IF NOT EXISTS ix_classes_section ON classes(section);",
    "ALTER TABLE subjects ADD COLUMN IF NOT EXISTS division VARCHAR(20) DEFAULT 'ALL';",
    "ALTER TABLE subjects ADD COLUMN IF NOT EXISTS applicable_levels VARCHAR(255);",
    "CREATE INDEX IF NOT EXISTS ix_subjects_division ON subjects(division);",
    "ALTER TABLE exams ADD COLUMN IF NOT EXISTS teacher_id INTEGER REFERENCES teachers(id) ON DELETE SET NULL;",
    "ALTER TABLE exams ADD COLUMN IF NOT EXISTS start_time VARCHAR(20);",
    "ALTER TABLE exams ADD COLUMN IF NOT EXISTS end_time VARCHAR(20);",
    "ALTER TABLE exams ADD COLUMN IF NOT EXISTS result_submission_deadline TIMESTAMP WITH TIME ZONE;",
    "ALTER TABLE exams ADD COLUMN IF NOT EXISTS created_by_id INTEGER REFERENCES users(id) ON DELETE SET NULL;",
    "ALTER TABLE exams ADD COLUMN IF NOT EXISTS reopened_at TIMESTAMP WITH TIME ZONE;",
    "ALTER TABLE exams ADD COLUMN IF NOT EXISTS reopened_by_id INTEGER REFERENCES users(id) ON DELETE SET NULL;",
    "ALTER TABLE exams ADD COLUMN IF NOT EXISTS reopen_reason TEXT;",
    "ALTER TABLE exams ADD COLUMN IF NOT EXISTS instructions TEXT;",
    "ALTER TABLE exams ALTER COLUMN status TYPE VARCHAR(30);",
    "ALTER TABLE exam_results ALTER COLUMN grade TYPE VARCHAR(20);"
]

with engine.begin() as conn:
    for stmt in statements:
        conn.execute(text(stmt))
print("Schema successfully synchronized!")
