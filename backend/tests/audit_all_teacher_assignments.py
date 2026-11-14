"""
Authoritative Teacher Identity and Assignment Consistency Audit Script.
Tests EVERY teacher account in Hawlwadaag Primary and Secondary School.

Checks:
1. Authenticated User -> Teacher Profile -> Teacher ID resolution.
2. Parity between Admin-visible assignments and Teacher Portal assignments.
3. Class IDs, Subject IDs, and Academic Years matching.
4. IDOR / Authorization enforcement (cannot create exam for unassigned class/subject).
"""
import sys
from app.core.database import SessionLocal
from app.models.user import User
from app.models.teacher import Teacher
from app.models.teacher_assignment import TeacherAssignment
from app.models.user_role import UserRole
from app.models.role import Role
from app.services.teacher_service import TeacherService
from app.services.teacher_portal_service import TeacherPortalService
from app.schemas.exam import ExamCreate
from datetime import date
from fastapi import HTTPException

def audit_all_teachers():
    db = SessionLocal()
    teacher_service = TeacherService(db)
    portal_service = TeacherPortalService(db)

    # 1. Fetch all users with TEACHER role
    roles = {r.name: r.id for r in db.query(Role).all()}
    teacher_role_id = roles.get("TEACHER")
    teacher_user_roles = db.query(UserRole).filter(UserRole.role_id == teacher_role_id).all()
    teacher_user_ids = sorted(list(set(ur.user_id for ur in teacher_user_roles)))

    print(f"=== AUDITING ALL {len(teacher_user_ids)} TEACHER ACCOUNTS ===")
    audit_results = []
    has_mismatch = False

    for uid in teacher_user_ids:
        user = db.query(User).filter(User.id == uid).first()
        if not user:
            continue

        # Step 1: Resolve authenticated user -> teacher
        try:
            teacher = portal_service.get_authenticated_teacher(user)
            identity = portal_service.get_teacher_me(user)
            identity_resolved = True
        except Exception as e:
            teacher = None
            identity = None
            identity_resolved = False

        if not identity_resolved or not teacher:
            print(f"[FAIL] User {user.id} ({user.username}): Failed to resolve teacher profile.")
            has_mismatch = True
            audit_results.append({
                "username": user.username,
                "user_id": user.id,
                "teacher_id": None,
                "teacher_name": None,
                "mapping_status": "BROKEN",
                "admin_count": 0,
                "portal_count": 0,
                "consistent": False,
                "error": "No teacher profile resolved"
            })
            continue

        # Step 2: Fetch Admin-visible assignments
        admin_profile = teacher_service.get_full_profile(teacher.id)
        admin_assignments = admin_profile.assignments
        admin_assign_keys = sorted([
            (a.class_id, a.subject_id, a.academic_year)
            for a in admin_assignments
        ])

        # Step 3: Fetch Teacher Portal assignments
        portal_assignments = portal_service.get_my_classes(user)
        portal_assign_keys = sorted([
            (a.class_id, a.subject_id, a.academic_year)
            for a in portal_assignments
        ])

        # Step 4: Compare
        is_consistent = (admin_assign_keys == portal_assign_keys)
        if not is_consistent:
            has_mismatch = True
            print(f"[MISMATCH] Teacher {teacher.id} ({teacher.full_name}): Admin={len(admin_assign_keys)}, Portal={len(portal_assign_keys)}")
            print(f"   Admin:  {admin_assign_keys}")
            print(f"   Portal: {portal_assign_keys}")
        else:
            print(f"[OK] User {user.id} ({user.username}) <-> Teacher {teacher.id} ({teacher.full_name}): {len(portal_assign_keys)} active assignments in sync.")

        audit_results.append({
            "username": user.username,
            "user_id": user.id,
            "teacher_id": teacher.id,
            "teacher_name": teacher.full_name,
            "mapping_status": "EXACT_MATCH",
            "admin_count": len(admin_assign_keys),
            "portal_count": len(portal_assign_keys),
            "consistent": is_consistent,
            "error": None
        })

    print(f"\n=== IDOR / SECURITY ENFORCEMENT TEST ===")
    # Pick Fadumo (User 104, Teacher 19)
    user_fadumo = db.query(User).filter(User.id == 104).first()
    if user_fadumo:
        # Attempt to create an exam for an unassigned class (e.g. class 9999 or class 22)
        idor_blocked = False
        try:
            fake_exam = ExamCreate(
                name="IDOR Test Exam",
                exam_type="Mid-Term",
                academic_year="2026/2027",
                class_id=9999,
                subject_id=23,
                start_date=date(2026, 3, 1),
                max_marks=100.0,
                pass_marks=50.0
            )
            portal_service.create_exam(user_fadumo, fake_exam)
        except HTTPException as exc:
            if exc.status_code == 403:
                idor_blocked = True
                print(f"[PASSED] Server-side IDOR check blocked unassigned class: {exc.detail}")
            else:
                print(f"[WARN] Unexpected exception: {exc}")
        except Exception as e:
            print(f"[WARN] Non-HTTP exception: {e}")

        if not idor_blocked:
            print("[FAIL] IDOR security check failed! Unassigned exam creation was not blocked with 403.")
            has_mismatch = True

    db.close()
    return audit_results, not has_mismatch

if __name__ == "__main__":
    results, success = audit_all_teachers()
    if not success:
        sys.exit(1)
    sys.exit(0)
