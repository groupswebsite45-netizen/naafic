import sys, os
from pathlib import Path

BACKEND_DIR = Path("backend").resolve()
sys.path.insert(0, str(BACKEND_DIR))
from dotenv import load_dotenv
load_dotenv(BACKEND_DIR / ".env")

from app.core.database import engine
from sqlalchemy import text

with engine.begin() as conn:
    # Test updating class_id = 29 where class_id = 1
    # Check subjects in class 29 vs class 1
    c1_subjs = conn.execute(text("SELECT id, subject_id, teacher_id FROM teacher_assignments WHERE class_id = 1")).mappings().all()
    c29_subjs = conn.execute(text("SELECT id, subject_id, teacher_id FROM teacher_assignments WHERE class_id = 29")).mappings().all()
    print("Class 1 teacher assignments:")
    for r in c1_subjs:
        print(" ", dict(r))
    print("Class 29 teacher assignments:")
    for r in c29_subjs:
        print(" ", dict(r))
