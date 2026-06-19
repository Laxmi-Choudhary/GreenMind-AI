import asyncio


def _async(fn):
    async def wrapper(*a, **k):
        return fn(*a, **k)
    return wrapper


async def _noop(*a, **k):
    return None


async def _create_user(data):
    return data


def test_register(monkeypatch, client):
    # Simulate no existing user and successful creation
    from app import database

    async def fake_get_user_by_email(email):
        return None

    async def fake_create_user(user_data):
        user_data["id"] = "new-user-1"
        return user_data

    monkeypatch.setattr(database.db_manager, "get_user_by_email", fake_get_user_by_email)
    monkeypatch.setattr(database.db_manager, "create_user", fake_create_user)

    payload = {"username": "tester", "email": "test@example.com", "password": "password123"}
    r = client.post("/api/auth/register", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert "access_token" in body
    assert body["user"]["email"] == "test@example.com"


def test_login(monkeypatch, client, sample_user):
    from app import database
    async def fake_get_user_by_email(email):
        return sample_user

    monkeypatch.setattr(database.db_manager, "get_user_by_email", fake_get_user_by_email)

    payload = {"email": sample_user["email"], "password": "password123"}
    r = client.post("/api/auth/login", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert "access_token" in body
