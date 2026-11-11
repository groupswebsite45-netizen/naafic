"""
Seed script to initialize core roles, system settings, initial Admin,
and realistic school foundation records (Classes, Subjects, Teachers, Students, Timetables, Fees, Exams).

Usage:
    python backend/scripts/seed.py
"""
import sys
import os
from datetime import date, time, datetime, timedelta, timezone
from decimal import Decimal

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal, engine, Base
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.role import Role
from app.models.user import User
from app.models.user_role import UserRole
from app.models.system_setting import SystemSetting
from app.models.school_class import SchoolClass
from app.models.subject import Subject
from app.models.teacher import Teacher
from app.models.teacher_assignment import TeacherAssignment
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.models.timetable import Timetable
from app.models.fee import FeeStructure, StudentFee, FeePayment
from app.models.exam import Exam, ExamResult
from app.utils.logger import logger


def run_seed():
    """Execute complete PostgreSQL database seed."""
    logger.info("Verifying tables in PostgreSQL database...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # =========================================================================
        # 1. ROLES
        # =========================================================================
        roles_data = [
            ("ADMIN", "System and school administrator with full management access", True),
            ("TEACHER", "Academic faculty member managing attendance, schedule and grades", True),
            ("STUDENT", "Enrolled student accessing timetable, fees, and exam results", True),
            ("PARENT", "Parent or legal guardian monitoring student progress", True),
            ("STAFF", "Administrative and supporting school staff", True),
        ]
        created_roles = {}
        for r_name, r_desc, is_sys in roles_data:
            role = db.query(Role).filter(Role.name == r_name).first()
            if not role:
                role = Role(name=r_name, description=r_desc, is_system=is_sys)
                db.add(role)
                db.commit()
                db.refresh(role)
            created_roles[r_name] = role

        # =========================================================================
        # 2. SYSTEM SETTINGS
        # =========================================================================
        default_settings = [
            ("school_name", "Hawlwadaag Primary and Secondary School", "Official school institution name", True),
            ("school_short_name", "Hawlwadaag School", "Abbreviated school name", True),
            ("school_motto", "Excellence in Education and Character", "Official school motto", True),
            ("school_email", "info@hawlwadaagschool.edu.so", "Official contact email", True),
            ("school_phone", "+252 61 0000000", "Official contact phone number", True),
            ("school_address", "Hawlwadaag District, Mogadishu, Somalia", "Physical campus location", True),
            ("primary_color", "#1e3a8a", "Primary school theme branding color", True),
            ("secondary_color", "#0284c7", "Secondary theme branding color", True),
            ("academic_year_current", "2025-2026", "Current active academic year", True),
        ]
        for k, v, d, p in default_settings:
            s = db.query(SystemSetting).filter(SystemSetting.key == k).first()
            if not s:
                s = SystemSetting(key=k, value=v, description=d, is_public=p)
                db.add(s)
        db.commit()

        # =========================================================================
        # 3. INITIAL ADMIN USER
        # =========================================================================
        admin_email = settings.INITIAL_ADMIN_EMAIL.lower().strip()
        admin_username = settings.INITIAL_ADMIN_USERNAME.lower().strip()
        admin_user = db.query(User).filter(User.username == admin_username).first()
        if not admin_user:
            admin_user = User(
                email=admin_email,
                username=admin_username,
                hashed_password=get_password_hash(settings.INITIAL_ADMIN_PASSWORD),
                full_name=settings.INITIAL_ADMIN_FULL_NAME,
                phone_number="+252 61 1234567",
                is_active=True,
                is_superuser=True
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)

            db.add(UserRole(user_id=admin_user.id, role_id=created_roles["ADMIN"].id))
            db.commit()
            logger.info("Admin user created.")
        else:
            admin_user.hashed_password = get_password_hash(settings.INITIAL_ADMIN_PASSWORD)
            admin_user.is_active = True
            db.commit()
            logger.info("Admin user password refreshed.")

        # =========================================================================
        # 4. CLASSES
        # =========================================================================
        classes_data = [
            ("Grade 1", "G1-A", "Section A", "2025-2026", 40, "Primary School Grade 1"),
            ("Grade 2", "G2-A", "Section A", "2025-2026", 40, "Primary School Grade 2"),
            ("Grade 3", "G3-A", "Section A", "2025-2026", 40, "Primary School Grade 3"),
            ("Grade 4", "G4-A", "Section A", "2025-2026", 40, "Primary School Grade 4"),
            ("Grade 5", "G5-A", "Section A", "2025-2026", 40, "Primary School Grade 5"),
            ("Grade 6", "G6-A", "Section A", "2025-2026", 40, "Primary School Grade 6"),
            ("Grade 7", "G7-A", "Section A", "2025-2026", 45, "Middle School Grade 7"),
            ("Grade 8", "G8-A", "Section A", "2025-2026", 45, "Middle School Grade 8 (Primary Leaving)"),
            ("Form 1", "F1-A", "Science Stream", "2025-2026", 45, "Secondary School Form 1"),
            ("Form 2", "F2-A", "Science Stream", "2025-2026", 45, "Secondary School Form 2"),
            ("Form 3", "F3-A", "Science Stream", "2025-2026", 45, "Secondary School Form 3"),
            ("Form 4", "F4-A", "Science Stream", "2025-2026", 45, "Secondary School Form 4 (National Cert)"),
        ]
        created_classes = {}
        for c_name, c_code, sec, year, cap, desc in classes_data:
            c = db.query(SchoolClass).filter(SchoolClass.code == c_code).first()
            if not c:
                c = SchoolClass(name=c_name, code=c_code, section=sec, academic_year=year, capacity=cap, description=desc, status="ACTIVE")
                db.add(c)
                db.commit()
                db.refresh(c)
            created_classes[c_code] = c

        # =========================================================================
        # 5. SUBJECTS
        # =========================================================================
        subjects_data = [
            ("Mathematics", "MATH-101", "Mathematics & Logic", "Core Mathematics & Algebra"),
            ("Somali Language & Literature", "SOM-101", "Languages", "Somali Grammar, Composition & Literature"),
            ("English Language", "ENG-101", "Languages", "Grammar, Reading, Writing & Oral Skills"),
            ("Arabic & Islamic Studies", "ISL-101", "Religious Studies", "Quranic Studies, Hadith, Fiqh & Arabic"),
            ("Integrated Science", "SCI-101", "Sciences", "Physics, Chemistry and Biology Fundamentals"),
            ("Physics", "PHY-201", "Sciences", "Mechanics, Thermodynamics, Optics & Electricity"),
            ("Chemistry", "CHEM-201", "Sciences", "Organic & Inorganic Chemistry"),
            ("Biology", "BIO-201", "Sciences", "Cellular Biology, Human Anatomy & Ecology"),
            ("Social Studies & Geography", "SOC-101", "Social Sciences", "Somali History, World Geography & Civics"),
            ("ICT & Computer Studies", "ICT-101", "Technology", "Digital Literacy, Office Tools & Coding Basics"),
        ]
        created_subjects = {}
        for s_name, s_code, dept, desc in subjects_data:
            s = db.query(Subject).filter(Subject.code == s_code).first()
            if not s:
                s = Subject(name=s_name, code=s_code, department=dept, description=desc, status="ACTIVE")
                db.add(s)
                db.commit()
                db.refresh(s)
            created_subjects[s_code] = s

        # =========================================================================
        # 6. TEACHERS (WITH PORTAL ACCOUNTS)
        # =========================================================================
        teachers_data = [
            ("TCH-001", "Ahmed", "Hassan", "Ali", "Male", "ahmed.ali@hawlwadaagschool.edu.so", "+252 61 5111111", "B.Ed Mathematics & Physics", "teacher.ahmed"),
            ("TCH-002", "Fadumo", "Mohamed", "Warsame", "Female", "fadumo.warsame@hawlwadaagschool.edu.so", "+252 61 5222222", "M.A. English & Literature", "teacher.fadumo"),
            ("TCH-003", "Sheikh", "Omar", "Abdirahman", "Male", "omar.abdirahman@hawlwadaagschool.edu.so", "+252 61 5333333", "B.A. Islamic Studies & Arabic", "teacher.omar"),
            ("TCH-004", "Khadija", "Osman", "Guled", "Female", "khadija.guled@hawlwadaagschool.edu.so", "+252 61 5444444", "B.Sc. Chemistry & Biology", "teacher.khadija"),
            ("TCH-005", "Abdi", "Nur", "Farah", "Male", "abdi.farah@hawlwadaagschool.edu.so", "+252 61 5555555", "B.Sc. Computer Science & IT", "teacher.abdi"),
        ]
        created_teachers = {}
        teacher_role = created_roles["TEACHER"]
        for t_no, f_name, m_name, l_name, gender, email, phone, qual, username in teachers_data:
            t = db.query(Teacher).filter(Teacher.teacher_number == t_no).first()
            if not t:
                # Create user for teacher
                u = db.query(User).filter(User.username == username).first()
                if not u:
                    u = User(
                        email=email,
                        username=username,
                        hashed_password=get_password_hash("Teacher@Hawlwadaag2026"),
                        full_name=f"{f_name} {m_name} {l_name}",
                        phone_number=phone,
                        is_active=True,
                        is_superuser=False
                    )
                    db.add(u)
                    db.commit()
                    db.refresh(u)
                    db.add(UserRole(user_id=u.id, role_id=teacher_role.id))
                    db.commit()

                t = Teacher(
                    user_id=u.id,
                    teacher_number=t_no,
                    first_name=f_name,
                    middle_name=m_name,
                    last_name=l_name,
                    gender=gender,
                    date_of_birth=date(1988, 5, 12),
                    phone=phone,
                    email=email,
                    address="Hawlwadaag, Mogadishu",
                    qualification=qual,
                    hire_date=date(2022, 8, 15),
                    status="ACTIVE"
                )
                db.add(t)
                db.commit()
                db.refresh(t)
            created_teachers[t_no] = t

        # =========================================================================
        # 7. TEACHER CLASS & SUBJECT ASSIGNMENTS
        # =========================================================================
        assignments_data = [
            # Teacher Ahmed -> Grade 7, Grade 8, Form 1 (Mathematics, Physics)
            ("TCH-001", "G7-A", "MATH-101", "2025-2026"),
            ("TCH-001", "G8-A", "MATH-101", "2025-2026"),
            ("TCH-001", "F1-A", "PHY-201", "2025-2026"),
            # Teacher Fadumo -> Grade 7, Grade 8, Form 1 (English, Somali)
            ("TCH-002", "G7-A", "ENG-101", "2025-2026"),
            ("TCH-002", "G8-A", "ENG-101", "2025-2026"),
            ("TCH-002", "G7-A", "SOM-101", "2025-2026"),
            # Teacher Omar -> Grade 7, Grade 8, Form 1 (Islamic Studies)
            ("TCH-003", "G7-A", "ISL-101", "2025-2026"),
            ("TCH-003", "G8-A", "ISL-101", "2025-2026"),
            # Teacher Khadija -> Grade 7, Grade 8, Form 1 (Science, Chemistry, Biology)
            ("TCH-004", "G7-A", "SCI-101", "2025-2026"),
            ("TCH-004", "F1-A", "CHEM-201", "2025-2026"),
            ("TCH-004", "F1-A", "BIO-201", "2025-2026"),
            # Teacher Abdi -> Grade 7, Grade 8, Form 1 (ICT)
            ("TCH-005", "G7-A", "ICT-101", "2025-2026"),
            ("TCH-005", "F1-A", "ICT-101", "2025-2026"),
        ]
        for t_no, c_code, s_code, year in assignments_data:
            t = created_teachers.get(t_no)
            c = created_classes.get(c_code)
            s = created_subjects.get(s_code)
            if t and c and s:
                existing = db.query(TeacherAssignment).filter(
                    TeacherAssignment.teacher_id == t.id,
                    TeacherAssignment.class_id == c.id,
                    TeacherAssignment.subject_id == s.id,
                    TeacherAssignment.academic_year == year
                ).first()
                if not existing:
                    db.add(TeacherAssignment(
                        teacher_id=t.id,
                        class_id=c.id,
                        subject_id=s.id,
                        academic_year=year,
                        status="ACTIVE"
                    ))
        db.commit()

        # =========================================================================
        # 8. STUDENTS (WITH ENROLLMENTS & PORTAL ACCOUNTS)
        # =========================================================================
        students_data = [
            ("ADM-2026-001", "Mustaf", "Ali", "Yusuf", "Male", "G7-A", "student.mustaf", "Ali Yusuf", "+252 61 7000001", "Father"),
            ("ADM-2026-002", "Amina", "Hassan", "Ibrahim", "Female", "G7-A", "student.amina", "Hassan Ibrahim", "+252 61 7000002", "Father"),
            ("ADM-2026-003", "Liban", "Abdirahman", "Elmi", "Male", "G7-A", "student.liban", "Mariam Noor", "+252 61 7000003", "Mother"),
            ("ADM-2026-004", "Hafsa", "Mohamud", "Adan", "Female", "G7-A", "student.hafsa", "Mohamud Adan", "+252 61 7000004", "Father"),
            ("ADM-2026-005", "Zakarie", "Jama", "Hussein", "Male", "G8-A", "student.zakarie", "Jama Hussein", "+252 61 7000005", "Father"),
            ("ADM-2026-006", "Safia", "Farah", "Gedi", "Female", "G8-A", "student.safia", "Farah Gedi", "+252 61 7000006", "Father"),
            ("ADM-2026-007", "Khaalid", "Ibrahim", "Nur", "Male", "F1-A", "student.khaalid", "Ibrahim Nur", "+252 61 7000007", "Father"),
            ("ADM-2026-008", "Yasmin", "Osman", "Roble", "Female", "F1-A", "student.yasmin", "Osman Roble", "+252 61 7000008", "Father"),
        ]
        created_students = {}
        student_role = created_roles["STUDENT"]
        for adm_no, f_name, m_name, l_name, gender, c_code, username, g_name, g_phone, g_rel in students_data:
            st = db.query(Student).filter(Student.admission_number == adm_no).first()
            if not st:
                # Create User for Student Portal
                u = db.query(User).filter(User.username == username).first()
                if not u:
                    u = User(
                        email=f"{username}@student.hawlwadaagschool.edu.so",
                        username=username,
                        hashed_password=get_password_hash("Student@Hawlwadaag2026"),
                        full_name=f"{f_name} {m_name} {l_name}",
                        phone_number=g_phone,
                        is_active=True,
                        is_superuser=False
                    )
                    db.add(u)
                    db.commit()
                    db.refresh(u)
                    db.add(UserRole(user_id=u.id, role_id=student_role.id))
                    db.commit()

                st = Student(
                    user_id=u.id,
                    admission_number=adm_no,
                    first_name=f_name,
                    middle_name=m_name,
                    last_name=l_name,
                    gender=gender,
                    date_of_birth=date(2011, 4, 20),
                    guardian_name=g_name,
                    guardian_phone=g_phone,
                    guardian_relationship=g_rel,
                    admission_date=date(2025, 9, 1),
                    status="ACTIVE"
                )
                db.add(st)
                db.commit()
                db.refresh(st)

                # Enroll into class
                c = created_classes.get(c_code)
                if c:
                    db.add(StudentEnrollment(
                        student_id=st.id,
                        class_id=c.id,
                        academic_year="2025-2026",
                        start_date=date(2025, 9, 1),
                        status="ACTIVE"
                    ))
                    db.commit()

            created_students[adm_no] = st

        # =========================================================================
        # 9. TIMETABLE SCHEDULE
        # =========================================================================
        timetables_data = [
            # Grade 7-A Schedule
            ("G7-A", "MATH-101", "TCH-001", "2025-2026", "Monday", time(8, 0), time(9, 0), "Room 101"),
            ("G7-A", "ENG-101", "TCH-002", "2025-2026", "Monday", time(9, 15), time(10, 15), "Room 101"),
            ("G7-A", "ISL-101", "TCH-003", "2025-2026", "Monday", time(10, 30), time(11, 30), "Room 101"),
            ("G7-A", "SCI-101", "TCH-004", "2025-2026", "Tuesday", time(8, 0), time(9, 0), "Science Lab"),
            ("G7-A", "ICT-101", "TCH-005", "2025-2026", "Tuesday", time(9, 15), time(10, 15), "Computer Lab"),
            ("G7-A", "SOM-101", "TCH-002", "2025-2026", "Wednesday", time(8, 0), time(9, 0), "Room 101"),
            # Grade 8-A Schedule
            ("G8-A", "MATH-101", "TCH-001", "2025-2026", "Monday", time(9, 15), time(10, 15), "Room 102"),
            ("G8-A", "ENG-101", "TCH-002", "2025-2026", "Monday", time(8, 0), time(9, 0), "Room 102"),
            ("G8-A", "ISL-101", "TCH-003", "2025-2026", "Tuesday", time(8, 0), time(9, 0), "Room 102"),
        ]
        for c_code, s_code, t_no, year, day, start_t, end_t, room in timetables_data:
            c = created_classes.get(c_code)
            s = created_subjects.get(s_code)
            t = created_teachers.get(t_no)
            if c and s:
                existing = db.query(Timetable).filter(
                    Timetable.class_id == c.id,
                    Timetable.day_of_week == day,
                    Timetable.start_time == start_t,
                    Timetable.academic_year == year
                ).first()
                if not existing:
                    db.add(Timetable(
                        class_id=c.id,
                        subject_id=s.id,
                        teacher_id=t.id if t else None,
                        academic_year=year,
                        day_of_week=day,
                        start_time=start_t,
                        end_time=end_t,
                        room=room,
                        status="ACTIVE"
                    ))
        db.commit()

        # =========================================================================
        # 10. FEE STRUCTURES, STUDENT INVOICES & PAYMENT RECEIPTS
        # =========================================================================
        structures_data = [
            ("Term 1 Tuition Fee (Grade 7)", "2025-2026", "G7-A", Decimal("120.00"), date(2025, 10, 15), "Primary/Middle Tuition Fee for Term 1"),
            ("Term 1 Tuition Fee (Grade 8)", "2025-2026", "G8-A", Decimal("130.00"), date(2025, 10, 15), "Grade 8 Tuition & Exam Registration Fee"),
            ("Term 1 Tuition Fee (Form 1)", "2025-2026", "F1-A", Decimal("150.00"), date(2025, 10, 15), "Secondary School Form 1 Tuition & Science Lab Fee"),
        ]
        for name, year, c_code, amt, due, desc in structures_data:
            c = created_classes.get(c_code)
            fs = db.query(FeeStructure).filter(FeeStructure.name == name, FeeStructure.academic_year == year).first()
            if not fs:
                fs = FeeStructure(
                    name=name,
                    academic_year=year,
                    class_id=c.id if c else None,
                    amount=amt,
                    due_date=due,
                    description=desc,
                    status="ACTIVE"
                )
                db.add(fs)
                db.commit()
                db.refresh(fs)

                # Assign invoices to students in that class
                if c:
                    enrollments = db.query(StudentEnrollment).filter(
                        StudentEnrollment.class_id == c.id,
                        StudentEnrollment.academic_year == year,
                        StudentEnrollment.status == "ACTIVE"
                    ).all()

                    for en in enrollments:
                        sf = StudentFee(
                            invoice_number=f"INV-{year[:4]}-{fs.id:03d}-{en.student_id:04d}",
                            student_id=en.student_id,
                            class_id=c.id,
                            fee_structure_id=fs.id,
                            academic_year=year,
                            fee_type="Tuition Fee",
                            amount_due=amt,
                            discount_amount=Decimal("0.00"),
                            due_date=due,
                            status="PENDING"
                        )
                        db.add(sf)
                        db.commit()
                        db.refresh(sf)

                        # Record partial payment for Mustaf Ali (ADM-2026-001)
                        if en.student.admission_number == "ADM-2026-001":
                            pmt = FeePayment(
                                student_fee_id=sf.id,
                                student_id=en.student_id,
                                receipt_number=f"REC-2026-{sf.id:05d}",
                                amount_paid=Decimal("80.00"),
                                payment_date=date(2025, 10, 10),
                                payment_method="EVC Plus",
                                reference_number="EVC-994821",
                                recorded_by_id=admin_user.id,
                                notes="Partial payment received via EVC Plus"
                            )
                            db.add(pmt)
                            sf.status = "PARTIALLY_PAID"
                            db.commit()

        # =========================================================================
        # 11. EXAMS & EXAM RESULTS
        # =========================================================================
        exams_data = [
            ("Mid-Term Mathematics Exam", "Mid-Term", "2025-2026", "G7-A", "MATH-101", date(2025, 11, 10), Decimal("100.00"), Decimal("50.00")),
            ("Mid-Term English Language Exam", "Mid-Term", "2025-2026", "G7-A", "ENG-101", date(2025, 11, 12), Decimal("100.00"), Decimal("50.00")),
            ("Mid-Term Islamic Studies Exam", "Mid-Term", "2025-2026", "G7-A", "ISL-101", date(2025, 11, 14), Decimal("100.00"), Decimal("50.00")),
        ]
        for e_name, e_type, year, c_code, s_code, s_date, max_m, pass_m in exams_data:
            c = created_classes.get(c_code)
            s = created_subjects.get(s_code)
            if c and s:
                ex = db.query(Exam).filter(Exam.name == e_name, Exam.class_id == c.id, Exam.subject_id == s.id).first()
                if not ex:
                    ex = Exam(
                        name=e_name,
                        exam_type=e_type,
                        academic_year=year,
                        class_id=c.id,
                        subject_id=s.id,
                        start_date=s_date,
                        max_marks=max_m,
                        pass_marks=pass_m,
                        status="COMPLETED"
                    )
                    db.add(ex)
                    db.commit()
                    db.refresh(ex)

                    # Enter results for Grade 7 students
                    g7_students = db.query(Student).join(StudentEnrollment).filter(
                        StudentEnrollment.class_id == c.id,
                        StudentEnrollment.status == "ACTIVE"
                    ).all()

                    sample_scores = [Decimal("88.50"), Decimal("94.00"), Decimal("76.00"), Decimal("82.50")]
                    for idx, st in enumerate(g7_students):
                        score = sample_scores[idx % len(sample_scores)]
                        grade_val = "A" if score >= 80 else ("B" if score >= 70 else "C")
                        db.add(ExamResult(
                            exam_id=ex.id,
                            student_id=st.id,
                            subject_id=s.id,
                            marks_obtained=score,
                            grade=grade_val,
                            remarks="Good understanding of core principles",
                            recorded_by_id=admin_user.id
                        ))
                    db.commit()

        print("\n" + "="*70)
        print("DATABASE SEED COMPLETED SUCCESSFULLY FOR HAWLWADAAG SCHOOL")
        print("="*70)
        print(f"School Name: Hawlwadaag Primary and Secondary School")
        print(f"Admin Account:    admin / Admin@Hawlwadaag2026")
        print(f"Teacher Accounts: teacher.ahmed, teacher.fadumo, teacher.omar (Pwd: Teacher@Hawlwadaag2026)")
        print(f"Student Accounts: student.mustaf, student.amina, student.liban (Pwd: Student@Hawlwadaag2026)")
        print(f"Classes Seeded:   {len(classes_data)}")
        print(f"Subjects Seeded:  {len(subjects_data)}")
        print(f"Students Seeded:  {len(students_data)}")
        print("="*70 + "\n")

    except Exception as e:
        db.rollback()
        logger.error(f"Seed Error: {e}", exc_info=True)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
