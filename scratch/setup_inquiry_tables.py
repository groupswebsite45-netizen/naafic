import sys
sys.path.insert(0, ".")
import sqlalchemy
from app.core.config import settings
from app.core.database import Base
from app.models.institution import Institution, Subscription, InstitutionPayment
from app.models.inquiry import Inquiry

eng_pg = sqlalchemy.create_engine(settings.DATABASE_URL)
print("Creating institutions, subscriptions, institution_payments, and inquiries tables in PostgreSQL if not exist...")
# Create only these specific tables if they don't exist
Institution.__table__.create(bind=eng_pg, checkfirst=True)
Subscription.__table__.create(bind=eng_pg, checkfirst=True)
InstitutionPayment.__table__.create(bind=eng_pg, checkfirst=True)
Inquiry.__table__.create(bind=eng_pg, checkfirst=True)
print("Tables created successfully in PostgreSQL!")

# Sync institutions, subscriptions, payments from MySQL if PG is currently empty
try:
    eng_my = sqlalchemy.create_engine('mysql+pymysql://root:@localhost:3306/sms')
    with eng_pg.connect() as pg_conn:
        cnt = pg_conn.execute(sqlalchemy.text("SELECT count(*) FROM institutions;")).scalar()
        if cnt == 0:
            print("Syncing existing institutions from MySQL...")
            with eng_my.connect() as my_conn:
                inst_rows = my_conn.execute(sqlalchemy.text("SELECT id, code, name, type, logo_url, contact_person, email, phone, region, city, address, status, database_name, provisioning_status, provisioning_error, admin_email, admin_username, subscription_plan, subscription_status, subscription_start_date, subscription_expiry_date, created_at, updated_at FROM institutions;")).fetchall()
                for r in inst_rows:
                    pg_conn.execute(sqlalchemy.text("""
                        INSERT INTO institutions (id, code, name, type, logo_url, contact_person, email, phone, region, city, address, status, database_name, provisioning_status, provisioning_error, admin_email, admin_username, subscription_plan, subscription_status, subscription_start_date, subscription_expiry_date, created_at, updated_at)
                        VALUES (:id, :code, :name, :type, :logo_url, :contact_person, :email, :phone, :region, :city, :address, :status, :database_name, :provisioning_status, :provisioning_error, :admin_email, :admin_username, :subscription_plan, :subscription_status, :subscription_start_date, :subscription_expiry_date, :created_at, :updated_at)
                    """), r._asdict())
                
                sub_rows = my_conn.execute(sqlalchemy.text("SELECT id, institution_id, plan_name, billing_cycle, price, setup_fee, status, start_date, end_date, auto_renew, notes, created_at, updated_at FROM subscriptions;")).fetchall()
                for r in sub_rows:
                    d = r._asdict()
                    d["auto_renew"] = bool(d["auto_renew"])
                    pg_conn.execute(sqlalchemy.text("""
                        INSERT INTO subscriptions (id, institution_id, plan_name, billing_cycle, price, setup_fee, status, start_date, end_date, auto_renew, notes, created_at, updated_at)
                        VALUES (:id, :institution_id, :plan_name, :billing_cycle, :price, :setup_fee, :status, :start_date, :end_date, :auto_renew, :notes, :created_at, :updated_at)
                    """), d)

                pmt_rows = my_conn.execute(sqlalchemy.text("SELECT id, institution_id, subscription_id, reference, amount, currency, payment_method, payment_date, status, invoice_number, notes, created_at FROM institution_payments;")).fetchall()
                for r in pmt_rows:
                    pg_conn.execute(sqlalchemy.text("""
                        INSERT INTO institution_payments (id, institution_id, subscription_id, reference, amount, currency, payment_method, payment_date, status, invoice_number, notes, created_at)
                        VALUES (:id, :institution_id, :subscription_id, :reference, :amount, :currency, :payment_method, :payment_date, :status, :invoice_number, :notes, :created_at)
                    """), r._asdict())
                pg_conn.commit()
                # reset sequences
                pg_conn.execute(sqlalchemy.text("SELECT setval(pg_get_serial_sequence('institutions', 'id'), coalesce(max(id), 1)) FROM institutions;"))
                pg_conn.execute(sqlalchemy.text("SELECT setval(pg_get_serial_sequence('subscriptions', 'id'), coalesce(max(id), 1)) FROM subscriptions;"))
                pg_conn.execute(sqlalchemy.text("SELECT setval(pg_get_serial_sequence('institution_payments', 'id'), coalesce(max(id), 1)) FROM institution_payments;"))
                pg_conn.commit()
            print("Institutions, subscriptions, and payments successfully synced to PostgreSQL!")
        else:
            print(f"PostgreSQL institutions table already has {cnt} rows.")
except Exception as e:
    print("Notice during sync:", e)
