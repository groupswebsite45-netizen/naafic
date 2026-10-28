"""
Fees & Admin Students Consistency Audit
Compares Admin Students active enrollment count vs Fees student count for every academic year,
for both PRIMARY and SECONDARY classes.
Any mismatch = FAIL.
"""
import sys
import os
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal
from app.models.school_class import SchoolClass
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.repositories.fee_repo import FeeRepository
from sqlalchemy import func


def run_audit() -> bool:
    db = SessionLocal()
    fee_repo = FeeRepository(db)
    all_passed = True

    try:
        # Fetch all distinct academic years
        academic_years = [
            r[0] for r in db.query(SchoolClass.academic_year)
            .filter(SchoolClass.status == "ACTIVE")
            .distinct().order_by(SchoolClass.academic_year.desc()).all()
        ]

        print("=" * 80)
        print("FEES & ADMIN STUDENTS FILTER CONSISTENCY AUDIT")
        print("=" * 80)

        total_classes_checked = 0

        for ay in academic_years:
            print(f"\n[ Academic Year: {ay} ]")
            for div in ["PRIMARY", "SECONDARY"]:
                print(f"\n  --- Division: {div} ---")
                classes = fee_repo.get_classes_for_fees(academic_year=ay, division=div)

                if not classes:
                    print(f"  No {div} classes found for {ay}.")
                    continue

                for cls in classes:
                    total_classes_checked += 1

                    # 1. Admin Students active enrolled count
                    admin_count = (
                        db.query(func.count(StudentEnrollment.id))
                        .join(Student, Student.id == StudentEnrollment.student_id)
                        .filter(
                            StudentEnrollment.class_id == cls.id,
                            StudentEnrollment.academic_year == ay,
                            StudentEnrollment.status == "ACTIVE",
                            Student.status == "ACTIVE",
                        )
                        .scalar() or 0
                    )

                    # 2. Fees enrolled students count
                    fees_breakdown = fee_repo.get_class_enrolled_students_with_finance(cls.id, ay)
                    fees_count = fees_breakdown["total_students"]
                    fees_list_len = len(fees_breakdown["students"])

                    # 3. Verify class division strictly matches
                    div_correct = (cls.division == div)

                    # Check
                    passed = (admin_count == fees_count == fees_list_len) and div_correct

                    status_str = "PASS" if passed else "FAIL"
                    print(
                        f"  {cls.name:<25} ({cls.code}): Admin Students = {admin_count:>3} | "
                        f"Fees = {fees_count:>3} | Division = {cls.division} -> {status_str}"
                    )

                    if not passed:
                        all_passed = False
                        print(f"    ERROR MISMATCH in class {cls.name}: Admin={admin_count}, Fees={fees_count}, Div={cls.division} vs Expected={div}")

        print("\n" + "=" * 80)
        if all_passed:
            print(f"AUDIT RESULT: ALL {total_classes_checked} CLASSES PASSED WITH 100% CONSISTENCY (PASS)")
        else:
            print(f"AUDIT RESULT: SOME CLASSES FAILED CONSISTENCY AUDIT (FAIL)")
        print("=" * 80)

        return all_passed

    finally:
        db.close()


if __name__ == "__main__":
    success = run_audit()
    sys.exit(0 if success else 1)
