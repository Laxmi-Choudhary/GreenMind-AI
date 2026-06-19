from app.features.leaderboard.routes import router

def test_router():
    assert router.prefix == "/api/leaderboard"
