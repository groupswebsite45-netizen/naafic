from app.core.tenant_provisioner import get_tenant_db_url
from sqlalchemy import create_engine, text

def get_db_schema(db_name):
    engine = create_engine(get_tenant_db_url(db_name))
    with engine.connect() as conn:
        tables = conn.execute(text(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        )).fetchall()
        schema = {}
        for (t,) in tables:
            cols = conn.execute(text(
                f"SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_schema = 'public' AND table_name = '{t}'"
            )).fetchall()
            schema[t] = {col: (dtype, nullable) for col, dtype, nullable in cols}
    return schema

hawl = get_db_schema("hawlwadaag_school_db")
gara = get_db_schema("somroyal_garasale_primary_school")

missing_tables = set(hawl.keys()) - set(gara.keys())
print("Tables in hawlwadaag but missing in garasale:", missing_tables)

for table in hawl:
    if table in gara:
        diff_cols = set(hawl[table].keys()) - set(gara[table].keys())
        if diff_cols:
            print(f"Columns in {table} in hawlwadaag but missing in garasale:", diff_cols)
