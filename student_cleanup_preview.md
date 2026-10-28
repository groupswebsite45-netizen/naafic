# Student Database Cleanup Preview

## Overview
- **Current Total Students in Database:** 408
- **Retained Students:** 20 (10 Primary + 10 Secondary)
- **Students to Delete:** 388
- **Target Academic Year:** 2026/2027

---

## KEEP — PRIMARY

1. **Student Name:** Amina Hassan Ibrahim  
   **Student ID:** 22  
   **Admission #:** ADM-2026-002  
   **Class:** Grade 7 - A  
   **Academic Year:** 2026/2027  

2. **Student Name:** Liban Abdirahman Elmi  
   **Student ID:** 23  
   **Admission #:** ADM-2026-003  
   **Class:** Grade 7 - A  
   **Academic Year:** 2026/2027  

3. **Student Name:** Hafsa Mohamud Adan  
   **Student ID:** 24  
   **Admission #:** ADM-2026-004  
   **Class:** Grade 7 - A  
   **Academic Year:** 2026/2027  

4. **Student Name:** Mushtaaq Ahmed Cali  
   **Student ID:** 1  
   **Admission #:** ADM-413501  
   **Class:** Grade 7 - A  
   **Academic Year:** 2026/2027  

5. **Student Name:** Amina Farah  
   **Student ID:** 244  
   **Admission #:** ADM-527B23  
   **Class:** Grade 7 - A  
   **Academic Year:** 2026/2027  

6. **Student Name:** Zakarie Jama Hussein  
   **Student ID:** 25  
   **Admission #:** ADM-2026-005  
   **Class:** Grade 8 - A  
   **Academic Year:** 2026/2027  

7. **Student Name:** Safia Farah Gedi  
   **Student ID:** 26  
   **Admission #:** ADM-2026-006  
   **Class:** Grade 8 - A  
   **Academic Year:** 2026/2027  

8. **Student Name:** Mustaf Ali Yusuf  
   **Student ID:** 21  
   **Admission #:** ADM-2026-001  
   **Class:** Grade 8 - A  
   **Academic Year:** 2026/2027  

9. **Student Name:** Mustaf Noor  
   **Student ID:** 289  
   **Admission #:** ADM-2026-009  
   **Class:** Grade 8 - A  
   **Academic Year:** 2026/2027  

10. **Student Name:** Amina Ibrahim  
    **Student ID:** 290  
    **Admission #:** ADM-2026-010  
    **Class:** Grade 8 - A  
    **Academic Year:** 2026/2027  

---

## KEEP — SECONDARY

1. **Student Name:** Khaalid Ibrahim Nur  
   **Student ID:** 27  
   **Admission #:** ADM-2026-007  
   **Class:** Form 1 - A  
   **Academic Year:** 2026/2027  

2. **Student Name:** Yasmin Osman Roble  
   **Student ID:** 28  
   **Admission #:** ADM-2026-008  
   **Class:** Form 1 - A  
   **Academic Year:** 2026/2027  

3. **Student Name:** Khadija Ali Warsame  
   **Student ID:** 29  
   **Admission #:** ADM-562018  
   **Class:** Form 1 - A  
   **Academic Year:** 2026/2027  

4. **Student Name:** Hassan Omar Jama  
   **Student ID:** 30  
   **Admission #:** ADM-652157  
   **Class:** Form 1 - A  
   **Academic Year:** 2026/2027  

5. **Student Name:** Dahir Abdi Mohamed  
   **Student ID:** 134  
   **Admission #:** ADM-477791  
   **Class:** Form 1 - A  
   **Academic Year:** 2026/2027  

6. **Student Name:** Fadumo Ali Warsame  
   **Student ID:** 243  
   **Admission #:** ADM-869228  
   **Class:** Form 2 - A  
   **Academic Year:** 2026/2027  

7. **Student Name:** Mohamed Ali Mire  
   **Student ID:** 74  
   **Admission #:** ADM-PROM-5-1-1580  
   **Class:** Form 2 - A  
   **Academic Year:** 2026/2027  

8. **Student Name:** Abdirashid Nur Elmi  
   **Student ID:** 62  
   **Admission #:** ADM-PROM-1-1-1580  
   **Class:** Form 2 - A  
   **Academic Year:** 2026/2027  

9. **Student Name:** Nimo Ahmed Farah  
   **Student ID:** 63  
   **Admission #:** ADM-PROM-1-2-1580  
   **Class:** Form 2 - A  
   **Academic Year:** 2026/2027  

10. **Student Name:** Sahra Jama Hussein  
    **Student ID:** 64  
    **Admission #:** ADM-PROM-1-3-1580  
    **Class:** Form 2 - A  
    **Academic Year:** 2026/2027  

---

## DELETE

- **Count of students that will be removed:** 388
- **Dependent records to be cleaned:**
  - Student enrollments for deleted students
  - Fee payment records for deleted students
  - Student fee invoices for deleted students
  - Exam result records for deleted students
  - Attendance records for deleted students
  - Student result views for deleted students
  - Class promotion records for deleted students
  - Student-specific notifications for deleted students
  - Student portal user accounts for deleted students (Role STUDENT only; Admin and Teachers untouched)
  - Duplicate/invalid classes (Grade 8-Test, Form 1–6 Primary test streams, inactive duplicate classes)

---

## CANONICAL CLASSES DISTRIBUTION AFTER CLEANUP

### PRIMARY (10 Students)
- **Grade 7 - A** (Class ID 147): 5 students
- **Grade 8 - A** (Class ID 32): 5 students

### SECONDARY (10 Students)
- **Form 1 - A** (Class ID 157): 5 students
- **Form 2 - A** (Class ID 56): 5 students

**TOTAL STUDENTS IN DATABASE = EXACTLY 20**
