from app.features.goal_planner.routes import router

def test_router():
    assert router.prefix == "/api/planner"
