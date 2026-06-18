from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from app.database import db_manager
from app.middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/api/simulator", tags=["simulator"])

class TwinInput(BaseModel):
    # Optional inputs in case the user hasn't logged anything yet
    car_km: Optional[float] = None
    electricity_kwh: Optional[float] = None
    diet: Optional[str] = None
    ac_hours: Optional[float] = None
    online_purchases: Optional[int] = None
    waste_level: Optional[str] = None

class WhatIfInput(BaseModel):
    transit_shift_pct: float = Field(0.0, ge=0.0, le=100.0)  # 0% to 100% of driving shifted
    ac_reduction_hours: float = Field(0.0, ge=0.0)           # daily hours reduced
    meatless_days_per_week: int = Field(0, ge=0, le=7)       # 0 to 7 days
    shopping_reduction_pct: float = Field(0.0, ge=0.0, le=100.0) # 0% to 100%

@router.post("/twin")
async def get_carbon_twin(input_data: Optional[TwinInput] = None, current_user: dict = Depends(get_current_user)):
    # 1. Resolve current inputs
    car_km = 30.0
    electricity_kwh = 10.0
    diet = "non-vegetarian"
    ac_hours = 6.0
    online_purchases = 2
    waste_level = "medium"

    # Try to load from user history
    history = await db_manager.get_footprints_by_user(current_user["id"])
    if history:
        latest = history[0]
        inputs = latest.get("inputs", {})
        car_km = inputs.get("car_km", car_km)
        electricity_kwh = inputs.get("electricity_kwh", electricity_kwh)
        diet = inputs.get("diet", diet)
        ac_hours = inputs.get("ac_hours", ac_hours)
        online_purchases = inputs.get("online_purchases", online_purchases)
        waste_level = inputs.get("waste_level", waste_level)

    # Overwrite with payload if specified
    if input_data:
        if input_data.car_km is not None: car_km = input_data.car_km
        if input_data.electricity_kwh is not None: electricity_kwh = input_data.electricity_kwh
        if input_data.diet is not None: diet = input_data.diet
        if input_data.ac_hours is not None: ac_hours = input_data.ac_hours
        if input_data.online_purchases is not None: online_purchases = input_data.online_purchases
        if input_data.waste_level is not None: waste_level = input_data.waste_level

    # 2. Calculate Current Emissions (Daily)
    curr_travel = car_km * 0.20
    curr_energy = electricity_kwh * 0.5 + ac_hours * 0.8
    curr_food = 7.2 if diet == "non-vegetarian" else (3.8 if diet == "vegetarian" else 2.9)
    curr_shop = online_purchases * 2.5
    curr_waste = 5.0 if waste_level == "high" else (2.5 if waste_level == "medium" else 1.0)
    curr_total_daily = curr_travel + curr_energy + curr_food + curr_shop + curr_waste

    # 3. Calculate Optimized Eco Emissions (Daily)
    # Optimizations:
    # - Drive 50% less (switch to metro or bus with factors 0.03/0.08)
    eco_car_km = car_km * 0.5
    eco_transit_km = car_km * 0.5
    eco_travel = eco_car_km * 0.20 + eco_transit_km * 0.05  # mixed transit average 0.05
    
    # - Reduce AC to max 2 hours, reduce baseline electricity by 20%
    eco_ac_hours = min(2.0, ac_hours)
    eco_electricity = electricity_kwh * 0.8
    eco_energy = eco_electricity * 0.5 + eco_ac_hours * 0.8
    
    # - Upgrade diet: Vegetarian -> Vegan, Non-Vegetarian -> Vegetarian
    if diet == "non-vegetarian":
        eco_diet = "vegetarian"
        eco_food = 3.8
    else:
        eco_diet = "vegan"
        eco_food = 2.9
        
    # - Reduce online shopping by 40%
    eco_shopping_count = max(0, int(online_purchases * 0.6))
    eco_shop = eco_shopping_count * 2.5
    
    # - Reduce waste level to low
    eco_waste_level = "low"
    eco_waste = 1.0
    
    eco_total_daily = eco_travel + eco_energy + eco_food + eco_shop + eco_waste

    # 4. Extrapolate Annualized Figures
    current_annual_co2 = curr_total_daily * 365
    eco_annual_co2 = eco_total_daily * 365
    annual_co2_savings = current_annual_co2 - eco_annual_co2

    # Cost savings calculations
    # - Gas saved: $0.12 per km
    gas_saved = (car_km - eco_car_km) * 0.12 * 365
    # - Electricity saved: $0.15 per kWh
    elec_saved = (electricity_kwh - eco_electricity) * 0.15 * 365
    # - Shopping saved: average $20 per purchase avoided
    shopping_saved = (online_purchases - eco_shopping_count) * 20.0 * 52 # weekly frequency
    # - Diet saving: ~ $3.00/day saved switching away from meat
    food_saved = (3.00 if diet == "non-vegetarian" else 0.0) * 365

    annual_cost_savings = gas_saved + elec_saved + shopping_saved + food_saved

    # Environmental impact equivalence
    # 1 mature tree absorbs ~22 kg CO2 per year
    trees_equivalent = round(annual_co2_savings / 22.0, 1)

    return {
        "current": {
            "daily_emissions": round(curr_total_daily, 2),
            "annual_emissions": round(current_annual_co2, 2),
            "breakdown": {
                "travel": round(curr_travel * 365, 2),
                "energy": round(curr_energy * 365, 2),
                "food": round(curr_food * 365, 2),
                "shopping": round(curr_shop * 365, 2),
                "waste": round(curr_waste * 365, 2)
            }
        },
        "eco": {
            "daily_emissions": round(eco_total_daily, 2),
            "annual_emissions": round(eco_annual_co2, 2),
            "breakdown": {
                "travel": round(eco_travel * 365, 2),
                "energy": round(eco_energy * 365, 2),
                "food": round(eco_food * 365, 2),
                "shopping": round(eco_shop * 365, 2),
                "waste": round(eco_waste * 365, 2)
            }
        },
        "savings": {
            "annual_co2_kg": round(annual_co2_savings, 2),
            "annual_cost_usd": round(annual_cost_savings, 2),
            "trees_equivalent": trees_equivalent
        }
    }

