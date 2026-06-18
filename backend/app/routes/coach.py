from fastapi import APIRouter, Depends
from app.database import db_manager
from app.services.ai_service import ai_service
from app.middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/api/coach", tags=["coach"])

@router.get("/insights")
async def get_insights(current_user: dict = Depends(get_current_user)):
    history = await db_manager.get_footprints_by_user(current_user["id"])
    latest_log = history[0] if history else None
    
    insights = await ai_service.get_coach_insights(latest_log, history)
    return insights
