# Class & Subject Integrity Audit Report
**Generated:** 2026-09-18  
**System:** Hawlwadaag School Management System  
**Database:** PostgreSQL  

---

## Summary

| Category | Count |
|---|---|
| Total classes in DB | 50+ |
| Active classes | ~30 |
| Classes with active students | 10 |
| Empty active classes | 11 |
| Test/temp classes | 3 |
| Total subjects | 60 |
| Valid/recognized subjects | 7 (core) + 11 (school-used active) |
| Test/generated subjects | 42 |
| Total students | 375 |
| Active students | 369 |
| Active students without enrollment | 243 |
| Total enrollments | 201 |
| Active enrollments | 185 |
| Total teacher assignments | 79 (all active) |
| Orphan assignments | 0 |
| Total exams | 41 |
| Total result submissions | 32 |
| Submitted | 14 |
| Approved | 0 |
| Released | 16 |

---

## Classes Detail

### Legitimate Classes (Have Active Students)

| ID | Name | Division | Year | Students | TAs | Exams | Status |
|---|---|---|---|---|---|---|---|
| 147 | Grade 7 - A | PRIMARY | 2026/2027 | 30 | 12 | 12 | ACTIVE |
| 157 | Form 1 - A | SECONDARY | 2026/2027 | 28 | 12 | 0 | ACTIVE |
| 158 | Grade 7 - C | PRIMARY | 2026/2027 | 4 | 0 | 0 | ACTIVE |
| 56 | Form 2 - A | SECONDARY | 2026/2027 | 3 | 0 | 0 | ACTIVE |
| 57 | Form 3 - A | SECONDARY | 2026/2027 | 3 | 0 | 0 | ACTIVE |
| 58 | Form 4 - A | SECONDARY | 2026/2027 | 3 | 0 | 0 | ACTIVE |
| 59 | Form 5 - A | SECONDARY | 2026/2027 | 3 | 0 | 1 | ACTIVE |
| 60 | Form 6 - A | SECONDARY | 2026/2027 | 3 | 0 | 0 | ACTIVE |
| 177 | Grade 7-12Subj | PRIMARY | 2026-2027 | 30 | 12 | 12 | ACTIVE |
| 179 | Grade 7 | PRIMARY | 2026-2027 | 2 | 1 | 1 | ACTIVE |

> **Note:** Form 5-A and Form 6-A are out-of-spec (Secondary = Form 1–4 only).  
> **Note:** Grade 7-12Subj is a development test duplicate of Grade 7-A.  
> **Note:** Grade 7 (no section) is malformed.

### Empty Classes (0 Active Students) — Candidates for INACTIVE

| ID | Name | Year | TAs | Exams | Status |
|---|---|---|---|---|---|
| 180 | Grade 8 | 2025-2026 | 0 | 2 | ACTIVE |
| 26 | Grade 2 - A | 2025/2026 | 0 | 0 | ACTIVE |
| 27 | Grade 3 - A | 2025/2026 | 0 | 0 | ACTIVE |
| 28 | Grade 4 - A | 2025/2026 | 0 | 0 | ACTIVE |
| 30 | Grade 6 - A | 2025/2026 | 0 | 0 | ACTIVE |
| 173 | Grade 7 - DELTA STREAM | 2025/2026 | 1 | 0 | ACTIVE |
| 35 | Form 3 - A | 2025/2026 | 0 | 0 | ACTIVE |
| 36 | Form 4 - A | 2025/2026 | 0 | 0 | ACTIVE |
| 161 | Grade 4 - E | 2026/2027 | 0 | 0 | ACTIVE |
| 146 | Grade 8 - A | 2026/2027 | 0 | 0 | ACTIVE |
| 159 | Form 1 - B | 2026/2027 | 0 | 0 | ACTIVE |

### Test/Temp Classes — Mark INACTIVE

