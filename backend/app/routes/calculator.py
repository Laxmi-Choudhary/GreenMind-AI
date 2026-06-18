from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from app.database import db_manager
from app.middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/api/calculator", tags=["calculator"])

class FootprintLogInput(BaseModel):
    date: str  # YYYY-MM-DD
    car_km: float = Field(0.0, ge=0.0)
    bus_km: float = Field(0.0, ge=0.0)
    train_km: float = Field(0.0, ge=0.0)
    metro_km: float = Field(0.0, ge=0.0)
    electricity_kwh: float = Field(0.0, ge=0.0)
    ac_hours: float = Field(0.0, ge=0.0)
    diet: str = Field("vegetarian", pattern="^(vegetarian|non-vegetarian|vegan)$")
    online_purchases: int = Field(0, ge=0)
    waste_level: str = Field("medium", pattern="^(low|medium|high)$")

@router.post("/log")
async def log_footprint(log_input: FootprintLogInput, current_user: dict = Depends(get_current_user)):
    # Calculate emissions in kg CO2
    travel_emissions = (
        log_input.car_km * 0.20 +
        log_input.bus_km * 0.08 +
        log_input.train_km * 0.04 +
        log_input.metro_km * 0.03
    )
    energy_emissions = (
        log_input.electricity_kwh * 0.5 +
        log_input.ac_hours * 0.8
    )
    
    if log_input.diet == "vegan":
        food_emissions = 2.9
    elif log_input.diet == "vegetarian":
        food_emissions = 3.8
    else:
        food_emissions = 7.2
        
    shopping_emissions = log_input.online_purchases * 2.5
    
    if log_input.waste_level == "low":
        waste_emissions = 1.0
    elif log_input.waste_level == "medium":
        waste_emissions = 2.5
    else:
        waste_emissions = 5.0
        
    total_daily = travel_emissions + energy_emissions + food_emissions + shopping_emissions + waste_emissions
    
    log_data = {
        "user_id": current_user["id"],
        "date": log_input.date,
        "inputs": log_input.dict(),
        "breakdown": {
            "travel": round(travel_emissions, 2),
            "energy": round(energy_emissions, 2),
            "food": round(food_emissions, 2),
            "shopping": round(shopping_emissions, 2),
            "waste": round(waste_emissions, 2)
        },
        "daily_emissions": round(total_daily, 2),
        "monthly_emissions": round(total_daily * 30, 2),
        "annual_emissions": round(total_daily * 365, 2),
        "created_at": datetime.utcnow().isoformat()
    }
    
    saved_log = await db_manager.add_footprint(log_data)
    
    # Award points & badges
    points_earned = 10
    messages = ["Logged footprint! +10 Points"]
    
    if total_daily < 15.0:
        points_earned += 20
        messages.append("Green Day bonus! +20 Points")
        
    # Get user logs to check badge requirements
    all_logs = await db_manager.get_footprints_by_user(current_user["id"])
    
    new_badges = []
    existing_badges = set(current_user.get("badges", []))
    
    if "First Step" not in existing_badges:
        new_badges.append("First Step")
        messages.append("Unlocked Badge: First Step!")
        
    if total_daily < 10.0 and "Eco Warrior" not in existing_badges:
        new_badges.append("Eco Warrior")
        messages.append("Unlocked Badge: Eco Warrior!")
        
    if len(all_logs) >= 5 and "Consistent Saver" not in existing_badges:
        new_badges.append("Consistent Saver")
        messages.append("Unlocked Badge: Consistent Saver!")
        
    if log_input.ac_hours == 0 and log_input.electricity_kwh < 5 and "Energy Saver" not in existing_badges:
        new_badges.append("Energy Saver")
        messages.append("Unlocked Badge: Energy Saver!")
        
    if log_input.car_km == 0 and (log_input.bus_km > 0 or log_input.train_km > 0 or log_input.metro_km > 0) and "Cruisin' Green" not in existing_badges:
        new_badges.append("Cruisin' Green")
        messages.append("Unlocked Badge: Cruisin' Green!")

    # Update user points and badges
    updated_points = current_user.get("points", 0) + points_earned
    updated_level = 1 + updated_points // 100
    updated_badges = list(existing_badges.union(new_badges))
    
    user_updates = {
        "points": updated_points,
        "level": updated_level,
        "badges": updated_badges
    }
    
    await db_manager.update_user(current_user["id"], user_updates)
    
    return {
        "log": saved_log,
        "points_earned": points_earned,
        "level_up": updated_level > current_user.get("level", 1),
        "new_level": updated_level,
        "new_badges": new_badges,
        "messages": messages
    }

@router.get("/history")
async def get_history(current_user: dict = Depends(get_current_user)):
    logs = await db_manager.get_footprints_by_user(current_user["id"])
    return logs
