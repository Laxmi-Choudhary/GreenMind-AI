from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from app.features.recommendation_engine.services import RecommendationService
from app.middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/api/recommend", tags=["recommendation"]) 
service = RecommendationService()

class RecommendRequest(BaseModel):
    user_id: str
    context: Optional[dict] = None

@router.post("/suggestions")
async def suggestions(payload: RecommendRequest, user=Depends(get_current_user)):
    try:
        result = await service.suggest(payload.user_id, payload.context or {})
        return {"success": True, "suggestions": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
