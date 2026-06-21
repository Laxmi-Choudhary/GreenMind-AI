# backend/tests/test_chat.py

import pytest
from app.middleware.auth_middleware import get_current_user


def override_current_user(sample_user):
    """
    Returns a dependency override function.
    """
    async def _override():
        return sample_user

    return _override


def test_chat_success(monkeypatch, client, sample_user):
    """
    Test successful chat response.
    """

    from app.main import app

    # Override authentication
    app.dependency_overrides[get_current_user] = (
        override_current_user(sample_user)
    )

    # ----------------------------------------------------------------
    # Mock AI service
    # Change this section according to your actual AI service location.
    #
    # Example:
    # from app.routes import chat
    #
    # async def fake_chat_response(*args, **kwargs):
    #     return {
    #         "response":
    #         "Use public transport to reduce emissions."
    #     }
    #
    # monkeypatch.setattr(
    #     chat,
    #     "generate_ai_response",
    #     fake_chat_response
    # )
    # ----------------------------------------------------------------

    payload = {
        "message": "How can I reduce my carbon footprint?",
        "history": []
    }

    response = client.post(
        "/api/chat",
        json=payload
    )

    assert response.status_code in [200, 201]

    body = response.json()

    assert isinstance(body, dict)

    # Optional assertions
    # Uncomment if your API returns these fields

    # assert "response" in body
    # assert len(body["response"]) > 0

    # Cleanup
    app.dependency_overrides.clear()


def test_chat_empty_message(client, sample_user):
    """
    Test validation for empty message.
    """

    from app.main import app

    app.dependency_overrides[get_current_user] = (
        override_current_user(sample_user)
    )

    payload = {
        "message": ""
    }

    response = client.post(
        "/api/chat",
        json=payload
    )

    # FastAPI validation usually returns 422
    assert response.status_code in [400, 422]

    app.dependency_overrides.clear()


def test_chat_without_auth(client):
    """
    Test unauthenticated request.
    """

    payload = {
        "message": "Hello",
        "history": []
    }

    response = client.post(
        "/api/chat",
        json=payload
    )

    assert response.status_code in [200, 201]


def test_chat_invalid_payload(client, sample_user):
    """
    Test malformed request payload.
    """

    from app.main import app

    app.dependency_overrides[get_current_user] = (
        override_current_user(sample_user)
    )

    payload = {}

    response = client.post(
        "/api/chat",
        json=payload
    )

    assert response.status_code == 422

    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    """
    Automatically clear dependency overrides
    after every test.
    """

    yield

    from app.main import app
    app.dependency_overrides.clear()