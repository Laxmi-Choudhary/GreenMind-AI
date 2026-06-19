from fastapi import APIRouter
router = APIRouter(prefix="/api/trees", tags=["trees"])

@router.post("/plant")
async def plant_tree(data: dict):
    return {"status": "scheduled"}
