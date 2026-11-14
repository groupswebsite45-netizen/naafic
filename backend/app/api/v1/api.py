from fastapi import APIRouter
from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.admin import router as admin_router
from app.api.v1.routes.profile import router as profile_router
from app.api.v1.routes.system import router as system_router
from app.api.v1.routes.super_admin import router as super_admin_router
from app.api.v1.routes.super_admin_inquiries import router as super_admin_inquiries_router
from app.api.v1.routes.public import router as public_router
from app.api.v1.routes.classes import router as classes_router
from app.api.v1.routes.class_promotions import router as class_promotions_router
from app.api.v1.routes.subjects import router as subjects_router
from app.api.v1.routes.teachers import router as teachers_router
from app.api.v1.routes.students import router as students_router
from app.api.v1.routes.timetables import router as timetable_router
from app.api.v1.routes.fees import router as fees_router
from app.api.v1.routes.exams import router as exams_router
from app.api.v1.routes.results import router as results_router
from app.api.v1.routes.notifications import router as notifications_router
from app.api.v1.routes.teacher_portal import router as teacher_portal_router, teacher_alias_router
from app.api.v1.routes.teacher_attendance import router as teacher_attendance_router
from app.api.v1.routes.admin_attendance import router as admin_attendance_router
from app.api.v1.routes.admin_teacher_attendance import router as admin_teacher_attendance_router
from app.api.v1.routes.student_portal import router as student_portal_router
from app.api.v1.routes.form_master_admin import router as form_master_admin_router
from app.api.v1.routes.form_master_portal import router as form_master_portal_router

api_v1_router = APIRouter(prefix="/api/v1")

# Core & Auth
api_v1_router.include_router(public_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(admin_router)
api_v1_router.include_router(super_admin_router)
api_v1_router.include_router(super_admin_inquiries_router)
api_v1_router.include_router(profile_router)
api_v1_router.include_router(system_router)

# School Management Modules (Admin)
api_v1_router.include_router(classes_router)
api_v1_router.include_router(class_promotions_router)
api_v1_router.include_router(subjects_router)
api_v1_router.include_router(teachers_router)
api_v1_router.include_router(students_router)
api_v1_router.include_router(students_router, prefix="/admin")
api_v1_router.include_router(timetable_router)
api_v1_router.include_router(fees_router)
api_v1_router.include_router(fees_router, prefix="/admin")
api_v1_router.include_router(exams_router)
api_v1_router.include_router(results_router)
api_v1_router.include_router(notifications_router)
api_v1_router.include_router(form_master_admin_router)
api_v1_router.include_router(form_master_admin_router, prefix="/admin")
api_v1_router.include_router(admin_attendance_router)
api_v1_router.include_router(admin_teacher_attendance_router)

# Dedicated Portals & Aliases
api_v1_router.include_router(teacher_portal_router)
api_v1_router.include_router(teacher_alias_router)
api_v1_router.include_router(teacher_attendance_router)
api_v1_router.include_router(form_master_portal_router)
api_v1_router.include_router(form_master_portal_router, prefix="/teacher-portal")
api_v1_router.include_router(student_portal_router)


