from app.features.tree_tracker.routes import router

def test_router():
    assert router.prefix == "/api/trees"
