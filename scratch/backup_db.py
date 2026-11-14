import os, subprocess
from datetime import datetime

os.makedirs("backend/backups", exist_ok=True)
backup_file = os.path.abspath(f"backend/backups/sms_backup_before_ay_cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql")
print("Creating backup at:", backup_file)

env = os.environ.copy()
env["PGPASSWORD"] = "123"
pg_dump = r"D:\Program Files\PostgreSQL\18\bin\pg_dump.exe"

cmd = [pg_dump, "-h", "localhost", "-p", "5432", "-U", "postgres", "-d", "sms", "-f", backup_file]
res = subprocess.run(cmd, env=env, capture_output=True, text=True)
if res.returncode == 0:
    print("Backup SUCCESS! File size:", os.path.getsize(backup_file), "bytes")
else:
    print("Backup FAILED:", res.stderr)
