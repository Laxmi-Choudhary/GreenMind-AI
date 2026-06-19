from fastapi import APIRouter
router = APIRouter(prefix="/api/leaderboard", tags=["leaderboard"])

@router.get("/")
async def get_leaderboard():
    return {"leaders": []}
