import sys, os
from pathlib import Path

BACKEND_DIR = Path("backend").resolve()
sys.path.insert(0, str(BACKEND_DIR))
from dotenv import load_dotenv
load_dotenv(BACKEND_DIR / ".env")

from app.core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    print("Checking old classes usage:")
    for cid in [1, 2, 8, 93] + list(range(50, 74)):
        se_cnt = conn.execute(text(f"SELECT count(*) FROM student_enrollments WHERE class_id = {cid}")).scalar()
        att_cnt = conn.execute(text(f"SELECT count(*) FROM attendances WHERE class_id = {cid}")).scalar()
        ex_cnt = conn.execute(text(f"SELECT count(*) FROM exams WHERE class_id = {cid}")).scalar()
        ta_cnt = conn.execute(text(f"SELECT count(*) FROM teacher_assignments WHERE class_id = {cid}")).scalar()
        tt_cnt = conn.execute(text(f"SELECT count(*) FROM timetables WHERE class_id = {cid}")).scalar()
        if any([se_cnt, att_cnt, ex_cnt, ta_cnt, tt_cnt]):
            print(f"Class {cid}: enrollments={se_cnt}, att={att_cnt}, exams={ex_cnt}, teach_assign={ta_cnt}, timetable={tt_cnt}")
