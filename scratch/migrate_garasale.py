import sys
import os
sys.path.insert(0, os.path.abspath('.'))
import pymysql
import psycopg2
from sqlalchemy import create_engine
from app.core.database import Base
from app.models import *

# 1. Create all schema tables in PostgreSQL somroyal_garasale_primary_school using SQLAlchemy metadata
pg_url = 'postgresql+psycopg2://postgres:123@localhost:5432/somroyal_garasale_primary_school'
engine = create_engine(pg_url)
Base.metadata.create_all(bind=engine)
print('Base schema created in PostgreSQL somroyal_garasale_primary_school.')

# 2. Transfer data from MySQL to PostgreSQL for somroyal_garasale_primary_school
my_conn = pymysql.connect(host='localhost', user='root', password='', database='somroyal_garasale_primary_school', port=3306)
my_cur = my_conn.cursor()

pg_dsn = 'postgresql://postgres:123@localhost:5432/somroyal_garasale_primary_school'
pg_conn = psycopg2.connect(pg_dsn)
pg_cur = pg_conn.cursor()

# Get list of tables in MySQL
my_cur.execute('SHOW TABLES;')
tables = [r[0] for r in my_cur.fetchall()]

order = [
    'roles', 'users', 'user_roles', 'institutions', 'subscriptions', 'institution_payments',
    'system_settings', 'classes', 'subjects', 'teachers', 'students', 'student_enrollments',
    'teacher_assignments', 'timetables', 'exams', 'exam_results', 'fee_structures',
    'student_fees', 'fee_payments', 'notifications', 'notification_templates',
    'notification_deliveries', 'audit_logs'
]

for t in tables:
    if t not in order:
        order.append(t)

for tbl in order:
    if tbl not in tables:
        continue
    try:
        my_cur.execute(f"SELECT * FROM `{tbl}`;")
        rows = my_cur.fetchall()
        if not rows:
            continue
        
        my_cur.execute(f"SHOW COLUMNS FROM `{tbl}`;")
        cols = [c[0] for c in my_cur.fetchall()]
        
        # Get PG column data types
        pg_cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = %s;
        """, (tbl,))
        pg_type_map = {r[0]: r[1] for r in pg_cur.fetchall()}
        
        cols_str = ', '.join([f'"{c}"' for c in cols])
        placeholders = ', '.join(['%s'] * len(cols))
        insert_sql = f'INSERT INTO "{tbl}" ({cols_str}) VALUES ({placeholders}) ON CONFLICT DO NOTHING;'
        
        formatted_rows = []
        for r in rows:
            row_list = list(r)
            for idx, c in enumerate(cols):
                if c in pg_type_map and pg_type_map[c] == 'boolean':
                    if row_list[idx] is not None:
                        row_list[idx] = bool(row_list[idx])
            formatted_rows.append(row_list)
            
        pg_cur.executemany(insert_sql, formatted_rows)
        pg_conn.commit()
        print(f"Migrated table {tbl}: {len(rows)} rows.")
    except Exception as e:
        pg_conn.rollback()
        print(f"Warning migrating table {tbl}: {e}")

# Reset postgres sequences
for tbl in order:
    try:
        sql = f"SELECT setval(pg_get_serial_sequence('\"{tbl}\"', 'id'), coalesce(max(id), 1)) FROM \"{tbl}\";"
        pg_cur.execute(sql)
        pg_conn.commit()
    except Exception:
        pg_conn.rollback()

pg_conn.close()
my_conn.close()
print("Tenant migration completed successfully!")
