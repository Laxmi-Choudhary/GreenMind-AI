from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from pydantic import BaseModel
from app.middleware.auth_middleware import get_current_user
from app.features.prediction_engine.services import PredictionService

router = APIRouter(prefix="/api/prediction", tags=["prediction"])
service = PredictionService()

class PredictionRequest(BaseModel):
    monthly_kwh: Optional[float] = 100.0

@router.post("/predict")
async def predict(payload: PredictionRequest, user=Depends(get_current_user)):
    """Predict carbon emissions for given input payload (simple heuristic stub)."""
    try:
        result = await service.predict(payload.dict())
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
