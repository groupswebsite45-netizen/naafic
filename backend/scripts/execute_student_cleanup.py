import sys
import os
from decimal import Decimal
from datetime import date, datetime, timezone

# Ensure backend root in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal, engine
from app.core.security import get_password_hash
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.models.school_class import SchoolClass
from app.models.user import User
from app.models.user_role import UserRole
from app.models.role import Role
from app.models.teacher import Teacher
from app.models.teacher_assignment import TeacherAssignment
from app.models.subject import Subject
from app.models.fee import StudentFee, FeePayment, FeeStructure
from app.models.exam import Exam, ExamResult
from app.models.attendance import Attendance
from app.models.student_result_view import StudentResultView
from app.models.notification import Notification
from app.models.notification import NotificationTemplate
from app.models.session import SessionModel
from app.models.class_promotion import ClassPromotionBatch, ClassPromotionRecord
from sqlalchemy import text

# Canonical retained students definition
PRIMARY_RETAINED = [
    # Grade 7 - A (ID 147)
    {
        "id": 22, "adm": "ADM-2026-002", "first": "Amina", "middle": "Hassan", "last": "Ibrahim",
        "gender": "Female", "class_id": 147, "g_name": "Hassan Ibrahim", "g_phone": "+252 61 7000002", "g_rel": "Father"
    },
    {
        "id": 23, "adm": "ADM-2026-003", "first": "Liban", "middle": "Abdirahman", "last": "Elmi",
        "gender": "Male", "class_id": 147, "g_name": "Mariam Noor", "g_phone": "+252 61 7000003", "g_rel": "Mother"
    },
    {
        "id": 24, "adm": "ADM-2026-004", "first": "Hafsa", "middle": "Mohamud", "last": "Adan",
        "gender": "Female", "class_id": 147, "g_name": "Mohamud Adan", "g_phone": "+252 61 7000004", "g_rel": "Father"
    },
    {
        "id": 1, "adm": "ADM-413501", "first": "Mushtaaq", "middle": "Ahmed", "last": "Cali",
        "gender": "Male", "class_id": 147, "g_name": "Ahmed Cali", "g_phone": "+252 61 7000011", "g_rel": "Father"
    },
    {
        "id": 244, "adm": "ADM-527B23", "first": "Amina", "middle": "Farah", "last": "Gedi",
        "gender": "Female", "class_id": 147, "g_name": "Farah Gedi", "g_phone": "+252 61 7000012", "g_rel": "Father"
    },
    # Grade 8 - A (ID 32)
    {
        "id": 25, "adm": "ADM-2026-005", "first": "Zakarie", "middle": "Jama", "last": "Hussein",
        "gender": "Male", "class_id": 32, "g_name": "Jama Hussein", "g_phone": "+252 61 7000005", "g_rel": "Father"
    },
    {
        "id": 26, "adm": "ADM-2026-006", "first": "Safia", "middle": "Farah", "last": "Gedi",
        "gender": "Female", "class_id": 32, "g_name": "Farah Gedi", "g_phone": "+252 61 7000006", "g_rel": "Father"
    },
    {
        "id": 21, "adm": "ADM-2026-001", "first": "Mustaf", "middle": "Ali", "last": "Yusuf",
        "gender": "Male", "class_id": 32, "g_name": "Ali Yusuf", "g_phone": "+252 61 7000001", "g_rel": "Father"
    },
    {
        "id": 289, "adm": "ADM-2026-009", "first": "Mustaf", "middle": "Noor", "last": "Warsame",
        "gender": "Male", "class_id": 32, "g_name": "Noor Warsame", "g_phone": "+252 61 7000009", "g_rel": "Father"
    },
    {
        "id": 290, "adm": "ADM-2026-010", "first": "Amina", "middle": "Ibrahim", "last": "Dahir",
        "gender": "Female", "class_id": 32, "g_name": "Ibrahim Dahir", "g_phone": "+252 61 7000010", "g_rel": "Father"
    },
]

