# Developer Guide - Hawlwadaag School Management System

This guide outlines where every module is implemented across Frontend, Backend, and Database layers so that future developers can immediately locate and extend any feature.

---

## Architecture Map by Module

### 1. Classes Management
- **Frontend UI View**: [ClassesView.vue](file:///d:/desktop/SMS/frontend/src/views/admin/classes/ClassesView.vue)
- **Frontend API Service**: [classService.ts](file:///d:/desktop/SMS/frontend/src/services/classService.ts)
- **Backend API Routes**: [classes.py](file:///d:/desktop/SMS/backend/app/api/v1/routes/classes.py)
- **Backend Service**: [class_service.py](file:///d:/desktop/SMS/backend/app/services/class_service.py)
- **Backend Repository**: [class_repo.py](file:///d:/desktop/SMS/backend/app/repositories/class_repo.py)
- **Database Model**: [school_class.py](file:///d:/desktop/SMS/backend/app/models/school_class.py)
- **Database Migration**: [002_school_management_modules.py](file:///d:/desktop/SMS/backend/alembic/versions/002_school_management_modules.py)

---

### 2. Subjects Management
- **Frontend UI View**: [SubjectsView.vue](file:///d:/desktop/SMS/frontend/src/views/admin/subjects/SubjectsView.vue)
- **Frontend API Service**: [subjectService.ts](file:///d:/desktop/SMS/frontend/src/services/subjectService.ts)
- **Backend API Routes**: [subjects.py](file:///d:/desktop/SMS/backend/app/api/v1/routes/subjects.py)
- **Backend Service**: [subject_service.py](file:///d:/desktop/SMS/backend/app/services/subject_service.py)
- **Backend Repository**: [subject_repo.py](file:///d:/desktop/SMS/backend/app/repositories/subject_repo.py)
- **Database Model**: [subject.py](file:///d:/desktop/SMS/backend/app/models/subject.py)
- **Database Migration**: [002_school_management_modules.py](file:///d:/desktop/SMS/backend/alembic/versions/002_school_management_modules.py)

---

### 3. Teachers Management & Class Assignments
- **Frontend UI View**: [TeachersView.vue](file:///d:/desktop/SMS/frontend/src/views/admin/teachers/TeachersView.vue)
- **Frontend API Service**: [teacherService.ts](file:///d:/desktop/SMS/frontend/src/services/teacherService.ts)
- **Backend API Routes**: [teachers.py](file:///d:/desktop/SMS/backend/app/api/v1/routes/teachers.py)
- **Backend Service**: [teacher_service.py](file:///d:/desktop/SMS/backend/app/services/teacher_service.py)
- **Backend Repository**: [teacher_repo.py](file:///d:/desktop/SMS/backend/app/repositories/teacher_repo.py)
- **Database Models**: [teacher.py](file:///d:/desktop/SMS/backend/app/models/teacher.py), [teacher_assignment.py](file:///d:/desktop/SMS/backend/app/models/teacher_assignment.py)
- **Database Migration**: [002_school_management_modules.py](file:///d:/desktop/SMS/backend/alembic/versions/002_school_management_modules.py)

---

### 4. Students Management & Class Enrollment
- **Frontend UI View**: [StudentsView.vue](file:///d:/desktop/SMS/frontend/src/views/admin/students/StudentsView.vue)
- **Frontend API Service**: [studentService.ts](file:///d:/desktop/SMS/frontend/src/services/studentService.ts)
- **Backend API Routes**: [students.py](file:///d:/desktop/SMS/backend/app/api/v1/routes/students.py)
- **Backend Service**: [student_service.py](file:///d:/desktop/SMS/backend/app/services/student_service.py)
- **Backend Repository**: [student_repo.py](file:///d:/desktop/SMS/backend/app/repositories/student_repo.py)
- **Database Models**: [student.py](file:///d:/desktop/SMS/backend/app/models/student.py), [student_enrollment.py](file:///d:/desktop/SMS/backend/app/models/student_enrollment.py)
- **Database Migration**: [002_school_management_modules.py](file:///d:/desktop/SMS/backend/alembic/versions/002_school_management_modules.py)

---

### 5. Timetable Management & Conflict Prevention
- **Frontend UI View**: [TimetableView.vue](file:///d:/desktop/SMS/frontend/src/views/admin/timetable/TimetableView.vue)
- **Frontend API Service**: [timetableService.ts](file:///d:/desktop/SMS/frontend/src/services/timetableService.ts)
- **Backend API Routes**: [timetables.py](file:///d:/desktop/SMS/backend/app/api/v1/routes/timetables.py)
- **Backend Service**: [timetable_service.py](file:///d:/desktop/SMS/backend/app/services/timetable_service.py)
- **Backend Repository**: [timetable_repo.py](file:///d:/desktop/SMS/backend/app/repositories/timetable_repo.py)
- **Database Model**: [timetable.py](file:///d:/desktop/SMS/backend/app/models/timetable.py)
- **Database Migration**: [002_school_management_modules.py](file:///d:/desktop/SMS/backend/alembic/versions/002_school_management_modules.py)

---

### 6. Fees, Billing & Payment Receipts
- **Frontend UI View**: [FeesView.vue](file:///d:/desktop/SMS/frontend/src/views/admin/fees/FeesView.vue)
- **Frontend API Service**: [feeService.ts](file:///d:/desktop/SMS/frontend/src/services/feeService.ts)
- **Backend API Routes**: [fees.py](file:///d:/desktop/SMS/backend/app/api/v1/routes/fees.py)
- **Backend Service**: [fee_service.py](file:///d:/desktop/SMS/backend/app/services/fee_service.py)
- **Backend Repository**: [fee_repo.py](file:///d:/desktop/SMS/backend/app/repositories/fee_repo.py)
- **Database Model**: [fee.py](file:///d:/desktop/SMS/backend/app/models/fee.py)
- **Database Migration**: [002_school_management_modules.py](file:///d:/desktop/SMS/backend/alembic/versions/002_school_management_modules.py)

---

### 7. Examinations & Results Grading
- **Frontend UI View**: [ExamsView.vue](file:///d:/desktop/SMS/frontend/src/views/admin/exams/ExamsView.vue)
- **Frontend API Service**: [examService.ts](file:///d:/desktop/SMS/frontend/src/services/examService.ts)
- **Backend API Routes**: [exams.py](file:///d:/desktop/SMS/backend/app/api/v1/routes/exams.py)
- **Backend Service**: [exam_service.py](file:///d:/desktop/SMS/backend/app/services/exam_service.py)
- **Backend Repository**: [exam_repo.py](file:///d:/desktop/SMS/backend/app/repositories/exam_repo.py)
- **Database Model**: [exam.py](file:///d:/desktop/SMS/backend/app/models/exam.py)
- **Database Migration**: [002_school_management_modules.py](file:///d:/desktop/SMS/backend/alembic/versions/002_school_management_modules.py)

---

### 8. Teacher Portal
- **Frontend Layout**: [TeacherLayout.vue](file:///d:/desktop/SMS/frontend/src/layouts/TeacherLayout.vue)
- **Frontend Dashboard View**: [TeacherDashboardView.vue](file:///d:/desktop/SMS/frontend/src/views/teacher/TeacherDashboardView.vue)
- **Frontend Classes View**: [TeacherClassesView.vue](file:///d:/desktop/SMS/frontend/src/views/teacher/TeacherClassesView.vue)
- **Frontend Students View**: [TeacherStudentsView.vue](file:///d:/desktop/SMS/frontend/src/views/teacher/TeacherStudentsView.vue)
- **Frontend Timetable View**: [TeacherTimetableView.vue](file:///d:/desktop/SMS/frontend/src/views/teacher/TeacherTimetableView.vue)
- **Frontend Exams View**: [TeacherExamsView.vue](file:///d:/desktop/SMS/frontend/src/views/teacher/TeacherExamsView.vue)
- **Frontend API Service**: [teacherPortalService.ts](file:///d:/desktop/SMS/frontend/src/services/teacherPortalService.ts)
- **Backend API Routes**: [teacher_portal.py](file:///d:/desktop/SMS/backend/app/api/v1/routes/teacher_portal.py)
- **Backend Service**: [teacher_portal_service.py](file:///d:/desktop/SMS/backend/app/services/teacher_portal_service.py)

---

### 9. Student Portal
- **Frontend Layout**: [StudentLayout.vue](file:///d:/desktop/SMS/frontend/src/layouts/StudentLayout.vue)
- **Frontend Dashboard View**: [StudentDashboardView.vue](file:///d:/desktop/SMS/frontend/src/views/student/StudentDashboardView.vue)
- **Frontend Class View**: [StudentClassView.vue](file:///d:/desktop/SMS/frontend/src/views/student/StudentClassView.vue)
- **Frontend Timetable View**: [StudentTimetableView.vue](file:///d:/desktop/SMS/frontend/src/views/student/StudentTimetableView.vue)
- **Frontend Fees View**: [StudentFeesView.vue](file:///d:/desktop/SMS/frontend/src/views/student/StudentFeesView.vue)
- **Frontend Exams View**: [StudentExamsView.vue](file:///d:/desktop/SMS/frontend/src/views/student/StudentExamsView.vue)
- **Frontend API Service**: [studentPortalService.ts](file:///d:/desktop/SMS/frontend/src/services/studentPortalService.ts)
- **Backend API Routes**: [student_portal.py](file:///d:/desktop/SMS/backend/app/api/v1/routes/student_portal.py)
- **Backend Service**: [student_portal_service.py](file:///d:/desktop/SMS/backend/app/services/student_portal_service.py)
