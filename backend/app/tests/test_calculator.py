from app.middleware.auth_middleware import get_current_user


def test_log_and_history(monkeypatch, client, sample_user):
    from app.main import app
    from app import database

    # Override authentication
    app.dependency_overrides[get_current_user] = lambda: sample_user

    # Mock database methods
    async def fake_add_footprint(data):
        return data

    async def fake_get_footprints_by_user(user_id):
        return [
            {
                "id": "fp-1",
                "user_id": user_id,
                "daily_emissions": 12.34,
                "created_at": "2026-01-01T00:00:00Z"
            }
        ]

    async def fake_update_user(user_id, updates):
        return {**sample_user, **updates}

    monkeypatch.setattr(
        database.db_manager,
        "add_footprint",
        fake_add_footprint
    )

    monkeypatch.setattr(
        database.db_manager,
        "get_footprints_by_user",
        fake_get_footprints_by_user
    )

    monkeypatch.setattr(
        database.db_manager,
        "update_user",
        fake_update_user
    )

    payload = {
        "date": "2026-06-01",
        "car_km": 0,
        "bus_km": 10,
        "train_km": 0,
        "metro_km": 0,
        "electricity_kwh": 4,
        "ac_hours": 0,
        "diet": "vegetarian",
        "online_purchases": 1,
        "waste_level": "medium"
    }

    # Test logging footprint
    response = client.post(
        "/api/calculator/log",
        json=payload
    )

    assert response.status_code == 200

    body = response.json()

    assert "log" in body
    assert "points_earned" in body

    # Test history endpoint
    response = client.get("/api/calculator/history")

    assert response.status_code == 200

    history = response.json()

    assert isinstance(history, list)
    assert len(history) == 1
    assert history[0]["user_id"] == sample_user["id"]

    # Cleanup dependency overrides
    app.dependency_overrides.clear()