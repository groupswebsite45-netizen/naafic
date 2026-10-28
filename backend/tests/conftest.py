import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client
