from app.core.tenant_provisioner import get_tenant_db_url
from sqlalchemy import create_engine, text

e = create_engine(get_tenant_db_url('somroyal_garasale_primary_school'))
with e.connect() as c:
    try:
        years = c.execute(text('SELECT DISTINCT academic_year FROM classes')).fetchall()
        print('Classes academic_year:', years)
    except Exception as exc:
        print('classes error:', exc)
    try:
        settings = c.execute(text("SELECT key, value FROM system_settings WHERE key LIKE '%year%'")).fetchall()
        print('system_settings:', settings)
    except Exception as exc:
        print('settings error:', exc)
    try:
        counts = c.execute(text("SELECT (SELECT count(*) FROM students) as students, (SELECT count(*) FROM teachers) as teachers, (SELECT count(*) FROM classes) as classes")).fetchall()
        print('counts:', counts)
    except Exception as exc:
        print('counts error:', exc)
