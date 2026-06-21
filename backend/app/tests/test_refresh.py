from app.utils.auth_utils import create_token, verify_token


def test_refresh_flow(monkeypatch, client):
    # Create fake user and patch db methods
    from app import database

    from app.utils.auth_utils import hash_password
    async def fake_get_user_by_email(email):
        return {"id": "u1", "email": email, "username": "t", "points": 0, "level":1, "badges": [], "created_at": "2026-01-01T00:00:00Z", "hashed_password": hash_password("password123")}

    async def fake_save_refresh_token(user_id, jti, expires_at):
        # store in-memory
        fake_save_refresh_token.store = (user_id, jti)

    async def fake_is_refresh_token_valid(user_id, jti):
        return getattr(fake_save_refresh_token, 'store', (None, None)) == (user_id, jti)

    async def fake_revoke_refresh_token(user_id, jti):
        fake_save_refresh_token.store = None

    monkeypatch.setattr(database.db_manager, "get_user_by_email", fake_get_user_by_email)
    monkeypatch.setattr(database.db_manager, "save_refresh_token", fake_save_refresh_token)
    monkeypatch.setattr(database.db_manager, "is_refresh_token_valid", fake_is_refresh_token_valid)
    monkeypatch.setattr(database.db_manager, "revoke_refresh_token", fake_revoke_refresh_token)

    # Simulate login to get tokens (refresh stored as cookie)
    payload = {"email": "test@example.com", "password": "password123"}
    r = client.post("/api/auth/login", json=payload)
    assert r.status_code == 200
    body = r.json()
    # Refresh token should be set in cookie by server
    rt = client.cookies.get("refresh_token")
    assert rt is not None

    # Use refresh endpoint (cookie will be sent automatically by TestClient)
    r2 = client.post("/api/auth/token/refresh", json={})
    assert r2.status_code == 200, f"Failed with {r2.status_code}: {r2.json()}"
    assert "access_token" in r2.json()

    # Logout (revoke) - cookie will be used
    r3 = client.post("/api/auth/logout", json={})
    assert r3.status_code == 200

    # After revoke, refresh should fail
    r4 = client.post("/api/auth/token/refresh", json={})
    assert r4.status_code == 401
