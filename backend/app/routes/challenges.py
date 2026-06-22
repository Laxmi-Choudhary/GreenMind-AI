from _pytest import python_api
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List
import copy
import logging

from app.database import db_manager
from app.middleware.auth_middleware import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/challenges",
    tags=["Challenges"]
)

# =====================================================
# Challenge Templates
# =====================================================

CHALLENGE_TEMPLATES = [
    {
        "id": "no_plastic",
        "title": "No Plastic Week",
        "description": (
            "Avoid using single-use plastic bottles, "
            "bags, or packaging for 7 days."
        ),
        "category": "waste",
        "points": 150,
        "target": 7,
        "progress": 0,
        "status": "active"
    },
    {
        "id": "walk_to_work",
        "title": "Walk To Work",
        "description": (
            "Walk, cycle, or skateboard for commute "
            "trips at least 3 days."
        ),
        "category": "travel",
        "points": 100,
        "target": 3,
        "progress": 0,
        "status": "active"
    },
    {
        "id": "save_electricity",
        "title": "Save Electricity",
        "description": (
            "Keep daily electricity usage under "
            "6 kWh for 5 days."
        ),
        "category": "energy",
        "points": 120,
        "target": 5,
        "progress": 0,
        "status": "active"
    },
    {
        "id": "sustainable_shopping",
        "title": "Sustainable Shopping",
        "description": (
            "Avoid ordering online for 2 weeks "
            "to reduce freight shipping."
        ),
        "category": "shopping",
        "points": 100,
        "target": 2,
        "progress": 0,
        "status": "active"
    },
    {
        "id": "vegan_marathon",
        "title": "Vegan for 3 Days",
        "description": (
            "Opt for completely vegan meals "
            "for 3 consecutive days."
        ),
        "category": "food",
        "points": 80,
        "target": 3,
        "progress": 0,
        "status": "active"
    }
]


# =====================================================
# Request Models
# =====================================================

class ProgressInput(BaseModel):
    increment: int = Field(..., gt=0)


# =====================================================
# Get All Challenges
# =====================================================

@router.get("/", status_code=status.HTTP_200_OK)
async def get_challenges(
    current_user: dict = Depends(get_current_user)
):
    """
    Get all challenges for current user.
    """

    try:

        user_id = current_user["id"]

        user_challenges = (
            await db_manager.get_challenges_by_user(
                user_id
            )
        )

        # First time user
        if not user_challenges:

            user_challenges = copy.deepcopy(
                CHALLENGE_TEMPLATES
            )

            await db_manager.save_challenges_by_user(
                user_id,
                user_challenges
            )

        return {
            "success": True,
            "count": len(user_challenges),
            "challenges": user_challenges
        }

    except Exception as e:

        logger.exception(
            f"Error fetching challenges: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to fetch challenges"
        )


# =====================================================
# Get Single Challenge
# =====================================================

@router.get("/{challenge_id}")
async def get_challenge(
    challenge_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get single challenge details.
    """

    user_id = current_user["id"]

    challenges = (
        await db_manager.get_challenges_by_user(
            user_id
        )
    )

    if not challenges:
        challenges = copy.deepcopy(
            CHALLENGE_TEMPLATES
        )

        await db_manager.save_challenges_by_user(
            user_id,
            challenges
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


# =====================================================
# Update Challenge Progress
# =====================================================

@router.post("/{challenge_id}/progress")
async def update_challenge_progress(
    challenge_id: str,
    payload: ProgressInput,
    current_user: dict = Depends(get_current_user)
):
    """
    Update challenge progress.
    """

    try:

        user_id = current_user["id"]

        user_challenges = (
            await db_manager.get_challenges_by_user(
                user_id
            )
        )

        if not user_challenges:
            user_challenges = copy.deepcopy(
                CHALLENGE_TEMPLATES
            )

        challenge = next(
            (
                ch for ch in user_challenges
                if ch["id"] == challenge_id
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
            challenge["progress"]
            + payload.increment
        )

        points_earned = 0
        level_up = False
        messages = []

        # ==========================================
        # Challenge Completed
        # ==========================================

        if challenge["progress"] >= challenge["target"]:

            challenge["status"] = "completed"

            points_earned = challenge["points"]

            messages.append(
                f"Completed '{challenge['title']}' "
                f"+{points_earned} points earned."
            )

            badge_map = {
                "travel": "Eco Commuter",
                "energy": "Watts Saver",
                "food": "Green Gourmet",
                "shopping": "Minimalist Pack",
                "waste": "Zero Waster"
            }

            badge = badge_map.get(
                challenge["category"],
                "Champion"
            )

            badges = set(
                current_user.get("badges", [])
            )

            if badge not in badges:

                badges.add(badge)

                messages.append(
                    f"Unlocked badge: {badge}"
                )

            updated_points = (
                current_user.get("points", 0)
                + points_earned
            )

            updated_level = (
                1 + updated_points // 100
            )

            level_up = (
                updated_level >
                current_user.get("level", 1)
            )

            if level_up:

                messages.append(
                    f"Congratulations! "
                    f"Level {updated_level} reached."
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

        # Save updated challenges

        await db_manager.save_challenges_by_user(
            user_id,
            user_challenges
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
            f"Error updating challenge: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to update challenge"
        )


# =====================================================
# Reset Challenges (Optional)
# =====================================================

@router.post("/reset")
async def reset_challenges(
    current_user: dict = Depends(get_current_user)
):
    """
    Reset all challenges.
    """

    try:

        user_id = current_user["id"]

        challenges = copy.deepcopy(
            CHALLENGE_TEMPLATES
        )

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
            f"Error resetting challenges: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to reset challenges"
        )