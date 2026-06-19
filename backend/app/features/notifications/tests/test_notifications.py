from app.features.notifications.routes import router

def test_router():
    assert router.prefix == "/api/notifications"