SECONDARY_RETAINED = [
    # Form 1 - A (ID 157)
    {
        "id": 27, "adm": "ADM-2026-007", "first": "Khaalid", "middle": "Ibrahim", "last": "Nur",
        "gender": "Male", "class_id": 157, "g_name": "Ibrahim Nur", "g_phone": "+252 61 7000007", "g_rel": "Father"
    },
    {
        "id": 28, "adm": "ADM-2026-008", "first": "Yasmin", "middle": "Osman", "last": "Roble",
        "gender": "Female", "class_id": 157, "g_name": "Osman Roble", "g_phone": "+252 61 7000008", "g_rel": "Father"
    },
    {
        "id": 29, "adm": "ADM-562018", "first": "Khadija", "middle": "Ali", "last": "Warsame",
        "gender": "Female", "class_id": 157, "g_name": "Ali Warsame", "g_phone": "+252 61 7000013", "g_rel": "Father"
    },
    {
        "id": 30, "adm": "ADM-652157", "first": "Hassan", "middle": "Omar", "last": "Jama",
        "gender": "Male", "class_id": 157, "g_name": "Omar Jama", "g_phone": "+252 61 7000014", "g_rel": "Father"
    },
    {
        "id": 134, "adm": "ADM-477791", "first": "Dahir", "middle": "Abdi", "last": "Mohamed",
        "gender": "Male", "class_id": 157, "g_name": "Abdi Mohamed", "g_phone": "+252 61 7000015", "g_rel": "Father"
    },
    # Form 2 - A (ID 56)
    {
        "id": 243, "adm": "ADM-869228", "first": "Fadumo", "middle": "Ali", "last": "Warsame",
        "gender": "Female", "class_id": 56, "g_name": "Ali Warsame", "g_phone": "+252 61 7000016", "g_rel": "Father"
    },
    {
        "id": 74, "adm": "ADM-PROM-5-1-1580", "first": "Mohamed", "middle": "Ali", "last": "Mire",
        "gender": "Male", "class_id": 56, "g_name": "Ali Mire", "g_phone": "+252 61 7000017", "g_rel": "Father"
    },
    {
        "id": 62, "adm": "ADM-PROM-1-1-1580", "first": "Abdirashid", "middle": "Nur", "last": "Elmi",
        "gender": "Male", "class_id": 56, "g_name": "Nur Elmi", "g_phone": "+252 61 7000018", "g_rel": "Father"
    },
    {
        "id": 63, "adm": "ADM-PROM-1-2-1580", "first": "Nimo", "middle": "Ahmed", "last": "Farah",
        "gender": "Female", "class_id": 56, "g_name": "Ahmed Farah", "g_phone": "+252 61 7000019", "g_rel": "Father"
    },
    {
        "id": 64, "adm": "ADM-PROM-1-3-1580", "first": "Sahra", "middle": "Jama", "last": "Hussein",
        "gender": "Female", "class_id": 56, "g_name": "Jama Hussein", "g_phone": "+252 61 7000020", "g_rel": "Father"
    },
]

