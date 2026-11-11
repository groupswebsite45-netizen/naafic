import io
import os
import pytest
from datetime import date
from PIL import Image
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.core.database import SessionLocal
from app.models.student import Student
from app.models.user import User
from app.core.security import create_access_token, get_password_hash
from app.repositories.role_repo import RoleRepository
from app.repositories.user_repo import UserRepository
from app.services.student_service import UPLOAD_STUDENT_PHOTOS_DIR


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module")
def admin_headers(db_session: Session):
    user_repo = UserRepository(db_session)
    role_repo = RoleRepository(db_session)
    admin_role = role_repo.get_or_create("ADMIN", "Administrator")

    user = user_repo.get_by_username("test_photo_admin")
    if not user:
        user = User(
            username="test_photo_admin",
            email="photo_admin@test.com",
            hashed_password=get_password_hash("AdminPass123!"),
            full_name="Photo Test Admin",
            is_active=True,
            is_superuser=True
        )
        user_repo.create(user)
        user_repo.add_role_to_user(user, admin_role)
        db_session.commit()

    token = create_access_token(subject=str(user.id), claims={"username": user.username})
    return {"Authorization": f"Bearer {token}"}, token, user.id


@pytest.fixture(scope="module")
def student_user_and_headers(db_session: Session):
    user_repo = UserRepository(db_session)
    role_repo = RoleRepository(db_session)
    student_role = role_repo.get_or_create("STUDENT", "Student")

    unique_username = f"std_photo_{os.urandom(3).hex()}"
    user = User(
        username=unique_username,
        email=f"{unique_username}@test.com",
        hashed_password=get_password_hash("StudentPass123!"),
        full_name="Photo Test Student",
        is_active=True,
        is_superuser=False
    )
    user_repo.create(user)
    user_repo.add_role_to_user(user, student_role)
    db_session.commit()

    token = create_access_token(subject=str(user.id), claims={"username": user.username})
    return {"Authorization": f"Bearer {token}"}, token, user.id


def create_test_image(format: str = "JPEG", size=(100, 100), color="blue") -> bytes:
    img = Image.new("RGB", size, color=color)
    buf = io.BytesIO()
    img.save(buf, format=format)
    return buf.getvalue()


