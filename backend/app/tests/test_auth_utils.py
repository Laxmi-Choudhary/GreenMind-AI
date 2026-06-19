from app.utils.auth_utils import hash_password, verify_password, create_token, verify_token

def test_password_hashing_and_verification():
    raw = "SecretPass123!"
    hashed = hash_password(raw)
    assert hashed != raw
    assert verify_password(raw, hashed)
    assert not verify_password("WrongPass", hashed)

def test_jwt_token_roundtrip():
    payload = {"sub": "test-id"}
    token = create_token(payload, token_type="access")
    assert token is not None
    decoded = verify_token(token)
    assert decoded is not None
    assert decoded.get("sub") == "test-id"
    assert decoded.get("type") == "access"