def execute_cleanup():
    db = SessionLocal()
    try:
        print("==================================================")
        print("STARTING AUTHORITATIVE STUDENT DATABASE CLEANUP")
        print("==================================================")

        all_students = db.query(Student).all()
        total_students_count = len(all_students)
        print(f"Total students before cleanup: {total_students_count}")

        retained_specs = PRIMARY_RETAINED + SECONDARY_RETAINED
        retained_ids = set(s["id"] for s in retained_specs)
        assert len(retained_ids) == 20, f"Expected 20 unique retained IDs, got {len(retained_ids)}"

        # Validate existence of all 20 retained students
        for spec in retained_specs:
            st = db.get(Student, spec["id"])
            if not st:
                raise ValueError(f"Required retained student ID {spec['id']} not found in DB!")

        delete_students = [s for s in all_students if s.id not in retained_ids]
        delete_ids = [s.id for s in delete_students]
        delete_count = len(delete_ids)
        print(f"Retained students: {len(retained_ids)}")
        print(f"Students to delete: {delete_count}")

        # Gather user IDs belonging to deleted students
        deleted_user_ids = set(s.user_id for s in delete_students if s.user_id is not None)
        # Safety guard: ensure no admin or teacher user_id is in deleted_user_ids
        admin_users = set(u.id for u in db.query(User).filter(User.is_superuser == True).all())
        teacher_users = set(t.user_id for t in db.query(Teacher).filter(Teacher.user_id != None).all())
        protected_users = admin_users.union(teacher_users)

        conflicting = deleted_user_ids.intersection(protected_users)
        if conflicting:
            raise RuntimeError(f"FATAL: Attempting to delete protected admin/teacher user IDs: {conflicting}")

        # Retained user IDs
        retained_user_ids = set(db.get(Student, sid).user_id for sid in retained_ids if db.get(Student, sid).user_id is not None)
        deleted_user_ids = deleted_user_ids - retained_user_ids
        print(f"Student portal user accounts to clean: {len(deleted_user_ids)}")

        # Step 1: Clean dependent records of deleted students in FK-safe order
        print("\n--- Cleaning dependent records for 388 deleted students ---")

        # 1.1 Notification deliveries for notifications belonging to deleted students
        del_notif_ids = [r[0] for r in db.query(Notification.id).filter(Notification.student_id.in_(delete_ids)).all()]
        if del_notif_ids:
            nd_cnt = db.execute(
                text("DELETE FROM notification_deliveries WHERE notification_id = ANY(:nids)"),
                {"nids": del_notif_ids}
            ).rowcount
            print(f"Deleted notification deliveries: {nd_cnt}")

        # 1.2 Notifications
        notif_cnt = db.query(Notification).filter(Notification.student_id.in_(delete_ids)).delete(synchronize_session=False)
        print(f"Deleted student notifications: {notif_cnt}")

        # 1.3 Fee payments (MUST be deleted before student_fees because of ON DELETE RESTRICT)
        # Also clean payments referencing deleted student_fees even if student_id was somehow different
        del_fee_ids = [r[0] for r in db.query(StudentFee.id).filter(StudentFee.student_id.in_(delete_ids)).all()]
        pay_cnt = 0
        if delete_ids:
            pay_cnt += db.query(FeePayment).filter(FeePayment.student_id.in_(delete_ids)).delete(synchronize_session=False)
        if del_fee_ids:
            pay_cnt += db.query(FeePayment).filter(FeePayment.student_fee_id.in_(del_fee_ids)).delete(synchronize_session=False)
        print(f"Deleted fee payments: {pay_cnt}")

        # 1.4 Student fees (invoices)
        fee_cnt = db.query(StudentFee).filter(StudentFee.student_id.in_(delete_ids)).delete(synchronize_session=False)
        print(f"Deleted student fees (invoices): {fee_cnt}")

        # 1.5 Exam results
        exam_cnt = db.query(ExamResult).filter(ExamResult.student_id.in_(delete_ids)).delete(synchronize_session=False)
        print(f"Deleted exam results: {exam_cnt}")

        # 1.6 Student result views
        srv_cnt = db.query(StudentResultView).filter(StudentResultView.student_id.in_(delete_ids)).delete(synchronize_session=False)
        print(f"Deleted student result views: {srv_cnt}")

        # 1.7 Attendances
        att_cnt = db.query(Attendance).filter(Attendance.student_id.in_(delete_ids)).delete(synchronize_session=False)
        print(f"Deleted attendance records: {att_cnt}")

        # 1.8 Class promotion records
        prom_cnt = db.query(ClassPromotionRecord).filter(ClassPromotionRecord.student_id.in_(delete_ids)).delete(synchronize_session=False)
        print(f"Deleted class promotion records: {prom_cnt}")

        # 1.9 Student enrollments
        enr_cnt = db.query(StudentEnrollment).filter(StudentEnrollment.student_id.in_(delete_ids)).delete(synchronize_session=False)
        print(f"Deleted student enrollments: {enr_cnt}")

        # 1.10 Students
        st_del_cnt = db.query(Student).filter(Student.id.in_(delete_ids)).delete(synchronize_session=False)
        print(f"Deleted students: {st_del_cnt}")

        # 1.11 Student Portal User accounts for deleted students
        if deleted_user_ids:
            del_u_list = list(deleted_user_ids)
            ur_cnt = db.execute(text("DELETE FROM user_roles WHERE user_id = ANY(:uids)"), {"uids": del_u_list}).rowcount
            sess_cnt = db.execute(text("DELETE FROM sessions WHERE user_id = ANY(:uids)"), {"uids": del_u_list}).rowcount
            u_cnt = db.execute(text("DELETE FROM users WHERE id = ANY(:uids)"), {"uids": del_u_list}).rowcount
            print(f"Deleted student portal users: {u_cnt} (roles: {ur_cnt}, sessions: {sess_cnt})")

        # Step 2: Clean invalid, test, and duplicate classes
        print("\n--- Cleaning invalid/test/duplicate classes ---")
        # List of invalid / test class names or IDs
        invalid_class_ids = [
            181, 182, 183, 184, 185, 186, 187, 188, 189, 190,
            173, 175, 177, 178, 179, 191, 192, 161, 159, 59, 60
        ]
        # Also any class that has 'test' or '12subj' in name
        extra_test_classes = db.query(SchoolClass).filter(
            (SchoolClass.name.ilike("%test%")) |
            (SchoolClass.name.ilike("%12subj%"))
        ).all()
        for ec in extra_test_classes:
            if ec.id not in invalid_class_ids:
                invalid_class_ids.append(ec.id)

        # Ensure canonical classes (147, 32, 157, 56, 1, 25, 31, 33, 34, 57, 58) are NOT in invalid_class_ids
        canonical_class_ids = {147, 32, 157, 56}
        invalid_class_ids = [cid for cid in invalid_class_ids if cid not in canonical_class_ids]

        # Before deleting these classes, remove any lingering foreign key references to them
        for cid in invalid_class_ids:
            cls_obj = db.get(SchoolClass, cid)
            if cls_obj:
                # Delete teacher assignments on test classes
                db.execute(text("DELETE FROM teacher_assignments WHERE class_id = :cid"), {"cid": cid})
                # Delete timetables on test classes
                db.execute(text("DELETE FROM timetables WHERE class_id = :cid"), {"cid": cid})
                # Delete exam results on test classes
                db.execute(text("DELETE FROM exam_results WHERE class_id = :cid"), {"cid": cid})
                # Delete result submissions on test classes
                db.execute(text("DELETE FROM result_submissions WHERE class_id = :cid"), {"cid": cid})
                # Delete exams on test classes
                db.execute(text("DELETE FROM exams WHERE class_id = :cid"), {"cid": cid})
                # Delete fee structures on test classes
                db.execute(text("DELETE FROM fee_structures WHERE class_id = :cid"), {"cid": cid})
                # Delete enrollments on test classes
                db.execute(text("DELETE FROM student_enrollments WHERE class_id = :cid"), {"cid": cid})
                # Delete notifications with class_id
                db.execute(text("UPDATE notifications SET class_id = NULL WHERE class_id = :cid"), {"cid": cid})
                # Delete promotion records referencing this class
                db.execute(text("DELETE FROM class_promotion_records WHERE from_class_id = :cid OR to_class_id = :cid"), {"cid": cid})
                db.delete(cls_obj)
                print(f"Deleted invalid/test class [{cid}] {cls_obj.name}")

        # Step 3: Normalize the 20 Retained Students
        print("\n--- Normalizing 20 retained students ---")
        student_role = db.query(Role).filter(Role.name == "STUDENT").first()
        academic_year = "2026/2027"

        for spec in retained_specs:
            st = db.get(Student, spec["id"])
            st.first_name = spec["first"]
            st.middle_name = spec["middle"]
            st.last_name = spec["last"]
            st.admission_number = spec["adm"]
            st.gender = spec["gender"]
            st.guardian_name = spec["g_name"]
            st.guardian_phone = spec["g_phone"]
            st.guardian_relationship = spec["g_rel"]
            st.status = "ACTIVE"

            # Check or create student portal user account
            if not st.user_id:
                clean_username = f"student.{spec['first'].lower()}.{st.id}"
                u = User(
                    email=f"{clean_username}@student.hawlwadaagschool.edu.so",
                    username=clean_username,
                    hashed_password=get_password_hash("Student@Hawlwadaag2026"),
                    full_name=f"{spec['first']} {spec['middle']} {spec['last']}",
                    phone_number=spec["g_phone"],
                    is_active=True,
                    is_superuser=False
                )
                db.add(u)
                db.flush()
                st.user_id = u.id
                db.add(UserRole(user_id=u.id, role_id=student_role.id))
                db.flush()
            else:
                # Ensure user is active and full name matches
                u = db.get(User, st.user_id)
                if u:
                    u.full_name = f"{spec['first']} {spec['middle']} {spec['last']}"
                    u.is_active = True
                    # Ensure role STUDENT is present
                    has_role = any(r.name == "STUDENT" for r in u.roles)
                    if not has_role and student_role:
                        db.add(UserRole(user_id=u.id, role_id=student_role.id))

            # Normalize Enrollments:
            # Note: UniqueConstraint("student_id", "academic_year")
            # If student already has enrollment in '2026/2027', update its class_id and status.
            # If student has enrollment in '2026-2027', clean it up to prevent collision.
            db.execute(
                text("DELETE FROM student_enrollments WHERE student_id = :sid AND academic_year = '2026-2027'"),
                {"sid": st.id}
            )

            enr_2026 = db.query(StudentEnrollment).filter(
                StudentEnrollment.student_id == st.id,
                StudentEnrollment.academic_year == academic_year
            ).first()

            if enr_2026:
                enr_2026.class_id = spec["class_id"]
                enr_2026.status = "ACTIVE"
                enr_2026.start_date = date(2026, 9, 1)
            else:
                new_enr = StudentEnrollment(
                    student_id=st.id,
                    class_id=spec["class_id"],
                    academic_year=academic_year,
                    start_date=date(2026, 9, 1),
                    status="ACTIVE"
                )
                db.add(new_enr)

            # Ensure any historical 2025/2026 enrollments are marked COMPLETED
            for h_enr in db.query(StudentEnrollment).filter(
                StudentEnrollment.student_id == st.id,
                StudentEnrollment.academic_year.in_(["2025/2026", "2025-2026"])
            ).all():
                h_enr.status = "COMPLETED"

            target_class = db.get(SchoolClass, spec["class_id"])
            print(f"  [OK] Student {st.id:3d} ({st.admission_number}): {st.full_name} -> {target_class.name} ({academic_year})")

        # Step 4: Ensure Teacher Assignments exist for Form 2 - A (Class ID 56)
        print("\n--- Verifying Teacher Assignments for Canonical Classes ---")
        f2_class = db.get(SchoolClass, 56)
        if f2_class:
            # Check existing TAs
            f2_tas = db.query(TeacherAssignment).filter(TeacherAssignment.class_id == 56).all()
            if not f2_tas:
                # Assign core teachers to Form 2 - A
                t1 = db.query(Teacher).filter(Teacher.teacher_number == "TCH-001").first()
                t2 = db.query(Teacher).filter(Teacher.teacher_number == "TCH-002").first()
                t3 = db.query(Teacher).filter(Teacher.teacher_number == "TCH-003").first()
                s_math = db.query(Subject).filter(Subject.name == "Mathematics").first()
                s_eng = db.query(Subject).filter(Subject.name == "English Language").first()
                s_isl = db.query(Subject).filter(Subject.name == "Arabic & Islamic Studies").first()

                if t1 and s_math:
                    db.add(TeacherAssignment(teacher_id=t1.id, class_id=56, subject_id=s_math.id, academic_year=academic_year, status="ACTIVE"))
                if t2 and s_eng:
                    db.add(TeacherAssignment(teacher_id=t2.id, class_id=56, subject_id=s_eng.id, academic_year=academic_year, status="ACTIVE"))
                if t3 and s_isl:
                    db.add(TeacherAssignment(teacher_id=t3.id, class_id=56, subject_id=s_isl.id, academic_year=academic_year, status="ACTIVE"))
                print("  Added teacher assignments for Form 2 - A (Math, English, Islamic Studies)")

        # Commit transaction
        db.commit()
        print("\n==================================================")
        print("[SUCCESS] ALL CLEANUP OPERATIONS COMMITTED SAFELY!")
        print("==================================================")

    except Exception as exc:
        db.rollback()
        print(f"\n[ERROR] Transaction rolled back due to error: {exc}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    execute_cleanup()
