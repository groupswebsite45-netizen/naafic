# Exam Data Cleanup Pre-Execution Audit Report

**Date Generated:** 2026-09-19 03:06:56 UTC

## 1. Summary of Existing Exam Records Found

| Table / Entity | Record Count | Cleanup Action |
| :--- | :--- | :--- |
| `exams` | 41 | Full Safe Removal |
| `exam_results` | 750 | Full Safe Removal |
| `result_submissions` | 32 | Full Safe Removal |
| `result_release_batches` | 16 | Full Safe Removal |
| `student_result_views` | 5 | Full Safe Removal |
| `exam-related notifications` | 754 | Safe Unlink & Removal |

## 2. Protected Core Entities (Must NEVER Be Modified)

| Entity | Preserved Count | Verification Status |
| :--- | :--- | :--- |
| `students` | 375 | PROTECTED |
| `teachers` | 22 | PROTECTED |
| `classes` | 30 | PROTECTED |
| `subjects` | 60 | PROTECTED |
| `teacher_assignments` | 67 | PROTECTED |
| `student_enrollments` | 201 | PROTECTED |
| `attendances` | 23 | PROTECTED |
| `fee_structures` | 102 | PROTECTED |
| `student_fees` | 203 | PROTECTED |
| `fee_payments` | 36 | PROTECTED |
| `timetables` | 10 | PROTECTED |

## 3. Inventory of Old Exam Records

| Exam ID | Name | Type | Academic Year | Class ID | Subject ID | Teacher ID | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 25 | E2E Isolation Exam 2026 | Final | 2026/2027 | 31 | 21 | 18 | PUBLISHED |
| 40 | Mid-Term Examination 2026/2027 | Mid-Term | 2026/2027 | 147 | 21 | 40 | PUBLISHED |
| 41 | Mid-Term Examination 2026/2027 | Mid-Term | 2026/2027 | 147 | 54 | 40 | PUBLISHED |
| 42 | Mid-Term Examination 2026/2027 | Mid-Term | 2026/2027 | 147 | 55 | 40 | PUBLISHED |
| 43 | Mid-Term Examination 2026/2027 | Mid-Term | 2026/2027 | 147 | 26 | 40 | PUBLISHED |
| 44 | Mid-Term Examination 2026/2027 | Mid-Term | 2026/2027 | 147 | 27 | 40 | PUBLISHED |
| 45 | Mid-Term Examination 2026/2027 | Mid-Term | 2026/2027 | 147 | 28 | 40 | PUBLISHED |
| 46 | Mid-Term Examination 2026/2027 | Mid-Term | 2026/2027 | 147 | 56 | 40 | PUBLISHED |
| 47 | Mid-Term Examination 2026/2027 | Mid-Term | 2026/2027 | 147 | 57 | 40 | PUBLISHED |
| 13 | Mid-Term Mathematics Exam | Mid-Term | 2025/2026 | 31 | 21 | 18 | COMPLETED |
| 16 | Unit Testing Examination 2026 | Mid-Term | 2025/2026 | 32 | 21 | 18 | SCHEDULED |
| 14 | Mid-Term English Language Exam | Mid-Term | 2025/2026 | 31 | 23 | 19 | COMPLETED |
| 17 | Unit Testing Examination 2026 | Mid-Term | 2025/2026 | 32 | 23 | 19 | SCHEDULED |
| 15 | Mid-Term Islamic Studies Exam | Mid-Term | 2025/2026 | 31 | 24 | 20 | COMPLETED |
| 1 | monthly | Monthly Test | 2026/2027 | 1 | 21 | 1 | SCHEDULED |
| 18 | Unit Testing Examination 2026 | Mid-Term | 2025/2026 | 1 | 21 | 1 | SCHEDULED |
| 20 | Term 1 Midterm Exam 2026 | MIDTERM | 2026/2027 | 59 | 21 | None (Orphan) | COMPLETED |
| 48 | Mid-Term Examination 2026/2027 | Mid-Term | 2026/2027 | 147 | 58 | 40 | PUBLISHED |
| 49 | Mid-Term Examination 2026/2027 | Mid-Term | 2026/2027 | 147 | 59 | 40 | PUBLISHED |
| 50 | Mid-Term Examination 2026/2027 | Mid-Term | 2026/2027 | 147 | 60 | 40 | PUBLISHED |
| 51 | Mid-Term Examination 2026/2027 | Mid-Term | 2026/2027 | 147 | 61 | 40 | PUBLISHED |
| 78 | Final English Language Examination | Final | 2025/2026 | 32 | 23 | 19 | SCHEDULED |
| 81 | Admin Redesign Mid-Term 2026 | Mid-Term | 2026-2027 | 175 | 52 | None (Orphan) | PUBLISHED |
| 83 | Mid-Term Examination 2026/2027 | Mid-Term | 2026-2027 | 177 | 54 | None (Orphan) | SCHEDULED |
| 84 | Mid-Term Examination 2026/2027 | Mid-Term | 2026-2027 | 177 | 55 | None (Orphan) | SCHEDULED |
| 85 | Mid-Term Examination 2026/2027 | Mid-Term | 2026-2027 | 177 | 26 | None (Orphan) | SCHEDULED |
| 86 | Mid-Term Examination 2026/2027 | Mid-Term | 2026-2027 | 177 | 27 | None (Orphan) | SCHEDULED |
| 87 | Mid-Term Examination 2026/2027 | Mid-Term | 2026-2027 | 177 | 28 | None (Orphan) | SCHEDULED |
| 88 | Mid-Term Examination 2026/2027 | Mid-Term | 2026-2027 | 177 | 56 | None (Orphan) | SCHEDULED |
| 89 | Mid-Term Examination 2026/2027 | Mid-Term | 2026-2027 | 177 | 57 | None (Orphan) | SCHEDULED |
| 90 | Mid-Term Examination 2026/2027 | Mid-Term | 2026-2027 | 177 | 58 | None (Orphan) | SCHEDULED |
| 91 | Mid-Term Examination 2026/2027 | Mid-Term | 2026-2027 | 177 | 59 | None (Orphan) | SCHEDULED |
| 92 | Mid-Term Examination 2026/2027 | Mid-Term | 2026-2027 | 177 | 60 | None (Orphan) | SCHEDULED |
| 93 | Mid-Term Examination 2026/2027 | Mid-Term | 2026-2027 | 177 | 61 | None (Orphan) | SCHEDULED |
| 82 | Mid-Term Examination 2026/2027 | Mid-Term | 2026-2027 | 177 | 21 | None (Orphan) | PUBLISHED |
| 94 | E2E Isolation Exam 2026 | Final | 2026-2027 | 179 | 21 | None (Orphan) | PUBLISHED |
| 95 | Unit Testing Examination 2026 | Mid-Term | 2025-2026 | 180 | 21 | None (Orphan) | SCHEDULED |
| 96 | Unit Testing Examination 2026 | Mid-Term | 2025-2026 | 180 | 23 | None (Orphan) | SCHEDULED |
| 98 | Final Examination 2026 | Final | 2026-2027 | 178 | 64 | 39 | SCHEDULED |
| 101 | Mid-Term Somali Grade 7-A Test 2025 | Mid-Term | 2025/2026 | 31 | 22 | 19 | PUBLISHED |
| 102 | Monthly Somali Language & Literature Examination (Grade 7 - A) | Monthly | 2025/2026 | 31 | 22 | 19 | SCHEDULED |

