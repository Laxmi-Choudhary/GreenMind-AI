from fastapi import APIRouter
router = APIRouter(prefix="/api/streaks", tags=["streaks"])

@router.get("/status")
async def streak_status(user_id: str):
    return {"streak": 0}
