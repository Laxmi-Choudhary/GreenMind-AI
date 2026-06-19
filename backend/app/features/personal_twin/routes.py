from fastapi import APIRouter
router = APIRouter(prefix="/api/twin", tags=["twin"])

@router.get("/profile")
async def twin_profile(user_id: str):
    return {"twin": {}}
