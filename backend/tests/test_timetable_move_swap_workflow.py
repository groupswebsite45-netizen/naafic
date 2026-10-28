import sys
import os
import pytest
from datetime import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.timetable import Timetable
from app.models.school_class import SchoolClass
from app.models.teacher import Teacher
from app.models.subject import Subject
from app.models.teacher_assignment import TeacherAssignment
from app.models.user import User

client = TestClient(app)

def test_move_and_swap_timetable_workflow():
    # 1. Login as Admin
    login_res = client.post("/api/v1/auth/login", json={
        "identifier": "admin",
        "password": "Admin@Hawlwadaag2026"
    })
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    db = SessionLocal()
    try:
        # 2. Pick or seed an isolated test class with at least 2 assigned subjects & teachers
        test_class = db.query(SchoolClass).filter(SchoolClass.status == "ACTIVE").first()
        assert test_class is not None, "Active class required"
        class_id = test_class.id
        year = test_class.academic_year or "2026/2027"

        # Find or create 2 distinct subjects
        subjects = db.query(Subject).limit(2).all()
        teachers = db.query(Teacher).limit(2).all()
        assert len(subjects) >= 2 and len(teachers) >= 2, "Need at least 2 subjects and 2 teachers"

        # Ensure teacher assignments exist for this class
        for s, t in zip(subjects, teachers):
            ta = db.query(TeacherAssignment).filter(
                TeacherAssignment.class_id == class_id,
                TeacherAssignment.subject_id == s.id
            ).first()
            if not ta:
                ta = TeacherAssignment(
                    class_id=class_id,
                    subject_id=s.id,
                    teacher_id=t.id,
                    academic_year=year,
                    status="ACTIVE"
                )
                db.add(ta)
        db.commit()

        # Clean any old test slots for this class in this test run
        db.query(Timetable).filter(Timetable.class_id == class_id).delete()
        db.commit()

        # Create Slot 1: Saturday 08:00 - 08:45
        slot1 = Timetable(
            class_id=class_id,
            subject_id=subjects[0].id,
            teacher_id=teachers[0].id,
            academic_year=year,
            day_of_week="Saturday",
            period_number=1,
            start_time=time(8, 0),
            end_time=time(8, 45),
            room="Room 101",
            status="DRAFT"
        )
        # Create Slot 2: Sunday 08:45 - 09:30
        slot2 = Timetable(
            class_id=class_id,
            subject_id=subjects[1].id,
            teacher_id=teachers[1].id,
            academic_year=year,
            day_of_week="Sunday",
            period_number=2,
            start_time=time(8, 45),
            end_time=time(9, 30),
            room="Room 102",
            status="DRAFT"
        )
        db.add(slot1)
        db.add(slot2)
        db.commit()
        db.refresh(slot1)
        db.refresh(slot2)

        s1_id = slot1.id
        s2_id = slot2.id

        # 3. Test Move Slot 1 to an available empty slot (Monday 08:00 - 08:45)
        move_res = client.post(
            "/api/v1/timetable/move-slot",
            headers=headers,
            json={
                "slot_id": s1_id,
                "target_day": "Monday",
                "target_period_number": 1,
                "target_start_time": "08:00:00",
                "target_end_time": "08:45:00",
                "target_room": "Room 101"
            }
        )
        assert move_res.status_code == 200, f"Move slot failed: {move_res.text}"
        moved_data = move_res.json()
        assert moved_data["day_of_week"] == "Monday"
        assert moved_data["start_time"] == "08:00:00"

        # Verify DB persisted
        db.expire_all()
        slot1_reloaded = db.query(Timetable).filter(Timetable.id == s1_id).first()
        assert slot1_reloaded.day_of_week == "Monday"

        # 4. Test Move to an OCCUPIED slot (Slot 2's position on Sunday 08:45-09:30)
        # Must be rejected because slot is occupied!
        occupied_res = client.post(
            "/api/v1/timetable/move-slot",
            headers=headers,
            json={
                "slot_id": s1_id,
                "target_day": "Sunday",
                "target_period_number": 2,
                "target_start_time": "08:45:00",
                "target_end_time": "09:30:00",
                "target_room": "Room 101"
            }
        )
        assert occupied_res.status_code == 409, f"Moving to occupied slot should be rejected: {occupied_res.text}"
        assert "occupied" in occupied_res.text.lower()

        # 5. Test SWAP Slots: Swap Slot 1 (Monday 8:00-8:45) and Slot 2 (Sunday 8:45-9:30)
        swap_res = client.post(
            "/api/v1/timetable/swap-slots",
            headers=headers,
            json={
                "slot_id_1": s1_id,
                "slot_id_2": s2_id
            }
        )
        assert swap_res.status_code == 200, f"Swap failed: {swap_res.text}"
        swap_data = swap_res.json()
        assert len(swap_data) == 2

        # Verify DB persistence of swapped coordinates
        db.expire_all()
        slot1_after = db.query(Timetable).filter(Timetable.id == s1_id).first()
        slot2_after = db.query(Timetable).filter(Timetable.id == s2_id).first()

        # Slot 1 should now be Sunday 08:45
        assert slot1_after.day_of_week == "Sunday"
        assert slot1_after.start_time == time(8, 45)
        # Slot 2 should now be Monday 08:00
        assert slot2_after.day_of_week == "Monday"
        assert slot2_after.start_time == time(8, 0)

        # 6. Test Teacher Collision Rejection:
        # Assign another class slot to Teacher 1 on Tuesday 10:00 - 10:45
        other_class = db.query(SchoolClass).filter(SchoolClass.id != class_id).first()
        if other_class:
            collision_slot = Timetable(
                class_id=other_class.id,
                subject_id=subjects[0].id,
                teacher_id=teachers[0].id,
                academic_year=year,
                day_of_week="Tuesday",
                period_number=3,
                start_time=time(10, 0),
                end_time=time(10, 45),
                room="Room 205",
                status="ACTIVE"
            )
            db.add(collision_slot)
            db.commit()

            # Now try to move Slot 1 (which belongs to Teacher 1) to Tuesday 10:00 - 10:45
            collision_move_res = client.post(
                "/api/v1/timetable/move-slot",
                headers=headers,
                json={
                    "slot_id": s1_id,
                    "target_day": "Tuesday",
                    "target_period_number": 3,
                    "target_start_time": "10:00:00",
                    "target_end_time": "10:45:00"
                }
            )
            assert collision_move_res.status_code == 409, f"Teacher overlap should be rejected: {collision_move_res.text}"
            assert "already teaching" in collision_move_res.text.lower() or "conflict" in collision_move_res.text.lower()

            # Clean up collision slot
            db.delete(collision_slot)
            db.commit()

        # 7. Test Student Portal Timetable endpoint
        student_user = db.query(User).filter(User.username.like("std_%")).first()
        if student_user:
            # Check service directly
            from app.services.student_portal_service import StudentPortalService
            st_svc = StudentPortalService(db)
            st_res = st_svc.get_my_timetable(student_user)
            assert isinstance(st_res, list)

        # 8. Test Teacher Portal Timetable endpoint
        teacher_user = db.query(User).filter(User.username.like("teacher%")).first()
        if teacher_user:
            from app.services.teacher_portal_service import TeacherPortalService
            t_svc = TeacherPortalService(db)
            t_res = t_svc.get_my_timetable(teacher_user)
            assert isinstance(t_res, list)

        print("[SUCCESS] All Move, Swap, and Portal sync tests passed!")
    finally:
        # Clean up test slots
        db.query(Timetable).filter(Timetable.class_id == class_id).delete()
        db.commit()
        db.close()
