import sys
import os
from collections import defaultdict
from sqlalchemy import text

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal, engine

def run_audit():
    print("=" * 80)
    print("SOMROYAL EMS - GLOBAL DUPLICATE DATA AUDIT")
    print("=" * 80)

    session = SessionLocal()
    try:
        # Check current database name
        db_name = session.execute(text("SELECT current_database();")).scalar()
        print(f"Connected to database: {db_name}\n")

        # ----------------------------------------------------
        # 1. TEACHERS AUDIT
        # ----------------------------------------------------
        print(">>> 1. AUDITING TEACHERS...")
        # A. Duplicate teacher_number
        dup_tch_numbers = session.execute(text("""
            SELECT LOWER(TRIM(teacher_number)) as norm_num, COUNT(*), array_agg(id) as ids, array_agg(teacher_number) as raw_nums
            FROM teachers
            GROUP BY LOWER(TRIM(teacher_number))
            HAVING COUNT(*) > 1;
        """)).fetchall()
        print(f"  - Duplicate Teacher Numbers: {len(dup_tch_numbers)}")
        for r in dup_tch_numbers:
            print(f"    * Number: {r.norm_num} (IDs: {r.ids}, Raw: {r.raw_nums})")

        # B. Duplicate email
        dup_tch_emails = session.execute(text("""
            SELECT LOWER(TRIM(email)) as norm_email, COUNT(*), array_agg(id) as ids, array_agg(email) as raw_emails
            FROM teachers
            WHERE email IS NOT NULL AND TRIM(email) != ''
            GROUP BY LOWER(TRIM(email))
            HAVING COUNT(*) > 1;
        """)).fetchall()
        print(f"  - Duplicate Teacher Emails: {len(dup_tch_emails)}")
        for r in dup_tch_emails:
            print(f"    * Email: {r.norm_email} (IDs: {r.ids}, Raw: {r.raw_emails})")

        # C. Duplicate phone
        dup_tch_phones = session.execute(text("""
            SELECT REGEXP_REPLACE(phone, '[^0-9]', '', 'g') as norm_phone, COUNT(*), array_agg(id) as ids, array_agg(phone) as raw_phones
            FROM teachers
            WHERE phone IS NOT NULL AND TRIM(phone) != ''
            GROUP BY REGEXP_REPLACE(phone, '[^0-9]', '', 'g')
            HAVING COUNT(*) > 1;
        """)).fetchall()
        print(f"  - Duplicate Teacher Phones: {len(dup_tch_phones)}")
        for r in dup_tch_phones:
            print(f"    * Phone: {r.norm_phone} (IDs: {r.ids}, Raw: {r.raw_phones})")

        # ----------------------------------------------------
        # 2. STUDENTS AUDIT
        # ----------------------------------------------------
        print("\n>>> 2. AUDITING STUDENTS...")
        # A. Duplicate admission_number
        dup_stu_adm = session.execute(text("""
            SELECT LOWER(TRIM(admission_number)) as norm_adm, COUNT(*), array_agg(id) as ids, array_agg(admission_number) as raw_adms
            FROM students
            GROUP BY LOWER(TRIM(admission_number))
            HAVING COUNT(*) > 1;
        """)).fetchall()
        print(f"  - Duplicate Admission Numbers: {len(dup_stu_adm)}")
        for r in dup_stu_adm:
            print(f"    * Admission: {r.norm_adm} (IDs: {r.ids}, Raw: {r.raw_adms})")

        # B. Duplicate phone
        dup_stu_phones = session.execute(text("""
            SELECT REGEXP_REPLACE(phone, '[^0-9]', '', 'g') as norm_phone, COUNT(*), array_agg(id) as ids, array_agg(phone) as raw_phones
            FROM students
            WHERE phone IS NOT NULL AND TRIM(phone) != ''
            GROUP BY REGEXP_REPLACE(phone, '[^0-9]', '', 'g')
            HAVING COUNT(*) > 1;
        """)).fetchall()
        print(f"  - Duplicate Student Phones: {len(dup_stu_phones)}")
        for r in dup_stu_phones:
            print(f"    * Phone: {r.norm_phone} (IDs: {r.ids}, Raw: {r.raw_phones})")

        # C. Potential duplicate students by full name + DOB
        dup_stu_names_dob = session.execute(text("""
            SELECT LOWER(TRIM(first_name)) as fn, LOWER(TRIM(last_name)) as ln, date_of_birth, COUNT(*), array_agg(id) as ids, array_agg(admission_number) as adms
            FROM students
            WHERE date_of_birth IS NOT NULL
            GROUP BY LOWER(TRIM(first_name)), LOWER(TRIM(last_name)), date_of_birth
            HAVING COUNT(*) > 1;
        """)).fetchall()
        print(f"  - Potential duplicate student records (Matching First+Last Name + DOB): {len(dup_stu_names_dob)}")
        for r in dup_stu_names_dob:
            print(f"    * Name: {r.fn} {r.ln}, DOB: {r.date_of_birth} (IDs: {r.ids}, Adms: {r.adms})")

        # ----------------------------------------------------
        # 3. SUBJECTS AUDIT
        # ----------------------------------------------------
        print("\n>>> 3. AUDITING SUBJECTS...")
        # A. Duplicate subject code
        dup_subj_codes = session.execute(text("""
            SELECT LOWER(TRIM(code)) as norm_code, COUNT(*), array_agg(id) as ids, array_agg(code) as raw_codes
            FROM subjects
            GROUP BY LOWER(TRIM(code))
            HAVING COUNT(*) > 1;
        """)).fetchall()
        print(f"  - Duplicate Subject Codes: {len(dup_subj_codes)}")
        for r in dup_subj_codes:
            print(f"    * Code: {r.norm_code} (IDs: {r.ids}, Raw: {r.raw_codes})")

        # B. Duplicate subject name within division
        dup_subj_names = session.execute(text("""
            SELECT LOWER(TRIM(name)) as norm_name, division, COUNT(*), array_agg(id) as ids, array_agg(name) as raw_names
            FROM subjects
            GROUP BY LOWER(TRIM(name)), division
            HAVING COUNT(*) > 1;
        """)).fetchall()
        print(f"  - Duplicate Subject Names (within division): {len(dup_subj_names)}")
        for r in dup_subj_names:
            print(f"    * Name: '{r.norm_name}' [Div: {r.division}] (IDs: {r.ids}, Raw: {r.raw_names})")

        # ----------------------------------------------------
        # 4. CLASSES AUDIT
        # ----------------------------------------------------
        print("\n>>> 4. AUDITING CLASSES...")
        # A. Duplicate class code
        dup_class_codes = session.execute(text("""
            SELECT LOWER(TRIM(code)) as norm_code, COUNT(*), array_agg(id) as ids, array_agg(code) as raw_codes
            FROM classes
            GROUP BY LOWER(TRIM(code))
            HAVING COUNT(*) > 1;
        """)).fetchall()
        print(f"  - Duplicate Class Codes: {len(dup_class_codes)}")
        for r in dup_class_codes:
            print(f"    * Code: {r.norm_code} (IDs: {r.ids}, Raw: {r.raw_codes})")

        # B. Duplicate academic_year + division + level + section
        dup_class_combos = session.execute(text("""
            SELECT academic_year, division, level, COALESCE(UPPER(TRIM(section)), '') as sec, COUNT(*), array_agg(id) as ids, array_agg(name) as names
            FROM classes
            GROUP BY academic_year, division, level, COALESCE(UPPER(TRIM(section)), '')
            HAVING COUNT(*) > 1;
        """)).fetchall()
        print(f"  - Duplicate (Year, Division, Level, Section) combinations: {len(dup_class_combos)}")
        for r in dup_class_combos:
            print(f"    * {r.academic_year} | {r.division} | {r.level} | Sec '{r.sec}' (IDs: {r.ids}, Names: {r.names})")

        # C. Duplicate Class Name within academic_year
        dup_class_names = session.execute(text("""
            SELECT academic_year, LOWER(TRIM(name)) as norm_name, COUNT(*), array_agg(id) as ids, array_agg(name) as raw_names
            FROM classes
            GROUP BY academic_year, LOWER(TRIM(name))
            HAVING COUNT(*) > 1;
        """)).fetchall()
        print(f"  - Duplicate Class Names within same academic year: {len(dup_class_names)}")
        for r in dup_class_names:
            print(f"    * Year: {r.academic_year}, Name: '{r.norm_name}' (IDs: {r.ids}, Raw: {r.raw_names})")

        # ----------------------------------------------------
        # 5. FEES AUDIT
        # ----------------------------------------------------
        print("\n>>> 5. AUDITING FEES...")
        # A. Fee structures with same name, academic_year, class_id, frequency
        dup_fee_structs = session.execute(text("""
            SELECT LOWER(TRIM(name)) as norm_name, academic_year, COALESCE(class_id, 0) as cid, frequency, COUNT(*), array_agg(id) as ids
            FROM fee_structures
            GROUP BY LOWER(TRIM(name)), academic_year, COALESCE(class_id, 0), frequency
            HAVING COUNT(*) > 1;
        """)).fetchall()
        print(f"  - Duplicate Fee Structures: {len(dup_fee_structs)}")
        for r in dup_fee_structs:
            print(f"    * Name: '{r.norm_name}', Year: {r.academic_year}, Class: {r.cid}, Freq: {r.frequency} (IDs: {r.ids})")

        # B. Student fee duplicate assignments (same student, same fee structure)
        dup_stu_fees = session.execute(text("""
            SELECT student_id, fee_structure_id, COUNT(*), array_agg(id) as ids, array_agg(invoice_number) as invoices
            FROM student_fees
            WHERE fee_structure_id IS NOT NULL
            GROUP BY student_id, fee_structure_id
            HAVING COUNT(*) > 1;
        """)).fetchall()
        print(f"  - Duplicate Student Fee Assignments (same student + fee structure): {len(dup_stu_fees)}")
        for r in dup_stu_fees:
            print(f"    * Student ID: {r.student_id}, Structure ID: {r.fee_structure_id} (Fee IDs: {r.ids}, Invoices: {r.invoices})")

        # C. Duplicate Invoice Numbers
        dup_invoices = session.execute(text("""
            SELECT LOWER(TRIM(invoice_number)) as norm_inv, COUNT(*), array_agg(id) as ids
            FROM student_fees
            GROUP BY LOWER(TRIM(invoice_number))
            HAVING COUNT(*) > 1;
        """)).fetchall()
        print(f"  - Duplicate Fee Invoices: {len(dup_invoices)}")
        for r in dup_invoices:
            print(f"    * Invoice: {r.norm_inv} (IDs: {r.ids})")

        # D. Duplicate Payment Receipts
        dup_receipts = session.execute(text("""
            SELECT LOWER(TRIM(receipt_number)) as norm_rcpt, COUNT(*), array_agg(id) as ids
            FROM fee_payments
            GROUP BY LOWER(TRIM(receipt_number))
            HAVING COUNT(*) > 1;
        """)).fetchall()
        print(f"  - Duplicate Payment Receipts: {len(dup_receipts)}")
        for r in dup_receipts:
            print(f"    * Receipt: {r.norm_rcpt} (IDs: {r.ids})")

        print("\n" + "=" * 80)
        print("AUDIT COMPLETE")
        print("=" * 80)

    finally:
        session.close()

if __name__ == "__main__":
    run_audit()