| ID | Name | Code | Students | TAs | Status |
|---|---|---|---|---|---|
| 178 | Grade 9-Test-CF | G9-TCF | 0 | 0 | ACTIVE |
| 175 | Grade 7-Test | G7-TST | 0 | 0 | ACTIVE |
| 176 | Grade 8-Test | G8-TST | 0 | 0 | ACTIVE |

---

## Subjects Detail

### 7 Core Recognized Subjects

| ID | Name | Code | Division | TAs | Exams | Status |
|---|---|---|---|---|---|---|
| 21 | Mathematics | MATH-101 | ALL | 6 | 7 | ACTIVE |
| 23 | English Language | ENG-101 | ALL | 2 | 4 | ACTIVE |
| 22 | Somali Language & Literature | SOM-101 | ALL | 1 | 2 | ACTIVE |
| 58 | Islamic Studies | ISL-12S | ALL | 2 | 2 | ACTIVE |
| 26 | Physics | PHY-201 | SECONDARY | 3 | 2 | ACTIVE |
| 27 | Chemistry | CHEM-201 | SECONDARY | 3 | 2 | ACTIVE |
| 28 | Biology | BIO-201 | SECONDARY | 3 | 2 | ACTIVE |

> **Note:** Islamic Studies code needs normalizing from `ISL-12S` to `ISL-101`.  
> **Note:** Physics code needs normalizing from `PHY-201` to `PHY-101`.  
> **Note:** Chemistry code needs normalizing from `CHEM-201` to `CHE-101`.  
> **Note:** Biology code needs normalizing from `BIO-201` to `BIO-101`.

### Other Active School Subjects (Keep, Clean Codes)

| ID | Name | Code | TAs | Exams | Status |
|---|---|---|---|---|---|
| 59 | Arabic | ARB-12S | 2 | 2 | ACTIVE |
| 24 | Arabic & Islamic Studies | ISL-101 | 2 | 1 | ACTIVE |
| 60 | Computer | CMP-12S | 2 | 2 | ACTIVE |
| 54 | English | ENG-12S | 2 | 2 | ACTIVE |
| 56 | Geography | GEO-12S | 2 | 2 | ACTIVE |
| 57 | History | HIST-12S | 2 | 2 | ACTIVE |
| 30 | ICT & Computer Studies | ICT-101 | 2 | 0 | ACTIVE |
| 1 | math | MAT-101 | 1 | 3 | ACTIVE |
| 61 | Physical Education | PE-12S | 2 | 2 | ACTIVE |
| 29 | Social Studies & Geography | SOC-101 | 0 | 0 | ACTIVE |
| 55 | Somali | SOM-12S | 2 | 2 | ACTIVE |

> **Note:** `math` [1] with code MAT-101 conflicts with Mathematics [21]. All assignments/exams must be migrated to Mathematics [21] then `math` marked INACTIVE.

### Test/Generated Subjects — Mark INACTIVE (42 records)

All `Advanced Astronomy *` (10 records), `General Science SCI-*` (14 records), `G9-*` series (12 records), `Mathematics-Test`, `Physics-Test`, `Advanced Physics Laboratory`, `Somali Literature 527B23`, `Integrated Science` (no assignments to valid classes).

---

## Teacher Assignments

- Total: 79 active
- Assignments to test classes: ~12 (in Grade 7-12Subj)
- Assignments to test subjects: some point to Advanced Astronomy variants (all INACTIVE subjects)
- Orphan assignments: 0

---

## Data Integrity Status

| Check | Status |
|---|---|
| Duplicate admission numbers | ✅ None |
| Duplicate active enrollments per year | ✅ None |
| Duplicate class-subject-year teacher assignments | ✅ None |
| Orphan teacher assignments | ✅ None |
| Empty classes in active selectors | ❌ 11 classes |
| Test classes in active state | ❌ 3 classes |
| Test subjects in active state | ❌ Some (Physics-Test, Mathematics-Test, General Science variants) |
| `math` vs `Mathematics` duplicate | ❌ Conflict |
| Form 5-A, Form 6-A out-of-spec | ❌ 2 classes |
| Grade 7-12Subj development class | ❌ 1 class |
