import os
import sys
from collections import defaultdict
from typing import Dict, List, Any

# Ensure backend directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal
from app.models.school_class import SchoolClass
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment


def run_student_enrollment_audit() -> Dict[str, Any]:
    db = SessionLocal()
    try:
        all_students = db.query(Student).all()
        all_enrollments = db.query(StudentEnrollment).all()

        total_students = len(all_students)
        total_enrollments = len(all_enrollments)

        # 1. Duplicate enrollments: same student_id + academic_year with active status
        active_enrollments = [e for e in all_enrollments if e.status == "ACTIVE"]
        student_year_map = defaultdict(list)
        for e in active_enrollments:
            # Normalize academic year format for grouping
            norm_year = (e.academic_year or "").replace("-", "/")
            student_year_map[(e.student_id, norm_year)].append(e)

        duplicate_student_enrollments = {k: v for k, v in student_year_map.items() if len(v) > 1}

        # 2. Student enrolled in two different active classes in the same academic year
        multi_class_enrollments = {}
        for (s_id, year), enr_list in student_year_map.items():
            classes = set(e.class_id for e in enr_list)
            if len(classes) > 1:
                multi_class_enrollments[(s_id, year)] = enr_list

        # 3. Students without class (no active enrollment)
        active_enrolled_student_ids = set(e.student_id for e in active_enrollments)
        students_without_class = [s for s in all_students if s.id not in active_enrolled_student_ids and s.status == "ACTIVE"]

        # 4. Inactive students with active enrollment
        inactive_students_with_active_enr = []
        for e in active_enrollments:
            s = db.query(Student).filter(Student.id == e.student_id).first()
            if s and s.status != "ACTIVE":
                inactive_students_with_active_enr.append((s, e))

        # 5. Enrollment pointing to inactive class
        enrollment_to_inactive_class = []
        for e in active_enrollments:
            c = db.query(SchoolClass).filter(SchoolClass.id == e.class_id).first()
            if not c or c.status != "ACTIVE":
                enrollment_to_inactive_class.append((e, c))

        # 6. Enrollment pointing to test/generated class
        test_keywords = ["test", "tst", "12subj", "12s", "cf", "delta stream"]
        enrollment_to_test_class = []
        for e in active_enrollments:
            c = db.query(SchoolClass).filter(SchoolClass.id == e.class_id).first()
            if c:
                name_l = (c.name or "").lower()
                code_l = (c.code or "").lower()
                if any(k in name_l or k in code_l for k in test_keywords):
                    enrollment_to_test_class.append((e, c))

        print("=== STUDENT ENROLLMENT INTEGRITY AUDIT RESULTS ===")
        print(f"Total Students: {total_students}")
        print(f"Total Enrollments: {total_enrollments}")
        print(f"Active Enrollments: {len(active_enrollments)}")
        print(f"Duplicate (Student, Year) Active Enrollments: {len(duplicate_student_enrollments)}")
        print(f"Students in Multiple Classes in Same Year: {len(multi_class_enrollments)}")
        print(f"Active Students without Active Class Enrollment: {len(students_without_class)}")
        print(f"Inactive Students with Active Enrollment: {len(inactive_students_with_active_enr)}")
        print(f"Active Enrollments Pointing to Inactive Class: {len(enrollment_to_inactive_class)}")
        print(f"Active Enrollments Pointing to Test Class: {len(enrollment_to_test_class)}")

        report_path = os.path.join(os.path.dirname(__file__), "student_enrollment_integrity_audit_report.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# Student Enrollment Integrity Audit Report\n\n")
            f.write(f"- **Total Students**: {total_students}\n")
            f.write(f"- **Total Enrollments**: {total_enrollments}\n")
            f.write(f"- **Active Enrollments**: {len(active_enrollments)}\n")
            f.write(f"- **Duplicate (Student, Year) Active Enrollments**: {len(duplicate_student_enrollments)}\n")
            f.write(f"- **Students Enrolled in 2+ Classes in Same Year**: {len(multi_class_enrollments)}\n")
            f.write(f"- **Active Students without Active Enrollment**: {len(students_without_class)}\n")
            f.write(f"- **Inactive Students with Active Enrollment**: {len(inactive_students_with_active_enr)}\n")
            f.write(f"- **Active Enrollments Pointing to Inactive Class**: {len(enrollment_to_inactive_class)}\n")
            f.write(f"- **Active Enrollments Pointing to Test Class**: {len(enrollment_to_test_class)}\n\n")

            if duplicate_student_enrollments:
                f.write("## Duplicate Enrollments (Same Year)\n\n")
                for (s_id, yr), elist in duplicate_student_enrollments.items():
                    s = db.query(Student).filter(Student.id == s_id).first()
                    f.write(f"### Student ID {s_id} ({s.admission_number if s else ''} - {s.full_name if s else ''}) Year: {yr}\n")
                    for en in elist:
                        c = db.query(SchoolClass).filter(SchoolClass.id == en.class_id).first()
                        f.write(f"- Enrollment ID {en.id}: Class {en.class_id} (`{c.name if c else 'Unknown'}`) Status: `{en.status}`\n")
                    f.write("\n")

            if enrollment_to_test_class:
                f.write("## Enrollments Pointing to Test Classes\n\n")
                for en, cl in enrollment_to_test_class:
                    s = db.query(Student).filter(Student.id == en.student_id).first()
                    f.write(f"- Student {s.full_name if s else en.student_id} ({s.admission_number if s else ''}) -> Class {cl.id} (`{cl.name}`) Enrollment ID: {en.id}\n")
                f.write("\n")

        print(f"Enrollment report generated at: {report_path}")
        return {
            "total_students": total_students,
            "total_enrollments": total_enrollments,
            "active_enrollments": len(active_enrollments),
            "duplicate_student_enrollments": len(duplicate_student_enrollments),
            "multi_class_enrollments": len(multi_class_enrollments),
            "students_without_class": len(students_without_class),
            "inactive_students_with_active_enr": len(inactive_students_with_active_enr),
            "enrollment_to_inactive_class": len(enrollment_to_inactive_class),
            "enrollment_to_test_class": len(enrollment_to_test_class),
        }
    finally:
        db.close()


if __name__ == "__main__":
    run_student_enrollment_audit()
