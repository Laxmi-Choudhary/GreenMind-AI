from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from app.database import db_manager
from app.middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/api/score", tags=["score"])

@router.get("")
async def get_eco_score(current_user: dict = Depends(get_current_user)):
    history = await db_manager.get_footprints_by_user(current_user["id"])
    
    # Default inputs if no logs exist
    car_km = 20.0
    electricity_kwh = 8.0
    ac_hours = 4.0
    diet = "vegetarian"
    online_purchases = 1
    waste_level = "medium"

    if history:
        latest = history[0]
        inputs = latest.get("inputs", {})
        car_km = inputs.get("car_km", car_km)
        electricity_kwh = inputs.get("electricity_kwh", electricity_kwh)
        ac_hours = inputs.get("ac_hours", ac_hours)
        diet = inputs.get("diet", diet)
        online_purchases = inputs.get("online_purchases", online_purchases)
        waste_level = inputs.get("waste_level", waste_level)

    # 1. Travel Score: penalized by gasoline car usage
    travel_score = max(10, round(100 - (car_km * 2)))
    
    # 2. Food Score: diet levels
    if diet == "vegan":
        food_score = 100
    elif diet == "vegetarian":
        food_score = 80
    else:
        food_score = 40

    # 3. Energy Score: electricity and AC hours penalties
    energy_score = max(10, round(100 - (electricity_kwh * 4) - (ac_hours * 5)))

    # 4. Shopping Score: online purchases penalty
    shopping_score = max(10, round(100 - (online_purchases * 20)))

    # 5. Waste Score: waste level
    if waste_level == "low":
        waste_score = 100
    elif waste_level == "medium":
        waste_score = 60
    else:
        waste_score = 20

    # Overall Score
    overall_score = round((travel_score + food_score + energy_score + shopping_score + waste_score) / 5)

    # Generate suggestions
    suggestions = []
    if travel_score < 75:
        suggestions.append({
            "category": "Travel",
            "score": travel_score,
            "text": "Your car travel is high. Shifting 30% of trips to metro, train, or a bicycle can improve your score by 15 points."
        })
    if food_score < 75:
        suggestions.append({
            "category": "Food",
            "score": food_score,
            "text": "Beef and poultry diets carry heavy carbon overheads. Incorporating a few meat-free days will lift your diet score significantly."
        })
    if energy_score < 75:
        suggestions.append({
            "category": "Energy",
            "score": energy_score,
            "text": "Reducing daily AC run time by 2 hours and choosing energy-saving LED bulbs will cut your carbon footprint and electricity bills."
        })
    if shopping_score < 75:
        suggestions.append({
            "category": "Shopping",
            "score": shopping_score,
            "text": "Online deliveries utilize freight networks that emit high CO2. Try grouping purchases or buying from local shops."
        })
    if waste_score < 75:
        suggestions.append({
            "category": "Waste",
            "score": waste_score,
            "text": "Landfill waste decays to produce methane. Start separating recyclables and compost food scraps to minimize garbage output."
        })

    # Default suggestions if score is very high
    if not suggestions:
        suggestions.append({
            "category": "General",
            "score": overall_score,
            "text": "Fantastic work! You have a highly sustainable lifestyle. Continue logging footprints daily and challenge friends to join!"
        })

    return {
        "overall": overall_score,
        "categories": {
            "travel": travel_score,
            "food": food_score,
            "energy": energy_score,
            "shopping": shopping_score,
            "waste": waste_score
        },
        "suggestions": suggestions
    }
