"""
Verify Fees and Admin Students Class Consistency
Requirement 33:
For every active class:
Compare Admin Students count against Fees student count for each academic_year + class_id.
They MUST MATCH.
Generate backend/tests/fees_class_consistency_report.md.
"""
import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal
from app.models.school_class import SchoolClass
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.repositories.fee_repo import FeeRepository
from sqlalchemy import func

def generate_consistency_report():
    db = SessionLocal()
    fee_repo = FeeRepository(db)
    
    try:
        # Get all active classes
        active_classes = db.query(SchoolClass).filter(
            SchoolClass.status == "ACTIVE"
        ).order_by(SchoolClass.academic_year, SchoolClass.division, SchoolClass.name).all()

        rows = []
        total_checks = 0
        passed_checks = 0
        failed_checks = 0

        for sc in active_classes:
            academic_year = sc.academic_year
            class_id = sc.id
            class_name = sc.name
            division = sc.division

            # 1. Admin Students Count:
            # Enrolled students with status ACTIVE joined with Student status ACTIVE
            admin_count = db.query(func.count(StudentEnrollment.id)).join(
                Student, Student.id == StudentEnrollment.student_id
            ).filter(
                StudentEnrollment.class_id == class_id,
                StudentEnrollment.academic_year == academic_year,
                StudentEnrollment.status == "ACTIVE",
                Student.status == "ACTIVE"
            ).scalar() or 0

            # 2. Fees Student Count via canonical FeeRepository:
            fees_result = fee_repo.get_class_enrolled_students_with_finance(class_id, academic_year)
            fees_count = fees_result["total_students"]
            fees_students_list_len = len(fees_result["students"])

            # Check match
            is_match = (admin_count == fees_count == fees_students_list_len)
            match_status = "PASS" if is_match else "FAIL"

            total_checks += 1
            if is_match:
                passed_checks += 1
            else:
                failed_checks += 1

            rows.append({
                "academic_year": academic_year,
                "division": division,
                "class_id": class_id,
                "class_name": class_name,
                "admin_count": admin_count,
                "fees_count": fees_count,
                "fees_list_len": fees_students_list_len,
                "match": match_status
            })

        # Generate markdown report
        report_path = Path(__file__).parent / "fees_class_consistency_report.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# Authoritative Fees vs Admin Students Class Consistency Report\n\n")
            f.write(f"Generated at: 2026-09-19\n\n")
            f.write("## Summary\n\n")
            f.write(f"- **Total Active Classes Evaluated**: {total_checks}\n")
            f.write(f"- **Passed Checks**: {passed_checks}\n")
            f.write(f"- **Failed Checks**: {failed_checks}\n")
            f.write(f"- **Overall Consistency Status**: **{'PASS' if failed_checks == 0 else 'FAIL'}**\n\n")

            f.write("## Class by Class Authoritative Comparison\n\n")
            f.write("| Academic Year | Division | Class ID | Class Name | Admin Students | Fees Students | Match |\n")
            f.write("|---|---|---:|---|---:|---:|---:|\n")
            for r in rows:
                f.write(f"| {r['academic_year']} | {r['division']} | {r['class_id']} | {r['class_name']} | {r['admin_count']} | {r['fees_count']} | {r['match']} |\n")

            f.write("\n\n## Specific Verification: Grade 8 - A\n\n")
            g8 = [r for r in rows if "Grade 8" in r["class_name"]]
            if g8:
                for g in g8:
                    f.write(f"- Class: **{g['class_name']}** (ID: {g['class_id']})\n")
                    f.write(f"  - Academic Year: {g['academic_year']}\n")
                    f.write(f"  - Admin Students Count: {g['admin_count']}\n")
                    f.write(f"  - Fees Module Count: {g['fees_count']}\n")
                    f.write(f"  - Consistency: **{g['match']}** (Zero Empty Mismatch)\n")
            else:
                f.write("No Grade 8 found.\n")

        print(f"Consistency report generated at: {report_path}")
        print(f"Checks: {total_checks} | Passed: {passed_checks} | Failed: {failed_checks}")
        if failed_checks > 0:
            print("WARNING: Some consistency checks failed!")
            sys.exit(1)
        else:
            print("ALL CHECKS PASSED: 100% consistency between Admin Students and Fees.")

    finally:
        db.close()

if __name__ == "__main__":
    generate_consistency_report()
