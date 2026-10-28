import sys
sys.path.insert(0, ".")
import sqlalchemy
from app.core.config import settings

eng = sqlalchemy.create_engine(settings.DATABASE_URL)
with eng.begin() as c:
    c.execute(sqlalchemy.text("UPDATE system_settings SET value = 'Hawlwadaag Primary and Secondary School' WHERE key = 'school_name'"))
    c.execute(sqlalchemy.text("UPDATE system_settings SET value = 'Hawlwadaag School' WHERE key = 'school_short_name'"))
print("Updated system_settings in DB successfully!")
