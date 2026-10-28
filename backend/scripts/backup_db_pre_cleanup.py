import sys
import os
import json
from datetime import datetime, date, time
from decimal import Decimal

# Ensure backend root in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import engine
from sqlalchemy import inspect, text

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date, time)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, bytes):
            return obj.hex()
        return super().default(obj)

def run_backup():
    backup_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backups"))
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup_dir, f"db_backup_pre_cleanup_{timestamp}.json")
    latest_path = os.path.join(backup_dir, "db_backup_pre_cleanup.json")

    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Starting PostgreSQL full snapshot of {len(tables)} tables...")

    backup_data = {
        "metadata": {
            "created_at": datetime.now().isoformat(),
            "table_count": len(tables),
            "tables": sorted(tables),
        },
        "tables": {}
    }

    with engine.connect() as conn:
        for t in sorted(tables):
            result = conn.execute(text(f'SELECT * FROM "{t}"'))
            columns = list(result.keys())
            rows = [dict(zip(columns, row)) for row in result.fetchall()]
            backup_data["tables"][t] = {
                "row_count": len(rows),
                "columns": columns,
                "rows": rows
            }
            print(f"  Backed up table '{t}': {len(rows)} rows")

    with open(backup_path, "w", encoding="utf-8") as f:
        json.dump(backup_data, f, cls=CustomEncoder, indent=2)

    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump(backup_data, f, cls=CustomEncoder, indent=2)

    file_size_mb = os.path.getsize(latest_path) / (1024 * 1024)
    print(f"\n[SUCCESS] Backup completed successfully!")
    print(f"Snapshot saved to: {latest_path} ({file_size_mb:.2f} MB)")

if __name__ == "__main__":
    run_backup()
