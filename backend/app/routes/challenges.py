from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict, Any
from app.database import db_manager
from app.middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/api/challenges", tags=["challenges"])

# Base template of challenges
CHALLENGES_TEMPLATES = [
    {
        "id": "no_plastic",
        "title": "No Plastic Week",
        "description": "Avoid using single-use plastic bottles, bags, or packaging for 7 days.",
        "category": "waste",
        "points": 150,
        "target": 7,
        "progress": 0,
        "status": "active"  # active, completed
    },
    {
        "id": "walk_to_work",
        "title": "Walk To Work",
        "description": "Walk, cycle, or skateboard for commute trips at least 3 days.",
        "category": "travel",
        "points": 100,
        "target": 3,
        "progress": 0,
        "status": "active"
    },
    {
        "id": "save_electricity",
        "title": "Save Electricity",
        "description": "Keep daily electricity usage under 6 kWh for 5 days.",
        "category": "energy",
        "points": 120,
        "target": 5,
        "progress": 0,
        "status": "active"
    },
    {
        "id": "sustainable_shopping",
        "title": "Sustainable Shopping",
        "description": "Avoid ordering online for 2 weeks to reduce freight shipping.",
        "category": "shopping",
        "points": 100,
        "target": 2,
        "progress": 0,
        "status": "active"
    },
    {
        "id": "vegan_marathon",
        "title": "Vegan for 3 Days",
        "description": "Opt for completely vegan meals for 3 consecutive days.",
        "category": "food",
        "points": 80,
        "target": 3,
        "progress": 0,
        "status": "active"
    }
]

class ProgressInput(BaseModel):
    increment: int

@router.get("")
async def get_challenges(current_user: dict = Depends(get_current_user)):
    user_challenges = await db_manager.get_challenges_by_user(current_user["id"])
    
    # Initialize challenges if they do not exist
    if not user_challenges:
        user_challenges = CHALLENGES_TEMPLATES.copy()
        await db_manager.save_challenges_by_user(current_user["id"], user_challenges)
        
    return user_challenges

@router.post("/{challenge_id}/progress")
async def update_challenge_progress(challenge_id: str, payload: ProgressInput, current_user: dict = Depends(get_current_user)):
    user_challenges = await db_manager.get_challenges_by_user(current_user["id"])
    if not user_challenges:
        user_challenges = CHALLENGES_TEMPLATES.copy()

    found_idx = -1
    for idx, ch in enumerate(user_challenges):
        if ch["id"] == challenge_id:
            found_idx = idx
            break
            
    if found_idx == -1:
        raise HTTPException(status_code=404, detail="Challenge not found")
        
    challenge = user_challenges[found_idx]
    if challenge["status"] == "completed":
        return {"detail": "Challenge already completed", "challenge": challenge}
        
    new_progress = min(challenge["target"], challenge["progress"] + payload.increment)
    challenge["progress"] = new_progress
    
    points_earned = 0
    level_up = False
    messages = []
    
    if new_progress >= challenge["target"]:
        challenge["status"] = "completed"
        points_earned = challenge["points"]
        messages.append(f"Completed '{challenge['title']}'! Earned +{points_earned} Points")
        
        # Add badge based on category if not already unlocked
        category_badges = {
            "travel": "Eco Commuter",
            "energy": "Watts Miner",
            "food": "Green Gourmet",
            "shopping": "Minimalist Pack",
            "waste": "Zero Waster"
        }
        
        badge_name = category_badges.get(challenge["category"], "Champion")
        existing_badges = set(current_user.get("badges", []))
        if badge_name not in existing_badges:
            existing_badges.add(badge_name)
            messages.append(f"Unlocked Badge: {badge_name}!")
            
        # Update user profile
        updated_points = current_user.get("points", 0) + points_earned
        updated_level = 1 + updated_points // 100
        level_up = updated_level > current_user.get("level", 1)
        
        await db_manager.update_user(current_user["id"], {
            "points": updated_points,
            "level": updated_level,
            "badges": list(existing_badges)
        })
    else:
        messages.append(f"Incremented progress for '{challenge['title']}' to {new_progress}/{challenge['target']}")

    user_challenges[found_idx] = challenge
    await db_manager.save_challenges_by_user(current_user["id"], user_challenges)
    
    # Fetch updated user profile
    updated_user = await db_manager.get_user_by_id(current_user["id"])
    
    return {
        "challenge": challenge,
        "points_earned": points_earned,
        "level_up": level_up,
        "user": {
            "points": updated_user["points"],
            "level": updated_user["level"],
            "badges": updated_user["badges"]
        },
        "messages": messages
    }
