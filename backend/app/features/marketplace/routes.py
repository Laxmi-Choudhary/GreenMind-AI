from fastapi import APIRouter
router = APIRouter(prefix="/api/marketplace", tags=["marketplace"])

@router.get("/items")
async def list_items():
    return {"items": []}
