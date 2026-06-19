from fastapi import APIRouter
router = APIRouter(prefix="/api/sdg", tags=["sdg"])

@router.get("/impact")
async def sdg_impact():
    return {"sdg": []}
