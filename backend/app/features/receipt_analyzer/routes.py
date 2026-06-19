from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from typing import List
from app.features.receipt_analyzer.services import ReceiptAnalyzer
from app.features.receipt_analyzer.schemas import ReceiptItem, ReceiptOutput
from app.middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/api/receipt", tags=["receipt"])
service = ReceiptAnalyzer()

@router.post("/analyze", response_model=ReceiptOutput)
async def analyze_receipt(items: List[ReceiptItem], user=Depends(get_current_user)):
    """Analyze a list of receipt items and estimate CO2."""
    result = await service.estimate_from_items([item.dict() for item in items])
    return result

@router.post("/upload", response_model=ReceiptOutput)
async def upload_receipt(file: UploadFile = File(...), user=Depends(get_current_user)):
    """Upload a receipt image and estimate CO2 from parsed items."""
    try:
        content = await file.read()
        result = await service.parse_image(content)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
