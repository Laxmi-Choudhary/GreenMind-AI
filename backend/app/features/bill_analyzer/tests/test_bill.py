from app.features.bill_analyzer.routes import router

def test_router():
    assert router.prefix == "/api/bill"
