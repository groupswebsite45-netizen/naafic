from app.core.tenant_provisioner import get_server_db_url, get_tenant_db_url
from sqlalchemy import create_engine, text

server_url = get_server_db_url()
engine = create_engine(server_url)
with engine.connect() as conn:
    dbs = [r[0] for r in conn.execute(text("SELECT datname FROM pg_database WHERE datistemplate = false;")).fetchall()]
print("All databases:", dbs)

for db in dbs:
    if db in ["postgres"]:
        continue
    db_url = get_tenant_db_url(db)
    e = create_engine(db_url)
    try:
        with e.connect() as c:
            cols = [r[0] for r in c.execute(text(
                "SELECT column_name FROM information_schema.columns WHERE table_name = 'timetables'"
            )).fetchall()]
            tbls = [r[0] for r in c.execute(text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
            )).fetchall()]
            has_settings = 'timetable_settings' in tbls
            has_avail = 'teacher_availabilities' in tbls
            print(f"{db}: has_timetables={len(cols)>0}, period_number in cols={('period_number' in cols)}, timetable_settings={has_settings}, teacher_availabilities={has_avail}")
    except Exception as exc:
        print(f"{db}: error {exc}")
