import sys, os
from pathlib import Path
BACKEND_DIR = Path('backend').resolve()
sys.path.insert(0, str(BACKEND_DIR))
from dotenv import load_dotenv
load_dotenv(BACKEND_DIR / '.env')
from app.core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    print('Teacher assignments non-2026/2027:')
    for r in conn.execute(text("SELECT id, class_id, subject_id, teacher_id, academic_year FROM teacher_assignments WHERE academic_year != '2026/2027'")).mappings():
        print(dict(r))
    print('Classes non-2026/2027:')
    for r in conn.execute(text("SELECT id, name, academic_year FROM classes WHERE academic_year != '2026/2027'")).mappings():
        print(dict(r))
