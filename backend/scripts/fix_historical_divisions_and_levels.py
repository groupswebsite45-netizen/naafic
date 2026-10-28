import sys
import os
import re

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app.core.database import SessionLocal
from app.models.school_class import SchoolClass
from app.models.subject import Subject

def fix_divisions_and_levels():
    db = SessionLocal()
    try:
        print("=== Classifying Historical Classes ===")
        classes = db.query(SchoolClass).all()
        for c in classes:
            name = c.name or ""
            # Match Form X
            form_match = re.search(r"Form\s*(\d+)", name, re.IGNORECASE)
            grade_match = re.search(r"Grade\s*(\d+)", name, re.IGNORECASE)
            
            if form_match:
                f_num = int(form_match.group(1))
                c.division = "SECONDARY"
                c.level = f"Form {f_num}"
            elif grade_match:
                g_num = int(grade_match.group(1))
                if g_num <= 8:
                    c.division = "PRIMARY"
                    c.level = f"Grade {g_num}"
                else:
                    c.division = "SECONDARY"
                    c.level = f"Form {min(4, g_num - 8)}"
            else:
                # Default timetable test classes or other classes
                c.division = "PRIMARY"
                c.level = "Grade 7"

            # Clean section if empty
            if not c.section:
                sec_match = re.search(r"-\s*([A-Za-z0-9]+)$", name)
                c.section = sec_match.group(1).upper() if sec_match else "A"

            print(f"Class ID {c.id}: name='{c.name}' -> division='{c.division}', level='{c.level}', section='{c.section}'")

        print("\n=== Classifying Historical Subjects ===")
        subjects = db.query(Subject).all()
        secondary_only = [
            "Physics", "Chemistry", "Biology", "History", "Geography",
            "Business Studies", "Economics", "Agriculture"
        ]
        primary_only = [
            "Science", "Social Studies", "Primary Science"
        ]

        for s in subjects:
            s_name = (s.name or "").strip()
            # Check if any secondary keyword in subject name
            is_sec = any(kw.lower() in s_name.lower() for kw in secondary_only)
            is_prim = any(kw.lower() in s_name.lower() for kw in primary_only)

            if is_sec and not is_prim:
                s.division = "SECONDARY"
                s.applicable_levels = "Form 1,Form 2,Form 3,Form 4"
            elif is_prim and not is_sec:
                s.division = "PRIMARY"
                s.applicable_levels = "Grade 1,Grade 2,Grade 3,Grade 4,Grade 5,Grade 6,Grade 7,Grade 8"
            else:
                # Shared subjects across both divisions (e.g. Mathematics, English, Somali, Arabic, Islamic Studies, Computer, PE)
                s.division = "ALL"
                s.applicable_levels = "Grade 1,Grade 2,Grade 3,Grade 4,Grade 5,Grade 6,Grade 7,Grade 8,Form 1,Form 2,Form 3,Form 4"

            print(f"Subject ID {s.id}: name='{s.name}' -> division='{s.division}', applicable_levels='{s.applicable_levels}'")

        db.commit()
        print("\nSuccessfully updated all classes and subjects.")
    except Exception as e:
        db.rollback()
        print(f"Error during update: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    fix_divisions_and_levels()
