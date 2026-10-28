# Hawlwadaag Primary & Secondary School - Examination System Integrity Audit Report

**Audit Date:** 2026-09-20  
**Scope:** PostgreSQL Database (`hawlwadaag_school_db`), Exam Models, Result Submissions, Result Releases, Classes, Teacher Assignments, and Academic Years.

---

## 1. Executive Summary

An authoritative audit of the exam and result management system in PostgreSQL revealed architectural flaws and data anomalies resulting from historical test executions and missing unique constraints:
1. **Unconstrained Exam Creation:** The existing database constraint `uq_exam_academic_year_class_subj_type_name` included the `name` column, enabling multiple duplicate active exams for the same `(academic_year, class_id, subject_id, exam_type)`.
2. **Arbitrary Test Exams & Names:** Generated/test exam records (e.g. `Somali Lit Return Exam 38a90b`, `Fadumo Somali Exam c0ea9c`, `Full Lifecycle Exam 814449`, `Admin Redesign Mid-Term 2026`) exist in the active database.
3. **Academic Year Inconsistencies:** Multiple string representations (`2026/2027`, `2026-2027`, `2025/2026`, `2025-2026`) were used interchangeably.
4. **Inactive & Test Classes:** Several non-standard test classes (`Grade 7-Test`, `Grade 7-12Subj`, `Grade 9-Test-CF`, `Grade 7 - 63C91C`, `Grade 7 - 32DA`) were created during previous testing.
5. **Class vs Subject Assignment Calculation:** The Admin Results Management was querying all subjects instead of strictly scoping to active `TeacherAssignment` records for the selected class and academic year.

---

## 2. Academic Years Audit

| Academic Year Format | Source Tables | Canonical Status | Action |
| :--- | :--- | :--- | :--- |
| `2026/2027` | `classes`, `exams`, `teacher_assignments`, `student_enrollments`, `result_submissions`, `result_release_batches` | **CANONICAL** | Keep as official format. |
| `2026-2027` | `classes` (test classes 195-198), `exams`, `result_submissions`, `result_release_batches` | **NON-CANONICAL** | Normalize to `2026/2027`. |
| `2025/2026` | `classes` (inactive historical), `teacher_assignments`, `exams` | **HISTORICAL CANONICAL** | Keep for historical records. |
| `2025-2026` | `classes` (test/inactive), `system_settings` | **NON-CANONICAL** | Normalize to `2025/2026`. |

---

## 3. Classes Audit

### Active Standard Classes (Production Roster)
| Class ID | Class Name | Code | Level | Division | Section | Academic Year | Enrolled Students | Active Assignments | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **147** | `Grade 7 - A` | `G7-A-2026` | `Grade 7` | `PRIMARY` | `A` | `2026/2027` | 8 | 5 core subjects | **ACTIVE** |
| **32** | `Grade 8 - A` | `G8-A-2026` | `Grade 8` | `PRIMARY` | `A` | `2026/2027` | 6 | 3 core subjects | **ACTIVE** |
| **157** | `Form 1 - A` | `F1-A-2026` | `Form 1` | `SECONDARY` | `A` | `2026/2027` | 6 | 5 core subjects | **ACTIVE** |
| **56** | `Form 2 - A` | `F2-A-2026` | `Form 2` | `SECONDARY` | `A` | `2026/2027` | 5 | 4 core subjects | **ACTIVE** |

### Test / Inactive / Non-standard Classes
- **Test Class IDs:** `195` (`Grade 7-Test`), `196` (`Grade 8-Test`), `197` (`Grade 7-12Subj`), `198` (`Grade 9-Test-CF`), `193` (`Grade 7 - FCF8`), `194` (`Grade 7 - 63C91C`), `212` (`Grade 7 - 32DA`), `213` (`Grade 7 - 68B6FE`), `201`-`206` (Promotion test classes).
- **Status:** Marked `INACTIVE` or flagged for exclusion from production dropdowns. Active school selectors must strictly query `status = 'ACTIVE'` and filter by Division (`PRIMARY` vs `SECONDARY`).

---

## 4. Subjects & Teacher Assignments Audit

