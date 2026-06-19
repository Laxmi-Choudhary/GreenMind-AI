from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional
from app.database import db_manager
from app.services.ai_service import ai_service
from app.middleware.auth_middleware import get_optional_current_user

router = APIRouter(prefix="/api/chat", tags=["chat"])

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage]
    language: Optional[str] = "en"
    voice: Optional[bool] = False

@router.post("")
async def chat_with_coach(request: ChatRequest, current_user: Optional[dict] = Depends(get_optional_current_user)):
    latest_log = None
    if current_user:
        user_history = await db_manager.get_footprints_by_user(current_user["id"])
        latest_log = user_history[0] if user_history else None

    # Format history as simple dict list for service
    formatted_history = [{"role": msg.role, "content": msg.content} for msg in request.history]
    response = await ai_service.get_chat_response(request.message, formatted_history, latest_log, language=request.language)

    result = {"response": response}
    if request.voice:
        result["voice_instructions"] = "Use a TTS service to speak this text aloud; integrate your voice assistant on the client."
    return result
