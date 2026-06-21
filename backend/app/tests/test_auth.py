from app import database


def test_register(monkeypatch, client):

    async def fake_get_user_by_email(email):
        return None

    async def fake_create_user(user_data):
        user_data["id"] = "new-user-1"
        return user_data

    async def fake_save_refresh_token(user_id, jti, exp):
        return None

    monkeypatch.setattr(
        database.db_manager,
        "get_user_by_email",
        fake_get_user_by_email
    )

    monkeypatch.setattr(
        database.db_manager,
        "create_user",
        fake_create_user
    )

    monkeypatch.setattr(
        database.db_manager,
        "save_refresh_token",
        fake_save_refresh_token
    )

    payload = {
        "username": "tester",
        "email": "test@example.com",
        "password": "Password123"
    }

    response = client.post(
        "/api/auth/register",
        json=payload
    )

    assert response.status_code == 200

    body = response.json()

    assert "access_token" in body
    assert body["user"]["email"] == "test@example.com"
    assert body["user"]["username"] == "tester"


def test_login(monkeypatch, client, sample_user):

    async def fake_get_user_by_email(email):
        return sample_user

    async def fake_save_refresh_token(user_id, jti, exp):
        return None

    monkeypatch.setattr(
        database.db_manager,
        "get_user_by_email",
        fake_get_user_by_email
    )

    monkeypatch.setattr(
        database.db_manager,
        "save_refresh_token",
        fake_save_refresh_token
    )

    payload = {
        "email": sample_user["email"],
        "password": "password123"
    }

    response = client.post(
        "/api/auth/login",
        json=payload
    )

    assert response.status_code == 200

    body = response.json()

    assert "access_token" in body
    assert body["user"]["email"] == sample_user["email"]


def test_login_invalid_password(monkeypatch, client, sample_user):

    async def fake_get_user_by_email(email):
        return sample_user

    monkeypatch.setattr(
        database.db_manager,
        "get_user_by_email",
        fake_get_user_by_email
    )

    payload = {
        "email": sample_user["email"],
        "password": "wrongpassword"
    }

    response = client.post(
        "/api/auth/login",
        json=payload
    )

    assert response.status_code == 400