def test_student_photo_lifecycle(client, admin_headers, student_user_and_headers, db_session):
    headers, admin_token, admin_id = admin_headers
    student_headers, student_token, student_user_id = student_user_and_headers

    # 1. Create a student without a photo
    adm_no = f"ADM-TEST-PHOTO-{os.urandom(3).hex().upper()}"
    create_payload = {
        "admission_number": adm_no,
        "first_name": "Hamza",
        "last_name": "Warsame",
        "gender": "Male",
        "date_of_birth": "2010-05-15",
        "status": "ACTIVE"
    }
    res = client.post("/api/v1/students", json=create_payload, headers=headers)
    assert res.status_code == 201, res.text
    student_data = res.json()
    student_id = student_data["id"]
    assert student_data["photo_path"] is None
    assert student_data["photo_url"] is None

    # Link student_user_id to this student for self-access testing
    student_record = db_session.query(Student).filter(Student.id == student_id).first()
    student_record.user_id = student_user_id
    db_session.commit()

    # 2. Upload invalid file (text file disguised as image)
    fake_file = io.BytesIO(b"This is not a real image file, it's just raw text")
    res = client.post(
        f"/api/v1/students/{student_id}/photo",
        headers=headers,
        files={"file": ("fake.jpg", fake_file, "image/jpeg")}
    )
    assert res.status_code == 400
    assert "Invalid image format" in res.text or "Verification failed" in res.text

    # 3. Upload a valid JPEG image
    jpeg_bytes = create_test_image("JPEG", color="navy")
    res = client.post(
        f"/api/v1/students/{student_id}/photo",
        headers=headers,
        files={"file": ("profile.jpg", io.BytesIO(jpeg_bytes), "image/jpeg")}
    )
    assert res.status_code == 200, res.text
    updated_data = res.json()
    assert updated_data["photo_path"] is not None
    assert updated_data["photo_filename"] == "profile.jpg"
    assert updated_data["photo_mime_type"] == "image/jpeg"
    assert updated_data["photo_size"] == len(jpeg_bytes)
    assert updated_data["photo_url"] == f"/api/v1/students/{student_id}/photo"

    # Verify physical file exists on disk in permanent location
    relative_path = updated_data["photo_path"]
    filename = os.path.basename(relative_path)
    physical_path = os.path.join(UPLOAD_STUDENT_PHOTOS_DIR, filename)
    assert os.path.exists(physical_path), f"Physical file not found at {physical_path}"

    # 4. Stream photo via GET with Authorization Header (Admin)
    get_res = client.get(f"/api/v1/students/{student_id}/photo", headers=headers)
    assert get_res.status_code == 200
    assert get_res.headers["content-type"] == "image/jpeg"
    assert "private, max-age=3600" in get_res.headers.get("cache-control", "")
    assert len(get_res.content) == len(jpeg_bytes)

    # 5. Stream photo via GET with ?token= query parameter (for standard browser img tags)
    get_res_query = client.get(f"/api/v1/students/{student_id}/photo?token={admin_token}")
    assert get_res_query.status_code == 200
    assert len(get_res_query.content) == len(jpeg_bytes)

    # 6. Stream photo as the student themselves
    get_res_student = client.get(f"/api/v1/students/{student_id}/photo", headers=student_headers)
    assert get_res_student.status_code == 200

    # 7. Unauthenticated request to photo is blocked (401)
    get_res_anon = client.get(f"/api/v1/students/{student_id}/photo")
    assert get_res_anon.status_code == 401

    # 8. Replace existing photo with a PNG image
    png_bytes = create_test_image("PNG", color="green")
    res_replace = client.post(
        f"/api/v1/students/{student_id}/photo",
        headers=headers,
        files={"file": ("updated_photo.png", io.BytesIO(png_bytes), "image/png")}
    )
    assert res_replace.status_code == 200
    replaced_data = res_replace.json()
    assert replaced_data["photo_mime_type"] == "image/png"
    assert replaced_data["photo_filename"] == "updated_photo.png"

    # Confirm old file was cleanly removed and new file exists
    new_filename = os.path.basename(replaced_data["photo_path"])
    assert not os.path.exists(physical_path), "Old JPEG file was not cleaned up on replacement!"
    new_physical_path = os.path.join(UPLOAD_STUDENT_PHOTOS_DIR, new_filename)
    assert os.path.exists(new_physical_path), "New PNG file does not exist!"

    # 9. Verify WEBP format is also supported
    webp_bytes = create_test_image("WEBP", color="purple")
    res_webp = client.post(
        f"/api/v1/students/{student_id}/photo",
        headers=headers,
        files={"file": ("photo.webp", io.BytesIO(webp_bytes), "image/webp")}
    )
    assert res_webp.status_code == 200
    assert res_webp.json()["photo_mime_type"] == "image/webp"

    # 10. Delete student photo
    del_res = client.delete(f"/api/v1/students/{student_id}/photo", headers=headers)
    assert del_res.status_code == 200
    cleared_data = del_res.json()
    assert cleared_data["photo_path"] is None
    assert cleared_data["photo_filename"] is None
    assert cleared_data["photo_mime_type"] is None

    # Verify physical file was unlinked
    webp_filename = os.path.basename(res_webp.json()["photo_path"])
    assert not os.path.exists(os.path.join(UPLOAD_STUDENT_PHOTOS_DIR, webp_filename))

    # Getting photo now returns 404
    get_res_404 = client.get(f"/api/v1/students/{student_id}/photo", headers=headers)
    assert get_res_404.status_code == 404