## 4. Inventory of Result Submissions

| Sub ID | Exam ID | Class ID | Subject ID | Teacher ID | Academic Year | Status | Completed / Expected |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 250 | 87 | 177 | 28 | 40 | 2026-2027 | SUBMITTED | 30/30 |
| 246 | 83 | 177 | 54 | 40 | 2026-2027 | SUBMITTED | 30/30 |
| 247 | 84 | 177 | 55 | 40 | 2026-2027 | SUBMITTED | 30/30 |
| 248 | 85 | 177 | 26 | 40 | 2026-2027 | PARTIAL | 28/30 |
| 16 | 13 | 31 | 21 | 18 | 2025/2026 | SUBMITTED | 4/4 |
| 251 | 88 | 177 | 56 | 40 | 2026-2027 | SUBMITTED | 30/30 |
| 249 | 86 | 177 | 27 | 40 | 2026-2027 | SUBMITTED | 30/30 |
| 257 | 102 | 31 | 22 | 19 | 2025/2026 | SUBMITTED | 4/4 |
| 17 | 16 | 32 | 21 | 18 | 2025/2026 | SUBMITTED | 2/2 |
| 252 | 89 | 177 | 57 | 40 | 2026-2027 | SUBMITTED | 30/30 |
| 116 | 48 | 147 | 58 | 40 | 2026/2027 | RELEASED | 30/30 |
| 253 | 90 | 177 | 58 | 40 | 2026-2027 | SUBMITTED | 30/30 |
| 117 | 49 | 147 | 59 | 40 | 2026/2027 | RELEASED | 30/30 |
| 118 | 50 | 147 | 60 | 40 | 2026/2027 | RELEASED | 30/30 |
| 119 | 51 | 147 | 61 | 40 | 2026/2027 | RELEASED | 30/30 |
| 108 | 40 | 147 | 21 | 40 | 2026/2027 | RELEASED | 30/30 |
| 109 | 41 | 147 | 54 | 40 | 2026/2027 | RELEASED | 30/30 |
| 110 | 42 | 147 | 55 | 40 | 2026/2027 | RELEASED | 30/30 |
| 111 | 43 | 147 | 26 | 40 | 2026/2027 | RELEASED | 30/30 |
| 112 | 44 | 147 | 27 | 40 | 2026/2027 | RELEASED | 30/30 |
| 113 | 45 | 147 | 28 | 40 | 2026/2027 | RELEASED | 30/30 |
| 114 | 46 | 147 | 56 | 40 | 2026/2027 | RELEASED | 30/30 |
| 115 | 47 | 147 | 57 | 40 | 2026/2027 | RELEASED | 30/30 |
| 254 | 91 | 177 | 59 | 40 | 2026-2027 | SUBMITTED | 30/30 |
| 144 | 78 | 32 | 23 | 19 | 2025/2026 | SUBMITTED | 2/2 |
| 54 | 25 | 31 | 21 | 18 | 2026/2027 | RELEASED | 2/2 |
| 255 | 92 | 177 | 60 | 40 | 2026-2027 | SUBMITTED | 30/30 |
| 256 | 93 | 177 | 61 | 40 | 2026-2027 | SUBMITTED | 30/30 |
| 245 | 82 | 177 | 21 | 40 | 2026-2027 | RELEASED | 30/30 |
| 230 | 101 | 31 | 22 | 19 | 2025/2026 | SUBMITTED | 4/4 |
| 231 | 81 | 175 | 52 | 39 | 2026-2027 | RELEASED | 2/2 |
| 244 | 94 | 179 | 21 | 29 | 2026-2027 | RELEASED | 2/2 |

