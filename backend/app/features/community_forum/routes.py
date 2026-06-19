from fastapi import APIRouter
router = APIRouter(prefix="/api/forum", tags=["forum"])

@router.get("/threads")
async def list_threads():
    return {"threads": []}
