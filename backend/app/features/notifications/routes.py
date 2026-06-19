from fastapi import APIRouter
router = APIRouter(prefix="/api/notifications", tags=["notifications"])

@router.post("/send")
async def send_notification(data: dict):
    return {"status": "queued"}
