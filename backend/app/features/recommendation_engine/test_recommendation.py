import asyncio
from app.features.recommendation_engine.services import RecommendationService

def test_suggestions_basic():
    svc = RecommendationService()
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(svc.suggest("user123", {}))
    assert isinstance(result, list)
    assert len(result) >= 1
