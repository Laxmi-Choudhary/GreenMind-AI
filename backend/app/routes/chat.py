from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from app.database import db_manager
from app.services.ai_service import ai_service
from app.middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/api/chat", tags=["chat"])

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage]

@router.post("")
async def chat_with_coach(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    user_history = await db_manager.get_footprints_by_user(current_user["id"])
    latest_log = user_history[0] if user_history else None
    
    # Format history as simple dict list for service
    formatted_history = [{"role": msg.role, "content": msg.content} for msg in request.history]
    
    response = await ai_service.get_chat_response(request.message, formatted_history, latest_log)
    return {"response": response}
