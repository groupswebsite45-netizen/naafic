import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.core.database import SessionLocal
from sqlalchemy import text

s = SessionLocal()
print('Academic years in classes:', [r[0] for r in s.execute(text('SELECT DISTINCT academic_year FROM classes'))])
print('Classes count:', s.execute(text('SELECT COUNT(*) FROM classes')).scalar())
print('Teachers count:', s.execute(text('SELECT COUNT(*) FROM teachers')).scalar())
print('Subjects count:', s.execute(text('SELECT COUNT(*) FROM subjects')).scalar())
try:
    print('Timetable settings:', [dict(r._mapping) for r in s.execute(text('SELECT * FROM timetable_settings'))])
except Exception as e:
    print('Error reading timetable_settings:', e)
try:
    print('Timetable count:', s.execute(text('SELECT COUNT(*) FROM timetables')).scalar())
    print('Sample timetables:', [dict(r._mapping) for r in s.execute(text('SELECT * FROM timetables LIMIT 3'))])
except Exception as e:
    print('Error reading timetables:', e)
s.close()
