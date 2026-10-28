from app.core.tenant_provisioner import get_tenant_db_url
from sqlalchemy import create_engine, text

e = create_engine(get_tenant_db_url('somroyal_garasale_primary_school'))
with e.connect() as c:
    classes_cols = [r[0] for r in c.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='classes'")).fetchall()]
    print('classes columns:', classes_cols)
    classes = c.execute(text('SELECT id, name, section, academic_year, level FROM classes')).fetchall()
    print('Classes:', classes)
    subjects = c.execute(text('SELECT id, name, code FROM subjects')).fetchall()
    print('Subjects:', subjects)
    teachers = c.execute(text('SELECT id, full_name, email FROM teachers')).fetchall()
    print('Teachers:', teachers)
    ts = c.execute(text('SELECT id, teacher_id, subject_id, class_id FROM teacher_subjects')).fetchall()
    print('Teacher-Subjects:', ts)
    settings = c.execute(text('SELECT id, academic_year, periods_per_day, school_days FROM timetable_settings')).fetchall()
    print('Timetable settings:', settings)
