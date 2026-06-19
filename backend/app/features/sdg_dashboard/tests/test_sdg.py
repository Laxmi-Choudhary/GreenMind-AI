from app.features.sdg_dashboard.routes import router

def test_router():
    assert router.prefix == "/api/sdg"
