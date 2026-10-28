import psycopg2

try:
    conn = psycopg2.connect('postgresql://postgres:123@localhost:5432/hawlwadaag_school_db')
    cur = conn.cursor()
    cur.execute("""
        ALTER TABLE exams ADD COLUMN IF NOT EXISTS start_time VARCHAR(20);
        ALTER TABLE exams ADD COLUMN IF NOT EXISTS end_time VARCHAR(20);
        ALTER TABLE exams ADD COLUMN IF NOT EXISTS result_submission_deadline TIMESTAMP;
        ALTER TABLE exams ADD COLUMN IF NOT EXISTS created_by_id INTEGER;
        ALTER TABLE exams ADD COLUMN IF NOT EXISTS reopened_at TIMESTAMP;
        ALTER TABLE exams ADD COLUMN IF NOT EXISTS reopened_by_id INTEGER;
        ALTER TABLE exams ADD COLUMN IF NOT EXISTS reopen_reason TEXT;

        CREATE TABLE IF NOT EXISTS exam_deadline_extensions (
            id SERIAL PRIMARY KEY,
            exam_id INTEGER NOT NULL REFERENCES exams(id) ON DELETE CASCADE,
            previous_deadline TIMESTAMP,
            new_deadline TIMESTAMP NOT NULL,
            reason TEXT NOT NULL,
            extended_by_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()
    print("PostgreSQL hawlwadaag_school_db schema migrated successfully.")
except Exception as e:
    print("PostgreSQL migration notice:", e)
