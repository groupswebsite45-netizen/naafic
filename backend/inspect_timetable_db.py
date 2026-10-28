from sqlalchemy import create_engine, text
from app.core.config import settings

url = settings.DATABASE_URL
for db_name in ['hawlwadaag_school_db', 'somroyal_garasale_primary_school']:
    print(f'=== DB: {db_name} ===')
    try:
        tenant_url = url.rsplit('/', 1)[0] + '/' + db_name
        t_engine = create_engine(tenant_url)
        with t_engine.connect() as conn:
            classes = conn.execute(text('SELECT id, name, academic_year, status FROM classes LIMIT 10')).fetchall()
            print('Classes:', classes)
            academic_years = conn.execute(text('SELECT DISTINCT academic_year FROM classes')).fetchall()
            print('Distinct Class Academic Years:', academic_years)
            
            # Check timetables
            tt_count = conn.execute(text('SELECT COUNT(*) FROM timetables')).scalar()
            print('Timetable count:', tt_count)
            if tt_count > 0:
                tt_sample = conn.execute(text('SELECT id, class_id, subject_id, teacher_id, academic_year, day_of_week, start_time, end_time, status FROM timetables LIMIT 10')).fetchall()
                print('Timetable sample:', tt_sample)
                tt_years = conn.execute(text('SELECT DISTINCT academic_year FROM timetables')).fetchall()
                print('Timetable years:', tt_years)

            # Check teacher_assignments
            has_ta = conn.execute(text("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'teacher_assignments')")).scalar()
            print('Has teacher_assignments:', has_ta)
            if has_ta:
                ta_count = conn.execute(text('SELECT COUNT(*) FROM teacher_assignments')).scalar()
                print('Teacher assignments count:', ta_count)
                ta_sample = conn.execute(text('SELECT id, teacher_id, class_id, subject_id, academic_year, status FROM teacher_assignments LIMIT 10')).fetchall()
                print('Teacher assignments sample:', ta_sample)
                ta_years = conn.execute(text('SELECT DISTINCT academic_year FROM teacher_assignments')).fetchall()
                print('Teacher assignments years:', ta_years)

            # Check subjects
            sub_count = conn.execute(text('SELECT COUNT(*) FROM subjects')).scalar()
            print('Subjects count:', sub_count)

            # Check teachers
            teach_count = conn.execute(text('SELECT COUNT(*) FROM teachers')).scalar()
            print('Teachers count:', teach_count)

            # Check system_settings
            has_ss = conn.execute(text("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'system_settings')")).scalar()
            print('Has system_settings table:', has_ss)
            if has_ss:
                settings_rows = conn.execute(text("SELECT key, value FROM system_settings")).fetchall()
                print('System settings:', settings_rows)

    except Exception as e:
        print('Error:', e)
