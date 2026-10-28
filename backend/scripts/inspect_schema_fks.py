import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.core.database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
print("=== Foreign Keys Referencing 'students' or 'users' ===")
for table_name in sorted(inspector.get_table_names()):
    fks = inspector.get_foreign_keys(table_name)
    for fk in fks:
        ref_table = fk.get("referred_table")
        if ref_table in ("students", "users", "student_enrollments", "student_fees", "exam_results", "attendances"):
            cols = fk.get("constrained_columns")
            ref_cols = fk.get("referred_columns")
            ondelete = fk.get("options", {}).get("ondelete")
            print(f"{table_name}.{cols} -> {ref_table}.{ref_cols} [ondelete={ondelete}]")
