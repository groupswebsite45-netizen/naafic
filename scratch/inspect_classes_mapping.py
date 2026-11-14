import sys, os
from pathlib import Path

BACKEND_DIR = Path("backend").resolve()
sys.path.insert(0, str(BACKEND_DIR))
from dotenv import load_dotenv
load_dotenv(BACKEND_DIR / ".env")

from app.core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    non_26_classes = conn.execute(text("""
        SELECT id, name, division, level, section, academic_year, status
        FROM classes
        WHERE academic_year != '2026/2027'
        ORDER BY id
    """)).mappings().all()

    c_26 = conn.execute(text("""
        SELECT id, name, division, level, section, academic_year, status
        FROM classes
        WHERE academic_year = '2026/2027'
        ORDER BY id
    """)).mappings().all()

    c_26_map = {(c['division'], c['level'], c['section']): c for c in c_26}
    c_26_name_map = {c['name']: c for c in c_26}

    print(f"Total 2026/2027 classes: {len(c_26)}")
    print(f"Total non-2026/2027 classes: {len(non_26_classes)}")
    
    matches = []
    no_matches = []
    for c in non_26_classes:
        key = (c['division'], c['level'], c['section'])
        if key in c_26_map:
            matches.append((c, c_26_map[key]))
        elif c['name'] in c_26_name_map:
            matches.append((c, c_26_name_map[c['name']]))
        else:
            no_matches.append(c)

    print(f"\nNon-2026 classes that have a corresponding 2026/2027 class: {len(matches)}")
    for old_c, new_c in matches:
        print(f"  Old Class {old_c['id']} ('{old_c['name']}', yr={old_c['academic_year']}) -> Matches 2026/2027 Class {new_c['id']} ('{new_c['name']}')")

    print(f"\nNon-2026 classes that do NOT have a corresponding 2026/2027 class: {len(no_matches)}")
    for c in no_matches:
        print(f"  Class {c['id']}: '{c['name']}' (lvl={c['level']}, sec={c['section']}, div={c['division']}) yr={c['academic_year']}")
