"""
Self-healing repair for corrupted InnoDB AUTO_INCREMENT counters.

XAMPP's MariaDB can lose/corrupt auto-increment counters after an unclean
shutdown (PC powered off while MySQL is running). Inserts then fail with
error 1467 "Failed to read auto-increment value from storage engine",
which breaks login (the sessions table) and anything else that inserts rows.

This module resets every broken counter to MAX(id) + 1 for the central
database and every tenant database registered in the institutions table.
"""
import logging
import re
from typing import Dict, List

from sqlalchemy import create_engine, text

from app.core.config import settings
from app.core.tenant_provisioner import get_server_db_url

logger = logging.getLogger("hawlwadaag_sms")

_SAFE_IDENT = re.compile(r"^[A-Za-z0-9_]+$")


def _tenant_database_names(conn, central_db: str) -> List[str]:
    names = {central_db}
    try:
        rows = conn.execute(text(
            f"SELECT database_name FROM `{central_db}`.institutions "
            "WHERE database_name IS NOT NULL AND database_name <> ''"
        ))
        names.update(r[0].strip() for r in rows if r[0])
    except Exception as exc:  # institutions table may not exist yet
        logger.debug(f"Could not read institutions table: {exc}")
    return sorted(n for n in names if _SAFE_IDENT.match(n))


def repair_auto_increment_counters() -> Dict[str, List[str]]:
    """Detects and repairs broken AUTO_INCREMENT counters. Returns repaired tables per DB."""
    if "mysql" not in settings.DATABASE_URL:
        return {}

    central_db = settings.DATABASE_URL.rsplit("/", 1)[-1].split("?", 1)[0] or "sms"
    engine = create_engine(get_server_db_url(), pool_pre_ping=True)
    repaired: Dict[str, List[str]] = {}

    try:
        with engine.connect() as conn:
            for db in _tenant_database_names(conn, central_db):
                # Tables with an auto_increment column
                cols = conn.execute(text(
                    "SELECT c.TABLE_NAME, c.COLUMN_NAME, t.AUTO_INCREMENT "
                    "FROM information_schema.COLUMNS c "
                    "JOIN information_schema.TABLES t "
                    "  ON t.TABLE_SCHEMA = c.TABLE_SCHEMA AND t.TABLE_NAME = c.TABLE_NAME "
                    "WHERE c.TABLE_SCHEMA = :db AND c.EXTRA LIKE '%auto_increment%'"
                ), {"db": db}).fetchall()

                for table, column, counter in cols:
                    if not (_SAFE_IDENT.match(table) and _SAFE_IDENT.match(column)):
                        continue
                    try:
                        max_id = conn.execute(text(
                            f"SELECT COALESCE(MAX(`{column}`), 0) FROM `{db}`.`{table}`"
                        )).scalar() or 0
                        if counter is not None and int(counter) > int(max_id):
                            continue  # healthy
                        next_id = int(max_id) + 1
                        conn.execute(text(
                            f"ALTER TABLE `{db}`.`{table}` AUTO_INCREMENT = {next_id}"
                        ))
                        repaired.setdefault(db, []).append(f"{table} (was {counter}, now {next_id})")
                    except Exception as exc:
                        logger.warning(f"Auto-increment repair failed for {db}.{table}: {exc}")
            conn.commit()
    finally:
        engine.dispose()

    for db, tables in repaired.items():
        logger.warning(f"Repaired AUTO_INCREMENT counters in '{db}': {', '.join(tables)}")
    return repaired


if __name__ == "__main__":
    result = repair_auto_increment_counters()
    if not result:
        print("All AUTO_INCREMENT counters are healthy.")
    for db, tables in result.items():
        print(f"[{db}]")
        for t in tables:
            print(f"  - {t}")
