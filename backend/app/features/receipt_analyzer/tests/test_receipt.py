from app.features.receipt_analyzer.routes import router
from app.features.receipt_analyzer.services import ReceiptAnalyzer

def test_router():
    assert router.prefix == "/api/receipt"

import asyncio

def test_estimate_items():
    svc = ReceiptAnalyzer()
    loop = asyncio.get_event_loop()
    items = [{"name": "Coffee", "price": 3.5}, {"name": "Bread", "price": 2.0}]
    result = loop.run_until_complete(svc.estimate_from_items(items))
    assert result["total"] == 5.5
    assert "estimated_co2_kg" in result