@router.post("/what-if")
async def get_what_if_scenario(scenario: WhatIfInput, current_user: dict = Depends(get_current_user)):
    # Establish a default baseline profile (daily averages)
    base_car_km = 30.0
    base_ac_hours = 6.0
    base_diet = "non-vegetarian"
    base_online_purchases = 2

    history = await db_manager.get_footprints_by_user(current_user["id"])
    if history:
        latest = history[0]
        inputs = latest.get("inputs", {})
        base_car_km = inputs.get("car_km", base_car_km)
        base_ac_hours = inputs.get("ac_hours", base_ac_hours)
        base_diet = inputs.get("diet", base_diet)
        base_online_purchases = inputs.get("online_purchases", base_online_purchases)

    # 1. Calculate travel savings (shift to transit)
    # Gas car emission factor is 0.20, mixed transit is 0.05
    km_shifted = base_car_km * (scenario.transit_shift_pct / 100.0)
    co2_saved_travel = km_shifted * (0.20 - 0.05)

    # 2. Calculate AC savings (reduction of AC hours)
    # AC consumes ~1.6 kW, emission factor is 0.8 kg/hour
    co2_saved_energy = min(base_ac_hours, scenario.ac_reduction_hours) * 0.8

    # 3. Calculate Diet savings (meatless days per week)
    # Switching from non-veg (7.2) to veg (3.8) saves 3.4 kg CO2 per day.
    # If they are already vegetarian, switching to vegan (2.9) saves 0.9 kg.
    daily_diet_diff = 3.4 if base_diet == "non-vegetarian" else 0.9
    co2_saved_food = (daily_diet_diff * scenario.meatless_days_per_week) / 7.0

    # 4. Calculate Shopping savings (online purchase reduction)
    purchases_reduced = base_online_purchases * (scenario.shopping_reduction_pct / 100.0)
    co2_saved_shopping = purchases_reduced * 2.5

    # Total daily saved
    total_saved_daily = co2_saved_travel + co2_saved_energy + co2_saved_food + co2_saved_shopping
    annual_co2_saved = total_saved_daily * 365
    trees = round(annual_co2_saved / 22.0, 1)

    # Calculate Sustainability Improvement Score (out of 100)
    # Scale: saving 3,000 kg CO2 / year gives a score of 100.
    sustainability_score = min(100.0, (annual_co2_saved / 3000.0) * 100.0)

    return {
        "daily_co2_saved_kg": round(total_saved_daily, 2),
        "annual_co2_saved_kg": round(annual_co2_saved, 2),
        "trees_equivalent": trees,
        "sustainability_score": round(sustainability_score, 1)
    }
