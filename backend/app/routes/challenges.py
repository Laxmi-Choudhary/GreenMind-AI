import copy
import logging
from datetime import datetime
from typing import List, Dict, Any

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)
from pydantic import BaseModel, Field

from app.database import db_manager
from app.middleware.auth_middleware import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/challenges",
    tags=["Challenges"]
)

# ==========================================================
# CHALLENGE TEMPLATES
# ==========================================================

CHALLENGE_TEMPLATES = [
    {
        "id": "no_plastic",
        "title": "No Plastic Week",
        "description":
            "Avoid using single-use plastic items for 7 days.",
        "category": "waste",
        "points": 150,
        "target": 7,
        "progress": 0,
        "status": "active"
    },

    {
        "id": "walk_to_work",
        "title": "Walk To Work",
        "description":
            "Walk or cycle for commuting at least 3 days.",
        "category": "travel",
        "points": 100,
        "target": 3,
        "progress": 0,
        "status": "active"
    },

    {
        "id": "save_electricity",
        "title": "Save Electricity",
        "description":
            "Keep electricity consumption under target for 5 days.",
        "category": "energy",
        "points": 120,
        "target": 5,
        "progress": 0,
        "status": "active"
    },

    {
        "id": "sustainable_shopping",
        "title": "Sustainable Shopping",
        "description":
            "Avoid unnecessary online shopping for 2 weeks.",
        "category": "shopping",
        "points": 100,
        "target": 2,
        "progress": 0,
        "status": "active"
    },

    {
        "id": "vegan_marathon",
        "title": "Vegan for 3 Days",
        "description":
            "Eat fully vegan meals for 3 consecutive days.",
        "category": "food",
        "points": 80,
        "target": 3,
        "progress": 0,
        "status": "active"
    }
]


# ==========================================================
# PYDANTIC MODELS
# ==========================================================

class ProgressInput(BaseModel):
    increment: int = Field(..., gt=0)


class ChallengeResponse(BaseModel):
    id: str
    title: str
    description: str
    category: str
    points: int
    target: int
    progress: int
    status: str
    created_at: str | None = None
    completed_at: str | None = None


# ==========================================================
# HELPERS
# ==========================================================

async def initialize_user_challenges(
    user_id: str
) -> List[Dict[str, Any]]:

    challenges = copy.deepcopy(CHALLENGE_TEMPLATES)

    for challenge in challenges:
        challenge["created_at"] = (
            datetime.utcnow().isoformat()
        )
        challenge["completed_at"] = None

    await db_manager.save_challenges_by_user(
        user_id,
        challenges
    )

    return challenges


async def get_user_challenges(
    user_id: str
) -> List[Dict[str, Any]]:

    challenges = (
        await db_manager.get_challenges_by_user(
            user_id
        )
    )

    if not challenges:
        challenges = await initialize_user_challenges(
            user_id
        )

    return challenges


# ==========================================================
# GET ALL CHALLENGES
# ==========================================================

@router.get("/")
async def get_challenges(
    current_user: dict = Depends(get_current_user)
):

    try:

        user_id = current_user["id"]

        challenges = await get_user_challenges(
            user_id
        )

        total = len(challenges)

        completed = len(
            [
                c for c in challenges
                if c["status"] == "completed"
            ]
        )

        active = total - completed

        return {
            "success": True,
            "count": total,
            "completed": completed,
            "active": active,
            "challenges": challenges
        }

    except Exception as e:

        logger.exception(
            f"Error fetching challenges: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to fetch challenges"
        )


# ==========================================================
# GET SINGLE CHALLENGE
# ==========================================================

@router.get("/{challenge_id}")
async def get_challenge(
    challenge_id: str,
    current_user: dict = Depends(get_current_user)
):

    try:

        user_id = current_user["id"]

        challenges = await get_user_challenges(
            user_id
        )

        challenge = next(
            (
                ch for ch in challenges
                if ch["id"] == challenge_id
            ),
            None
        )

        if not challenge:
            raise HTTPException(
                status_code=404,
                detail="Challenge not found"
            )

        return challenge

    except HTTPException:
        raise

    except Exception as e:

        logger.exception(
            f"Error fetching challenge: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to fetch challenge"
        )


# ==========================================================
# UPDATE PROGRESS
# ==========================================================

