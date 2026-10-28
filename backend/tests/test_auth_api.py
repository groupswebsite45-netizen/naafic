from app.core.config import settings


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Hawlwadaag" in data["app"]


def test_public_settings_endpoint(client):
    response = client.get("/api/v1/system/settings/public")
    assert response.status_code == 200
    settings_list = response.json()
    keys = [s["key"] for s in settings_list]
    assert "school_name" in keys


def test_login_invalid_credentials(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"identifier": "nonexistent_user", "password": "WrongPassword123"}
    )
    assert response.status_code == 401
    assert "Invalid" in response.json()["error"]["message"]


def test_login_success_and_protected_routes(client):
    # 1. Login with seeded admin credentials
    login_payload = {
        "identifier": settings.INITIAL_ADMIN_USERNAME,
        "password": settings.INITIAL_ADMIN_PASSWORD
    }
    response = client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert "refresh_token" in token_data
    assert token_data["user"]["username"] == settings.INITIAL_ADMIN_USERNAME

    access_token = token_data["access_token"]
    auth_headers = {"Authorization": f"Bearer {access_token}"}

    # 2. Access /api/v1/auth/me
    me_resp = client.get("/api/v1/auth/me", headers=auth_headers)
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["user"]["email"] == settings.INITIAL_ADMIN_EMAIL
    assert "admin:access" in me_data["permissions"]

    # 3. Access Admin Dashboard
    dash_resp = client.get("/api/v1/admin/dashboard", headers=auth_headers)
    assert dash_resp.status_code == 200
    dash_data = dash_resp.json()
    assert dash_data["system_status"] == "ONLINE"
    assert dash_data["database_status"] == "CONNECTED"
    assert len(dash_data["modules"]) > 0

    # 4. Access Admin Health
    health_resp = client.get("/api/v1/admin/health", headers=auth_headers)
    assert health_resp.status_code == 200
    assert health_resp.json()["database_connected"] is True


def test_unauthenticated_access_denied(client):
    response = client.get("/api/v1/admin/dashboard")
    assert response.status_code == 401
