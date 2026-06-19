from fastapi import APIRouter
router = APIRouter(prefix="/api/certificate", tags=["certificate"])

@router.post("/generate")
async def generate_cert(data: dict):
    return {"certificate_id": "stub"}
