from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from app.features.bill_analyzer.services import BillAnalyzer
from app.middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/api/bill", tags=["bill"]) 
service = BillAnalyzer()

class BillRequest(BaseModel):
    monthly_kwh: Optional[float] = None
    meter_readings: Optional[list] = None

@router.post("/analyze")
async def analyze_bill(payload: BillRequest, user=Depends(get_current_user)):
    try:
        data = payload.dict()
        if not data.get("monthly_kwh") and not data.get("meter_readings"):
            raise HTTPException(status_code=400, detail="Provide monthly_kwh or meter_readings")
        result = await service.analyze_consumption(data)
        return {"success": True, "result": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
