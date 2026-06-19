from fastapi import APIRouter
router = APIRouter(prefix="/api/planner", tags=["planner"])

@router.post("/plan")
async def create_plan():
    return {"plan": "stub"}
