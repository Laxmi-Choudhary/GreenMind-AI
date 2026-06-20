# backend/tests/conftest.py

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.utils.auth_utils import create_token, hash_password


@pytest.fixture(scope="session")
def client():
    """
    Shared FastAPI test client for all tests.
    """
    with TestClient(app) as c:
        yield c


@pytest.fixture
def sample_user():
    """
    Sample user object used across tests.
    """
    return {
        "id": "test-user-1",
        "username": "tester",
        "email": "test@example.com",
        "hashed_password": hash_password("password123"),
        "points": 0,
        "level": 1,
        "badges": [],
        "created_at": "2026-01-01T00:00:00Z"
    }


@pytest.fixture
def access_token(sample_user):
    """
    Generate a valid access token.
    """
    return create_token(
        {"sub": sample_user["id"]},
        token_type="access"
    )


@pytest.fixture
def refresh_token(sample_user):
    """
    Generate a valid refresh token.
    """
    return create_token(
        {"sub": sample_user["id"]},
        token_type="refresh"
    )


@pytest.fixture
def auth_header(access_token):
    """
    Authorization header for authenticated requests.
    """
    return {
        "Authorization": f"Bearer {access_token}"
    }