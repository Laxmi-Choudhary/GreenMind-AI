import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.utils.auth_utils import create_token, hash_password

@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture
def sample_user():
    return {
        "id": "test-user-1",
        "username": "tester",
        "email": "test@example.com",
        "points": 0,
        "level": 1,
        "badges": [],
        "created_at": "2026-01-01T00:00:00Z",
        "hashed_password": hash_password("password123")
    }

@pytest.fixture
def auth_header(sample_user):
    token = create_token({"sub": sample_user["id"]}, token_type="access")
    return {"Authorization": f"Bearer {token}"}
