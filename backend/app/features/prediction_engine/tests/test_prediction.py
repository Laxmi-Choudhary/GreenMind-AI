import asyncio
from app.features.prediction_engine.routes import router
from app.features.prediction_engine.services import PredictionService

def test_router_exists():
    assert router.prefix == "/api/prediction"

def test_prediction_service():
    svc = PredictionService()
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(svc.predict({"monthly_kwh": 200}))
    assert "predicted_annual_co2_kg" in result
    assert result["predicted_annual_co2_kg"] > 0
