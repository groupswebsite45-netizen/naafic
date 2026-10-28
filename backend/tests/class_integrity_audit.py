import os
import sys
from collections import defaultdict
from typing import Dict, List, Any

# Ensure backend directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal
from app.models.school_class import SchoolClass
from app.models.student_enrollment import StudentEnrollment
from app.models.teacher_assignment import TeacherAssignment
from app.models.timetable import Timetable
from app.models.exam import Exam, ExamResult
from app.models.attendance import Attendance
from app.models.fee import FeeStructure, StudentFee


def run_class_integrity_audit() -> Dict[str, Any]:
    db = SessionLocal()
    try:
        all_classes = db.query(SchoolClass).order_by(SchoolClass.academic_year, SchoolClass.division, SchoolClass.id).all()

        total_classes = len(all_classes)
        active_classes = [c for c in all_classes if c.status == "ACTIVE"]
        inactive_classes = [c for c in all_classes if c.status != "ACTIVE"]

        valid_primary_levels = [f"Grade {i}" for i in range(1, 9)]
        valid_secondary_levels = [f"Form {i}" for i in range(1, 5)]

        class_details = []
        classes_with_students = []
        empty_classes = []
        test_classes = []
        invalid_primary = []
        invalid_secondary = []

        # Grouping for duplicate detection by (academic_year, division, level, section)
        grouped_by_identity = defaultdict(list)

        for c in all_classes:
            enr_count = db.query(StudentEnrollment).filter(StudentEnrollment.class_id == c.id).count()
            active_enr_count = db.query(StudentEnrollment).filter(
                StudentEnrollment.class_id == c.id,
                StudentEnrollment.status == "ACTIVE"
            ).count()
            ta_count = db.query(TeacherAssignment).filter(TeacherAssignment.class_id == c.id).count()
            tt_count = db.query(Timetable).filter(Timetable.class_id == c.id).count()
            exam_count = db.query(Exam).filter(Exam.class_id == c.id).count()
            exam_res_count = db.query(ExamResult).join(Exam, ExamResult.exam_id == Exam.id).filter(Exam.class_id == c.id).count()
            att_count = db.query(Attendance).filter(Attendance.class_id == c.id).count()
            fee_struct_count = db.query(FeeStructure).filter(FeeStructure.class_id == c.id).count()
            student_fee_count = db.query(StudentFee).filter(StudentFee.class_id == c.id).count()

            is_test = False
            name_lower = (c.name or "").lower()
            code_lower = (c.code or "").lower()
            if any(k in name_lower or k in code_lower for k in ["test", "tst", "12subj", "12s", "cf", "delta stream"]):
                is_test = True
                test_classes.append(c)

            if active_enr_count > 0:
                classes_with_students.append(c)
            else:
                empty_classes.append(c)

            # Check validity of levels
            if c.division == "PRIMARY":
                if c.level not in valid_primary_levels:
                    invalid_primary.append(c)
            elif c.division == "SECONDARY":
                if c.level not in valid_secondary_levels:
                    invalid_secondary.append(c)

            grouped_by_identity[(c.academic_year, c.division, c.level, c.section)].append(c)

            class_details.append({
                "id": c.id,
                "name": c.name,
                "code": c.code,
                "division": c.division,
                "level": c.level,
                "section": c.section,
                "academic_year": c.academic_year,
                "status": c.status,
                "is_test": is_test,
                "enrolled_students": enr_count,
                "active_enrolled": active_enr_count,
                "teacher_assignments": ta_count,
                "timetables": tt_count,
                "exams": exam_count,
                "exam_results": exam_res_count,
                "attendances": att_count,
                "fee_structures": fee_struct_count,
                "student_fees": student_fee_count,
            })

        # Identify duplicate groups
        duplicate_groups = {k: v for k, v in grouped_by_identity.items() if len(v) > 1}

        # Generate markdown report
        report_path = os.path.join(os.path.dirname(__file__), "class_integrity_audit_report.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# Class Integrity Audit Report\n\n")
            f.write(f"- **Total Classes**: {total_classes}\n")
            f.write(f"- **Active Classes**: {len(active_classes)}\n")
            f.write(f"- **Inactive Classes**: {len(inactive_classes)}\n")
            f.write(f"- **Classes with Real Active Students**: {len(classes_with_students)}\n")
            f.write(f"- **Empty Classes (0 Students)**: {len(empty_classes)}\n")
            f.write(f"- **Identified Test/Generated Classes**: {len(test_classes)}\n")
            f.write(f"- **Invalid Primary Classes (Outside Grade 1-8)**: {len(invalid_primary)}\n")
            f.write(f"- **Invalid Secondary Classes (Outside Form 1-4)**: {len(invalid_secondary)}\n")
            f.write(f"- **Duplicate Class Groups**: {len(duplicate_groups)}\n\n")

            f.write("## 1. Duplicate Groups Detected\n\n")
            if not duplicate_groups:
                f.write("No duplicate class groups detected.\n\n")
            else:
                for (year, div, lvl, sec), clist in duplicate_groups.items():
                    f.write(f"### Group: Year={year} | Div={div} | Level={lvl} | Section={sec} ({len(clist)} duplicates)\n")
                    f.write("| ID | Name | Code | Status | Enrolled | TA | Timetables | Exams | Fee Structures | Invoices |\n")
                    f.write("|---|---|---|---|---:|---:|---:|---:|---:|---:|\n")
                    for cl in clist:
                        f.write(f"| {cl.id} | {cl.name} | {cl.code} | {cl.status} | {len(cl.enrollments)} | {len(cl.teacher_assignments)} | {len(cl.timetables)} | {len(cl.exams)} | {len(cl.fee_structures)} | {db.query(StudentFee).filter(StudentFee.class_id == cl.id).count()} |\n")
                    f.write("\n")

            f.write("## 2. Identified Test / Generated Classes\n\n")
            if not test_classes:
                f.write("No test or generated classes found.\n\n")
            else:
                f.write("| ID | Name | Code | Academic Year | Status | Enrolled | Has Dependents |\n")
                f.write("|---|---|---|---|---|---:|---|\n")
                for tc in test_classes:
                    has_dep = (len(tc.enrollments) + len(tc.teacher_assignments) + len(tc.exams) + len(tc.fee_structures)) > 0
                    f.write(f"| {tc.id} | {tc.name} | {tc.code} | {tc.academic_year} | {tc.status} | {len(tc.enrollments)} | {'YES' if has_dep else 'NO'} |\n")
                f.write("\n")

            f.write("## 3. Invalid Grade/Form Levels\n\n")
            if not invalid_primary and not invalid_secondary:
                f.write("All classes conform to Grade 1-8 and Form 1-4.\n\n")
            else:
                for ic in invalid_primary + invalid_secondary:
                    f.write(f"- ID {ic.id}: `{ic.name}` (Div: `{ic.division}`, Level: `{ic.level}`, Year: `{ic.academic_year}`, Status: `{ic.status}`)\n")
                f.write("\n")

            f.write("## 4. Comprehensive Class Inventory & Dependencies\n\n")
            f.write("| ID | Year | Div | Level | Sec | Name | Code | Status | Enr | TA | Ex | ExR | TT | Att | FeeStr | StFee |\n")
            f.write("|---:|---|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|\n")
            for cd in class_details:
                f.write(f"| {cd['id']} | {cd['academic_year']} | {cd['division']} | {cd['level']} | {cd['section']} | {cd['name']} | {cd['code']} | {cd['status']} | {cd['active_enrolled']} | {cd['teacher_assignments']} | {cd['exams']} | {cd['exam_results']} | {cd['timetables']} | {cd['attendances']} | {cd['fee_structures']} | {cd['student_fees']} |\n")
            f.write("\n")

        print(f"Class audit report successfully generated at: {report_path}")
        return {
            "total_classes": total_classes,
            "active_classes": len(active_classes),
            "inactive_classes": len(inactive_classes),
            "classes_with_students": len(classes_with_students),
            "empty_classes": len(empty_classes),
            "test_classes": len(test_classes),
            "invalid_primary": len(invalid_primary),
            "invalid_secondary": len(invalid_secondary),
            "duplicate_groups": len(duplicate_groups),
        }
    finally:
        db.close()


if __name__ == "__main__":
    res = run_class_integrity_audit()
    print("Class Integrity Audit Summary:", res)
