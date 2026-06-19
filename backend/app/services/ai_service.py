import httpx
import logging
import json
from typing import Dict, Any, List, Optional
from app.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are GreenMind AI.

Your primary expertise is sustainability, climate, carbon footprint reduction,
renewable energy, ESG, and green living.

However, you can also answer general questions on any topic including
programming, science, mathematics, education, business, and technology.

For sustainability-related questions, provide detailed environmental insights.
For other questions, respond like a professional AI assistant.
"""

class AIService:
    def __init__(self):
        self.gemini_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

    async def _call_gemini(self, prompt: str) -> Optional[str]:
        api_key = settings.GEMINI_API_KEY or settings.OPENAI_API_KEY
        if not api_key:
            logger.info("No AI API key found. Using local rule-based AI engine.")
            return None

        # Try to make direct API call to Gemini
        url = f"{self.gemini_url}?key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    # Extract the text
                    candidates = data.get("candidates", [])
                    if candidates:
                        content = candidates[0].get("content", {})
                        parts = content.get("parts", [])
                        if parts:
                            return parts[0].get("text", "")
                    logger.warning("Unexpected response structure from Gemini API.")
                else:
                    logger.error(f"Gemini API returned error code {response.status_code}: {response.text}")
        except Exception as e:
            logger.error(f"Failed to communicate with Gemini API: {e}")
        
        return None

    # --- AI Coach Service ---
    async def get_coach_insights(self, latest_log: Optional[Dict[str, Any]], history: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not latest_log:
            # Standard onboarding tips
            return self._get_mock_coach_insights(None)

        prompt = f"""
        You are an AI Sustainability Coach. Analyze the user's carbon footprint data.
        Latest Daily Footprint Log Details:
        - Date: {latest_log.get('date')}
        - Total Daily Emissions: {latest_log.get('daily_emissions')} kg CO2
        - Category Breakdown (kg CO2): {json.dumps(latest_log.get('breakdown'))}
        
        Historical Logs Count: {len(history)}
        
        Please provide a JSON response with exactly three keys:
        1. "insights": A bullet-list summary explaining the main emissions drivers (e.g. "Transportation contributes 42%...").
        2. "strategies": Actionable reduction strategies (e.g. "Use public transit twice a week...").
        3. "tips": 3 quick sustainability facts or habits.
        
        Do not include any markdown tags outside the JSON block. Return ONLY valid JSON.
        """
        
        response_text = await self._call_gemini(prompt)
        if response_text:
            try:
                # Strip potential markdown fences if returned
                cleaned = response_text.strip()
                if cleaned.startswith("```json"):
                    cleaned = cleaned[7:]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
                cleaned = cleaned.strip()
                return json.loads(cleaned)
            except Exception as e:
                logger.warning(f"Failed to parse Gemini response as JSON: {e}. Raw response: {response_text}")

        # Fallback to local rule-based engine
        return self._get_mock_coach_insights(latest_log)

    # --- AI Chat Service ---
    async def get_chat_response(self, user_message: str, chat_history: List[Dict[str, str]], latest_log: Optional[Dict[str, Any]], language: str = "en") -> str:
        log_context = ""
        if latest_log:
            log_context = f"\nUser's latest carbon footprint details: Total emissions: {latest_log.get('daily_emissions')} kg CO2. Breakdown: {json.dumps(latest_log.get('breakdown'))}"
 
        language_directive = ""
        if language and language.lower() not in ["en", "english"]:
            language_directive = f"\nPlease answer in {language}."
 
        prompt = SYSTEM_PROMPT + "\n\n"
        prompt += f"""
        You are GreenMind AI, a friendly and knowledgeable sustainability coach.
        {log_context}
         
        Recent chat history:
        {json.dumps(chat_history[-5:])}
         
        User question: \"{user_message}\"
        {language_directive}
         
        Provide a concise, engaging, and scientifically accurate response. Keep it within 3-4 paragraphs. If they ask about reducing their emissions, reference their specific footprint if available.
        """
 
        response_text = await self._call_gemini(prompt)
        if response_text:
            response = response_text.strip()
            return self._translate_text(response, language)
 
        # Fallback to rule-based chatbot
        return self._translate_text(self._get_mock_chat_response(user_message, latest_log), language)
 
    def _translate_text(self, text: str, language: str) -> str:
        if not language or language.lower() in ["en", "english"]:
            return text
 
        # Simple multilingual placeholder support for frontend demo.
        translations = {
            "es": "[ES]",
            "spanish": "[ES]",
            "fr": "[FR]",
            "french": "[FR]",
            "de": "[DE]",
            "german": "[DE]",
            "hi": "[HI]",
            "hindi": "[HI]",
            "pt": "[PT]",
            "portuguese": "[PT]"
        }
        lang_key = language.lower()
        prefix = translations.get(lang_key, f"[{language.upper()}]")
        return f"{prefix} {text}"

    # --- Weekly Report Generator Service ---
    async def get_weekly_report(self, history: List[Dict[str, Any]], user_profile: Dict[str, Any]) -> Dict[str, Any]:
        if not history:
            return {
                "summary": "No logs submitted this week to compute dynamic trends. Start logging to see reports!",
                "trends": "Insufficient data.",
                "savings": "0.00 kg CO2",
                "recommendations": ["Submit at least two footprint logs to unlock automated insights."],
                "score_change": 0
            }

        prompt = f"""
        You are an AI Sustainability Auditor. Generate a Weekly Sustainability Report.
        User Name: {user_profile.get('username')}
        User Level: {user_profile.get('level')}
        Recent Footprint Logs (up to 7 days):
        {json.dumps(history[:7])}
        
        Provide a JSON response with exactly five keys:
        1. "summary": A textual summary of the user's progress.
        2. "trends": A description of emissions trends compared to previous days.
        3. "savings": Estimated CO2 savings achieved compared to global averages (global daily average is ~16 kg CO2 per person).
        4. "recommendations": List of 3 tailored recommendations.
        5. "score_change": Integer score change (e.g., +5 or -2).
        
        Return ONLY valid JSON.
        """
        
        response_text = await self._call_gemini(prompt)
        if response_text:
            try:
                cleaned = response_text.strip()
                if cleaned.startswith("```json"):
                    cleaned = cleaned[7:]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
                cleaned = cleaned.strip()
                return json.loads(cleaned)
            except Exception as e:
                logger.warning(f"Failed to parse report response as JSON: {e}")

        # Fallback report generator
        return self._get_mock_weekly_report(history, user_profile)

    # --- Mock Helpers ---
    def _get_mock_coach_insights(self, latest_log: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        if not latest_log:
            return {
                "insights": [
                    "We need footprint data to construct detailed insights.",
                    "Onboarding: Record your first entry in the 'Carbon Calculator' tab!"
                ],
                "strategies": [
                    "Try walking or biking for trips under 2 km.",
                    "Unplug household devices when not in use to reduce vampire draw."
                ],
                "tips": [
                    "A single mature tree absorbs about 22 kg of CO2 annually.",
                    "LED bulbs consume up to 80% less energy than traditional incandescents."
                ]
            }

        breakdown = latest_log.get("breakdown", {})
        total = latest_log.get("daily_emissions", 1.0)
        if total == 0:
            total = 1.0

        travel_pct = round((breakdown.get("travel", 0) / total) * 100)
        energy_pct = round((breakdown.get("energy", 0) / total) * 100)
        food_pct = round((breakdown.get("food", 0) / total) * 100)
        shopping_pct = round((breakdown.get("shopping", 0) / total) * 100)
        waste_pct = round((breakdown.get("waste", 0) / total) * 100)

        # Build insights based on top category
        categories = [
            ("Travel", travel_pct, "traveling via fossil fuels"),
            ("Energy", energy_pct, "AC and electricity usage"),
            ("Food", food_pct, "diet preferences"),
            ("Shopping", shopping_pct, "online purchases"),
            ("Waste", waste_pct, "household waste disposal")
        ]
        categories.sort(key=lambda x: x[1], reverse=True)
        top_cat, top_pct, top_desc = categories[0]

        insights = [
            f"{top_cat} contributes the largest share ({top_pct}%) of your carbon footprint, driven by {top_desc}.",
            f"Your daily emissions total {total} kg CO2, which is {'below' if total < 16.0 else 'above'} the global average of 16 kg."
        ]

        strategies = []
        if top_cat == "Travel":
            strategies.append("Carpool or use public train/bus instead of driving to work.")
            strategies.append("Switch to cycling or walking for short local trips.")
        elif top_cat == "Energy":
            strategies.append("Increase your AC temperature by 2°C to reduce energy by 15%.")
            strategies.append("Shift to energy-efficient appliances (look for Energy Star label).")
        elif top_cat == "Food":
            strategies.append("Try implementing Meatless Mondays—swapping beef for lentils reduces food impact by 80%.")
            strategies.append("Compost kitchen scraps to avoid landfill methane release.")
        else:
            strategies.append("Reduce impulse online shopping; package shipping creates heavy freight emissions.")
            strategies.append("Practice local recycling and composting to cut waste-related emissions.")

        # Always add a general strategy
        strategies.append("Maintain a consistent log to identify monthly carbon emission trends.")

        tips = [
            "Eating local produce cuts transportation-related emissions by up to 10%.",
            "Setting your thermostat 1-2 degrees cooler in winter or warmer in summer saves tons of CO2.",
            "Recycling aluminum saves 95% of the energy needed to make new aluminum from raw materials."
        ]

        return {
            "insights": insights,
            "strategies": strategies,
            "tips": tips
        }

    def _get_mock_chat_response(self, user_message: str, latest_log: Optional[Dict[str, Any]]) -> str:
        msg = user_message.lower()
        
        # Pull log context
        fp_details = ""
        top_driver = ""
        if latest_log:
            bd = latest_log.get("breakdown", {})
            max_val = -1
            for k, v in bd.items():
                if v > max_val:
                    max_val = v
                    top_driver = k
            fp_details = f" Looking at your profile, your daily footprint is {latest_log.get('daily_emissions')} kg CO2, and your main emissions driver is {top_driver}."

        if any(w in msg for w in ["hello", "hi", "hey", "greetings"]):
            return f"Hello! I am GreenMind AI, your personalized sustainability assistant. How can I help you understand, track, or reduce your carbon footprint today?{fp_details}"
        
        if any(w in msg for w in ["reduce", "cut", "lower", "action", "decrease"]):
            if top_driver == "travel":
                return f"To reduce your emissions,{fp_details} I suggest shifting some of your travel to public transit (buses or trains) or active transit (walking/biking). Choosing public metro instead of driving saves up to 80% CO2 per kilometer!"
            elif top_driver == "energy":
                return f"Based on your high energy footprint,{fp_details} you can make a massive impact by setting your AC temperature to 25°C or higher and unplugging standby appliances. Transitioning to LED lighting is also an easy win."
            elif top_driver == "food":
                return f"To optimize your food footprint,{fp_details} reducing red meat consumption has the absolute largest impact. Transitioning towards vegetarian or vegan lunches even twice a week can cut your dietary emissions by 30%!"
            else:
                return "The three easiest ways to reduce your footprint today are: 1) Shift driving trips to public transport, 2) Set AC thermostat 2 degrees higher, and 3) Introduce plant-based alternatives to your meals."

        if any(w in msg for w in ["travel", "car", "transport", "bus", "train", "metro"]):
            return "Transportation emissions are heavily dependent on vehicle type and occupancy. Driving an average gasoline car produces about 0.20 kg CO2 per km. If you take the metro, that drops to just 0.03 kg CO2 per km. Choosing to walk, bicycle, or use shared transit makes a profound difference."

        if any(w in msg for w in ["energy", "electricity", "ac", "power", "utility"]):
            return "Electricity generation is the leading global source of CO2 emissions. In average grids, every kWh of electricity consumed accounts for ~0.5 kg CO2. Heating and cooling (AC) are the highest energy consumers. Optimizing AC run time and purchasing energy-star certified appliances can reduce household utility bills and carbon outputs."

        if any(w in msg for w in ["food", "diet", "vegan", "vegetarian", "meat"]):
            return "Food accounts for nearly 26% of global greenhouse gas emissions. Meat, especially beef and lamb, requires vast land and water, generating high methane emissions. Swapping one beef meal for a vegetarian dish saves roughly 3 kg of carbon. Plant-based options like lentils, tofu, and oats have tiny ecological impacts."

        if any(w in msg for w in ["shopping", "online", "purchase"]):
            return "Online shopping has a double-sided impact. While it can reduce personal driving, it introduces excessive packaging and rapid freight shipping (like overnight air) which produces heavy carbon emissions. Try combining your purchases, choosing slower shipping speeds, and supporting local circular economies."

        if any(w in msg for w in ["waste", "recycle", "garbage", "trash"]):
            return "Landfills are a major source of methane—a greenhouse gas 28 times more potent than carbon dioxide. Composting organic materials ensures they decompose aerobically, preventing methane formation. Recycling plastics, metal, and glass saves extensive raw material extraction energies."

        # Default fallback response
        return "That's an interesting question! Climate change is a complex topic, but minor actions aggregate to make a big difference. Focus on traveling efficiently, minimizing energy wastage at home, eating lower on the food chain, and reducing waste generation. What specific category are you interested in optimizing?"

    def _get_mock_weekly_report(self, history: List[Dict[str, Any]], user_profile: Dict[str, Any]) -> Dict[str, Any]:
        logs_count = len(history)
        avg_emissions = round(sum(log.get("daily_emissions", 0.0) for log in history) / logs_count, 2)
        
        # Calculate comparison
        global_avg = 16.0
        daily_saving = max(0.0, global_avg - avg_emissions)
        weekly_savings = round(daily_saving * logs_count, 2)

        summary = f"Congratulations {user_profile.get('username')}! You completed a full week of sustainability logging. Your average daily footprint was {avg_emissions} kg CO2."
        trends = f"Your daily emissions fluctuated with a low of {min(log.get('daily_emissions', 999.0) for log in history)} kg and a high of {max(log.get('daily_emissions', 0.0) for log in history)} kg."
        
        savings = f"{weekly_savings} kg CO2"
        
        recommendations = [
            "Your weekend emissions are slightly elevated; try to organize local or low-travel weekend activities.",
            "Consider a fully vegetarian diet at least twice a week to offset travel spikes.",
            "Track AC usage on warmer days; adjusting thermostat by 1°C saves significant carbon."
        ]
        
        return {
            "summary": summary,
            "trends": trends,
            "savings": savings,
            "recommendations": recommendations,
            "score_change": 4
        }

ai_service = AIService()