## 5. Inventory of Result Release Batches

| Batch ID | Batch Code | Academic Year | Class ID | Exam Name | Results Count | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 64 | RB-2025/2026-0004 | 2025/2026 | 31 | Mid-Term Somali Grade 7-A Test 2025 | 4 | RELEASED |
| 65 | RB-2026-0008 | 2026-2027 | 175 | Admin Redesign Mid-Term 2026 | 2 | RELEASED |
| 68 | RB-2025/2026-0005 | 2025/2026 | 31 | Mid-Term Somali Grade 7-A Test 2025 | 4 | RELEASED |
| 69 | RB-2026-0011 | 2026-2027 | 175 | Admin Redesign Mid-Term 2026 | 2 | RELEASED |
| 71 | RB-2026-0003 | 2026-2027 | 179 | E2E Isolation Exam 2026 | 2 | RELEASED |
| 72 | RB-2026-0002 | 2026-2027 | 177 | Mid-Term Examination 2026/2027 | 30 | RELEASED |
| 31 | RB-2026-0006 | 2026-2027 | 31 | E2E Isolation Exam 2026 | 2 | RELEASED |
| 45 | RB-2026-0009 | 2026-2027 | 147 | Mid-Term Examination 2026/2027 | 30 | RELEASED |
| 46 | RB-2026-0010 | 2026-2027 | 147 | Mid-Term Examination 2026/2027 | 360 | RELEASED |
| 49 | RB-2025/2026-0001 | 2025/2026 | 31 | Mid-Term Somali Grade 7-A Test 2025 | 4 | RELEASED |
| 50 | RB-2026-0001 | 2026-2027 | 175 | Admin Redesign Mid-Term 2026 | 2 | RELEASED |
| 53 | RB-2026-0004 | 2026-2027 | 175 | Admin Redesign Mid-Term 2026 | 2 | RELEASED |
| 55 | RB-2025/2026-0002 | 2025/2026 | 31 | Mid-Term Somali Grade 7-A Test 2025 | 4 | RELEASED |
| 56 | RB-2026-0005 | 2026-2027 | 175 | Admin Redesign Mid-Term 2026 | 2 | RELEASED |
| 59 | RB-2025/2026-0003 | 2025/2026 | 31 | Mid-Term Somali Grade 7-A Test 2025 | 4 | RELEASED |
| 60 | RB-2026-0007 | 2026-2027 | 175 | Admin Redesign Mid-Term 2026 | 2 | RELEASED |

