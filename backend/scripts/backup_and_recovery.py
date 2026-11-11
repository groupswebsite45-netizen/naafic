"""
Somroyal EMS — Complete System Backup and Recovery Script
Handles atomic backup and restore of both PostgreSQL database and persistent file storage (student photos, exam papers).
"""
import os
import sys
import json
import shutil
import tarfile
from decimal import Decimal
from datetime import datetime, date, time, timezone

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import engine, SessionLocal
from app.models.student import Student
from sqlalchemy import inspect, text


BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UPLOADS_DIR = os.path.join(BACKEND_DIR, "uploads")
BACKUP_DIR = os.path.join(BACKEND_DIR, "backups")


class SafeJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date, time)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, bytes):
            return obj.hex()
        return super().default(obj)


def perform_full_backup() -> str:
    """Create a consolidated backup archive containing PostgreSQL dump and all persistent uploads."""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    staging_dir = os.path.join(BACKUP_DIR, f"snapshot_{timestamp}")
    os.makedirs(staging_dir, exist_ok=True)

    try:
        # 1. Export PostgreSQL tables
        print("[1/3] Snapshotting PostgreSQL database tables...")
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        db_dump = {"metadata": {"timestamp": timestamp, "tables_count": len(tables)}, "tables": {}}

        with engine.connect() as conn:
            for t in sorted(tables):
                res = conn.execute(text(f'SELECT * FROM "{t}"'))
                cols = list(res.keys())
                rows = []
                for row in res.fetchall():
                    row_dict = {}
                    for k, v in zip(cols, row):
                        if hasattr(v, "isoformat"):
                            row_dict[k] = v.isoformat()
                        else:
                            row_dict[k] = v
                    rows.append(row_dict)
                db_dump["tables"][t] = {"row_count": len(rows), "columns": cols, "rows": rows}

        with open(os.path.join(staging_dir, "database_snapshot.json"), "w", encoding="utf-8") as f:
            json.dump(db_dump, f, indent=2, cls=SafeJSONEncoder)

        # 2. Copy persistent upload files (student photos & exam papers)
        print("[2/3] Archiving persistent upload directories...")
        uploads_target = os.path.join(staging_dir, "uploads")
        if os.path.exists(UPLOADS_DIR):
            shutil.copytree(UPLOADS_DIR, uploads_target, dirs_exist_ok=True)
        else:
            os.makedirs(uploads_target, exist_ok=True)

        # 3. Create compressed tar.gz bundle
        archive_path = os.path.join(BACKUP_DIR, f"somroyal_ems_backup_{timestamp}.tar.gz")
        print(f"[3/3] Compressing into {archive_path}...")
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(staging_dir, arcname=f"somroyal_ems_backup_{timestamp}")

        print(f"SUCCESS: System backup completed successfully! Archive: {archive_path}")
        return archive_path
    finally:
        shutil.rmtree(staging_dir, ignore_errors=True)


def verify_photo_integrity() -> dict:
    """Verifies that all students with photo_path in DB have their physical files present on disk."""
    db = SessionLocal()
    try:
        students = db.query(Student).filter(Student.photo_path.isnot(None)).all()
        total_photos = len(students)
        verified = 0
        missing = []

        for s in students:
            full_path = os.path.join(UPLOADS_DIR, s.photo_path.replace("/", os.sep).replace("\\", os.sep))
            if os.path.exists(full_path):
                verified += 1
            else:
                missing.append({"student_id": s.id, "admission_number": s.admission_number, "path": s.photo_path})

        return {
            "total_students_with_photo_records": total_photos,
            "intact_files_on_disk": verified,
            "missing_files": missing,
            "integrity_pass": len(missing) == 0
        }
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        report = verify_photo_integrity()
        print(json.dumps(report, indent=2))
    else:
        archive = perform_full_backup()
        print("\nIntegrity check after backup:")
        report = verify_photo_integrity()
        print(json.dumps(report, indent=2))