### Core Valid Primary / Secondary Subjects:
1. `ID 21`: **Mathematics** (`MATH-101`) - Active (Primary & Secondary)
2. `ID 22`: **Somali Language & Literature** (`SOM-101`) - Active (Primary & Secondary)
3. `ID 23`: **English Language** (`ENG-101`) - Active (Primary & Secondary)
4. `ID 24`: **Arabic & Islamic Studies** (`ISL-101`) - Active (Primary & Secondary)
5. `ID 25`: **Integrated Science** (`SCI-101`) - Active (Primary)
6. `ID 26`: **Physics** (`PHY-101`) - Active (Secondary)
7. `ID 27`: **Chemistry** (`CHE-101`) - Active (Secondary)
8. `ID 28`: **Biology** (`BIO-101`) - Active (Secondary)
9. `ID 29`: **Social Studies & Geography** (`SOC-101`) - Active (Primary & Secondary)
10. `ID 30`: **ICT & Computer Studies** (`ICT-101`) - Active (Primary & Secondary)

### Active Assignment Cleanliness for Standard Grade 7 - A (Class ID 147):
- **Mathematics (21):** Teacher Ahmed Hassan Ali (ID 18)
- **Somali Language & Literature (22):** Teacher Fadumo Mohamed Warsame (ID 19)
- **English Language (23):** Teacher Fadumo Mohamed Warsame (ID 19)
- **Arabic & Islamic Studies (24):** Teacher Sheikh Omar Abdirahman (ID 20)
- **Integrated Science (25):** Teacher Khadija Osman Guled (ID 21)

---

## 5. Examinations Audit (Categorization of All Records)

| Category | Description | Count | Action |
| :--- | :--- | :--- | :--- |
| **A. Legitimate School Exams** | Official Mid-Term/Final exams for standard classes | ~6 | Retain & align with canonical workflow |
| **B. Test / Generated Exams** | Generated with random hash suffixes (e.g. `38a90b`, `c0ea9c`, `814449`) | ~28 | Safe removal / archiving |
| **C. Duplicate Exams** | Multiple exams for same class + subject + exam_type | ~15 | Deduplicate, keeping single authoritative record |
| **D. Orphan Exams** | Exams pointing to deleted or inactive test classes | ~4 | Purge |
| **E. Invalid Exam Types** | Any non-standard type | 0 | Ensure schema strictly enforces `MID_TERM`, `FINAL`, `MONTHLY`, `QUIZ` |

---

## 6. Result Submissions & Release Batches Audit

- **Submissions Count:** 50 entries. Multiple entries exist per subject on Class 147 from automated lifecycle tests.
- **Release Batches Count:** 8 batches generated across test runs.
- **Workflow State Alignment:** All retained result submissions will be mapped cleanly to `DRAFT`, `SUBMITTED`, `RETURNED`, `APPROVED`, or `RELEASED`.

---

## 7. Action Plan for Remediation

1. **Database Uniqueness & Schema:**
   - Enforce database constraint `uq_exam_academic_year_class_subj_type` on `(academic_year, class_id, subject_id, exam_type)`.
   - Normalize academic years to canonical `2026/2027`.
   - Clean up development/test duplicates safely without touching active student enrollments or real faculty assignments.
2. **Backend Services & API:**
   - Enforce Teacher-Only exam creation: resolve teacher from authenticated user session.
   - Restrict subject options strictly to teacher's active assignments.
   - Cascading class options strictly to classes assigned for that selected subject.
   - Enforce valid exam types: `MID_TERM`, `FINAL`, `MONTHLY`, `QUIZ`.
   - Implement teacher `recall` endpoint (`POST /teacher-portal/exams/{exam_id}/recall` or `/results/teacher/exams/{exam_id}/recall`).
   - Admin Results API: class-centric subject calculation derived strictly from `TeacherAssignment`.
   - Class release: single atomic action for all enrolled students in the class, with SMS/Notification trigger.
3. **Frontend UI Rebuild:**
   - Teacher Exams: strict dropdown cascading (Subject -> Class), exam type selector restricted to 4 types.
   - Admin Results: Class-centric matrix with Primary/Secondary level filters, real subject status table, Return for Correction modal, and single "RELEASE ALL CLASS RESULTS" button.
   - Remove all admin "Create Exam" buttons/actions.
4. **Automated Verification:**
   - End-to-end integration test suite `backend/tests/test_exam_class_result_workflow.py` validating complete lifecycle and negative security tests against real PostgreSQL.
