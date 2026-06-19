import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.middleware.auth_middleware import get_current_user

@pytest.fixture(autouse=True)
def override_auth(sample_user):
    app.dependency_overrides[get_current_user] = lambda: sample_user
    yield
    app.dependency_overrides.pop(get_current_user, None)

def test_prediction_endpoint(client: TestClient):
    response = client.post("/api/prediction/predict", json={"monthly_kwh": 150})
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["result"]["predicted_annual_co2_kg"] > 0

def test_receipt_endpoint(client: TestClient):
    response = client.post(
        "/api/receipt/analyze",
        json=[{"name": "Apples", "price": 2.5}, {"name": "Bread", "price": 3.0}],
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 5.5
    assert payload["estimated_co2_kg"] > 0

def test_bill_endpoint(client: TestClient):
    response = client.post("/api/bill/analyze", json={"monthly_kwh": 120})
    assert response.status_code == 200
    result = response.json()["result"]
    assert result["predicted_annual_co2_kg"] > 0

def test_recommendation_endpoint(client: TestClient):
    response = client.post(
        "/api/recommend/suggestions",
        json={"user_id": "test-user-1", "context": {"has_solar": True}},
    )
    assert response.status_code == 200
    suggestions = response.json()["suggestions"]
    assert isinstance(suggestions, list)
    assert any("Replace incandescent bulbs" in item["title"] or "Shift heavy" in item["title"] for item in suggestions)
