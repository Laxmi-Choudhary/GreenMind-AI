from app.features.marketplace.routes import router

def test_router():
    assert router.prefix == "/api/marketplace"
