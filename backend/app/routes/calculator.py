from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import List, Dict
from datetime import datetime, date
import logging

from app.database import db_manager
from app.middleware.auth_middleware import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/calculator",
    tags=["Carbon Calculator"]
)


# ======================================================
# Models
# ======================================================

class FootprintLogInput(BaseModel):
    date: date

    # Transportation
    car_km: float = Field(default=0.0, ge=0)
    bus_km: float = Field(default=0.0, ge=0)
    train_km: float = Field(default=0.0, ge=0)
    metro_km: float = Field(default=0.0, ge=0)

    # Energy
    electricity_kwh: float = Field(default=0.0, ge=0)
    ac_hours: float = Field(default=0.0, ge=0)

    # Lifestyle
    diet: str = Field(
        default="vegetarian",
        pattern="^(vegetarian|non-vegetarian|vegan)$"
    )

    online_purchases: int = Field(default=0, ge=0)

    waste_level: str = Field(
        default="medium",
        pattern="^(low|medium|high)$"
    )


# ======================================================
# Helper Function
# ======================================================

def calculate_emissions(data: FootprintLogInput) -> Dict:

    travel = (
        data.car_km * 0.20 +
        data.bus_km * 0.08 +
        data.train_km * 0.04 +
        data.metro_km * 0.03
    )

    energy = (
        data.electricity_kwh * 0.5 +
        data.ac_hours * 0.8
    )

    food_map = {
        "vegan": 2.9,
        "vegetarian": 3.8,
        "non-vegetarian": 7.2
    }

    food = food_map.get(data.diet, 3.8)

    shopping = data.online_purchases * 2.5

    waste_map = {
        "low": 1.0,
        "medium": 2.5,
        "high": 5.0
    }

    waste = waste_map.get(data.waste_level, 2.5)

    total = travel + energy + food + shopping + waste

    return {
        "travel": round(travel, 2),
        "energy": round(energy, 2),
        "food": round(food, 2),
        "shopping": round(shopping, 2),
        "waste": round(waste, 2),
        "total": round(total, 2)
    }


# ======================================================
# Log Carbon Footprint
# ======================================================

@router.post(
    "/log",
    status_code=status.HTTP_201_CREATED
)
async def log_footprint(
    log_input: FootprintLogInput,
    current_user: dict = Depends(get_current_user)
):
    try:

        emissions = calculate_emissions(log_input)

        # Convert date object to string
        inputs_data = log_input.model_dump()
        inputs_data["date"] = str(log_input.date)

        log_data = {
            "user_id": current_user["id"],
            "date": str(log_input.date),
            "inputs": inputs_data,

            "breakdown": {
                "travel": emissions["travel"],
                "energy": emissions["energy"],
                "food": emissions["food"],
                "shopping": emissions["shopping"],
                "waste": emissions["waste"]
            },

            "daily_emissions": emissions["total"],
            "monthly_emissions": round(
                emissions["total"] * 30, 2
            ),
            "annual_emissions": round(
                emissions["total"] * 365, 2
            ),

            "created_at": datetime.utcnow().isoformat()
        }

        # Save in MongoDB
        saved_log = await db_manager.add_footprint(log_data)

        # Convert ObjectId to string
        if saved_log and "_id" in saved_log:
            saved_log["_id"] = str(saved_log["_id"])

        # ==================================================
        # Points & Badges
        # ==================================================

        points_earned = 10
        messages = ["Footprint logged successfully! +10 Points"]

        if emissions["total"] < 15:
            points_earned += 20
            messages.append("Green Day Bonus! +20 Points")

        all_logs = await db_manager.get_footprints_by_user(
            current_user["id"]
        )

        existing_badges = set(
            current_user.get("badges", [])
        )

        new_badges = []

        if "First Step" not in existing_badges:
            new_badges.append("First Step")

        if (
            emissions["total"] < 10 and
            "Eco Warrior" not in existing_badges
        ):
            new_badges.append("Eco Warrior")

        if (
            len(all_logs) >= 5 and
            "Consistent Saver" not in existing_badges
        ):
            new_badges.append("Consistent Saver")

        if (
            log_input.ac_hours == 0 and
            log_input.electricity_kwh < 5 and
            "Energy Saver" not in existing_badges
        ):
            new_badges.append("Energy Saver")

        if (
            log_input.car_km == 0 and
            (
                log_input.bus_km > 0 or
                log_input.train_km > 0 or
                log_input.metro_km > 0
            ) and
            "Cruisin' Green" not in existing_badges
        ):
            new_badges.append("Cruisin' Green")

        updated_points = (
            current_user.get("points", 0)
            + points_earned
        )

        updated_level = 1 + (updated_points // 100)

        updated_badges = list(
            existing_badges.union(new_badges)
        )

        await db_manager.update_user(
            current_user["id"],
            {
                "points": updated_points,
                "level": updated_level,
                "badges": updated_badges
            }
        )

        return {
            "success": True,
            "log": saved_log,

            "summary": {
                "daily_emissions": emissions["total"],
                "monthly_emissions": round(
                    emissions["total"] * 30, 2
                ),
                "annual_emissions": round(
                    emissions["total"] * 365, 2
                )
            },

            "points_earned": points_earned,
            "level_up": updated_level > current_user.get("level", 1),
            "new_level": updated_level,
            "new_badges": new_badges,
            "messages": messages
        }

    except Exception as e:
        logger.exception("Footprint logging failed")

        raise HTTPException(
            status_code=500,
            detail=f"Failed to save footprint: {str(e)}"
        )


# ======================================================
# Get User History
# ======================================================

@router.get("/history", response_model=List[dict])
async def get_history(
    current_user: dict = Depends(get_current_user)
):
    try:

        logs = await db_manager.get_footprints_by_user(
            current_user["id"]
        )

        for log in logs:
            if "_id" in log:
                log["_id"] = str(log["_id"])

        return logs

    except Exception as e:
        logger.exception("History fetch failed")

        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch history: {str(e)}"
        )