@router.post("/{challenge_id}/progress")
async def update_challenge_progress(
    challenge_id: str,
    payload: ProgressInput,
    current_user: dict = Depends(get_current_user)
):

    try:

        user_id = current_user["id"]

        challenges = await get_user_challenges(
            user_id
        )

        challenge = next(
            (
                c for c in challenges
                if c["id"] == challenge_id
            ),
            None
        )

        if challenge is None:

            raise HTTPException(
                status_code=404,
                detail="Challenge not found"
            )

        if challenge["status"] == "completed":

            return {
                "success": True,
                "message":
                    "Challenge already completed",
                "challenge": challenge
            }

        challenge["progress"] = min(
            challenge["target"],
            challenge["progress"] +
            payload.increment
        )

        messages = []
        points_earned = 0
        level_up = False

        # ==================================================
        # COMPLETION LOGIC
        # ==================================================

        if challenge["progress"] >= challenge["target"]:

            challenge["status"] = "completed"
            challenge["completed_at"] = (
                datetime.utcnow().isoformat()
            )

            points_earned = challenge["points"]

            messages.append(
                f"Challenge '{challenge['title']}' completed!"
            )

            badge_map = {
                "travel": "Eco Commuter",
                "energy": "Energy Saver",
                "food": "Green Gourmet",
                "shopping": "Eco Shopper",
                "waste": "Zero Waste Hero"
            }

            earned_badge = badge_map.get(
                challenge["category"],
                "Green Champion"
            )

            badges = set(
                current_user.get("badges", [])
            )

            if earned_badge not in badges:

                badges.add(earned_badge)

                messages.append(
                    f"New badge unlocked: "
                    f"{earned_badge}"
                )

            updated_points = (
                current_user.get("points", 0)
                + points_earned
            )

            updated_level = (
                1 + (updated_points // 100)
            )

            if (
                updated_level >
                current_user.get("level", 1)
            ):
                level_up = True

                messages.append(
                    f"You reached level "
                    f"{updated_level}"
                )

            await db_manager.update_user(
                user_id,
                {
                    "points": updated_points,
                    "level": updated_level,
                    "badges": list(badges)
                }
            )

        else:

            messages.append(
                f"Progress updated: "
                f"{challenge['progress']}/"
                f"{challenge['target']}"
            )

        # Save challenges

        await db_manager.save_challenges_by_user(
            user_id,
            challenges
        )

        updated_user = (
            await db_manager.get_user_by_id(
                user_id
            )
        )

        return {

            "success": True,

            "challenge": challenge,

            "points_earned": points_earned,

            "level_up": level_up,

            "user": {
                "points":
                    updated_user.get("points", 0),

                "level":
                    updated_user.get("level", 1),

                "badges":
                    updated_user.get("badges", [])
            },

            "messages": messages
        }

    except HTTPException:
        raise

    except Exception as e:

        logger.exception(
            f"Challenge update failed: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to update challenge"
        )


# ==========================================================
# RESET CHALLENGES
# ==========================================================

@router.post("/reset")
async def reset_challenges(
    current_user: dict = Depends(get_current_user)
):

    try:

        user_id = current_user["id"]

        challenges = copy.deepcopy(
            CHALLENGE_TEMPLATES
        )

        for challenge in challenges:
            challenge["created_at"] = (
                datetime.utcnow().isoformat()
            )
            challenge["completed_at"] = None

        await db_manager.save_challenges_by_user(
            user_id,
            challenges
        )

        return {
            "success": True,
            "message":
                "Challenges reset successfully",
            "challenges": challenges
        }

    except Exception as e:

        logger.exception(
            f"Challenge reset failed: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to reset challenges"
        )


# ==========================================================
# USER CHALLENGE STATS
# ==========================================================

@router.get("/stats/summary")
async def challenge_stats(
    current_user: dict = Depends(get_current_user)
):

    try:

        user_id = current_user["id"]

        challenges = await get_user_challenges(
            user_id
        )

        total = len(challenges)

        completed = len(
            [
                c for c in challenges
                if c["status"] == "completed"
            ]
        )

        completion_rate = (
            round((completed / total) * 100, 2)
            if total > 0 else 0
        )

        return {
            "success": True,
            "total": total,
            "completed": completed,
            "active": total - completed,
            "completion_rate": completion_rate
        }

    except Exception as e:

        logger.exception(
            f"Stats error: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to fetch stats"
        )

async def save_challenges_by_user(
    self,
    user_id: str,
    challenges: list
# pyrefly: ignore [parse-error]
):
    