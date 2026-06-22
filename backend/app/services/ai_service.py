import httpx
import logging
import json
from typing import Dict, Any, List, Optional

from app.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are GreenMind AI.

Your primary expertise is sustainability, climate,
carbon footprint reduction, renewable energy,
ESG, and green living.

You can also answer general questions about
technology, science, education, programming,
and business.

Always provide accurate, helpful, and concise answers.
"""


class AIService:

    def __init__(self):
        self.gemini_url = (
            "https://generativelanguage.googleapis.com/"
            "v1beta/models/gemini-1.5-flash:generateContent"
        )

    # =====================================================
    # GEMINI API CALL
    # =====================================================

    async def _call_gemini(self, prompt: str) -> Optional[str]:

        api_key = (
            settings.GEMINI_API_KEY
            or settings.OPENAI_API_KEY
        )

        if not api_key:
            logger.warning(
                "No Gemini API key configured."
            )
            return None

        url = f"{self.gemini_url}?key={api_key}"

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }

        headers = {
            "Content-Type": "application/json"
        }

        try:
            async with httpx.AsyncClient(
                timeout=20.0
            ) as client:

                response = await client.post(
                    url,
                    json=payload,
                    headers=headers
                )

            if response.status_code != 200:
                logger.error(
                    f"Gemini Error {response.status_code}: "
                    f"{response.text}"
                )
                return None

            data = response.json()

            candidates = data.get(
                "candidates", []
            )

            if not candidates:
                return None

            content = candidates[0].get(
                "content", {}
            )

            parts = content.get(
                "parts", []
            )

            if not parts:
                return None

            return parts[0].get(
                "text", ""
            )

        except Exception as e:
            logger.exception(
                f"Gemini request failed: {e}"
            )
            return None

    # =====================================================
    # COACH INSIGHTS
    # =====================================================

    async def get_coach_insights(
        self,
        latest_log: Optional[Dict[str, Any]],
        history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        if not latest_log:
            return self._get_mock_coach_insights(
                None
            )

        prompt = f"""
        Analyze this sustainability data.

        Latest Log:
        {json.dumps(latest_log)}

        History Count:
        {len(history)}

        Return ONLY valid JSON:

        {{
            "insights": [],
            "strategies": [],
            "tips": []
        }}
        """

        response = await self._call_gemini(
            prompt
        )

        if response:
            try:

                cleaned = (
                    response
                    .replace("```json", "")
                    .replace("```", "")
                    .strip()
                )

                return json.loads(cleaned)

            except Exception as e:
                logger.warning(
                    f"JSON Parse Error: {e}"
                )

        return self._get_mock_coach_insights(
            latest_log
        )

    # =====================================================
    # CHATBOT
    # =====================================================

    async def get_chat_response(
        self,
        user_message: str,
        chat_history: List[Dict[str, str]],
        latest_log: Optional[Dict[str, Any]],
        language: str = "en"
    ) -> str:

        context = ""

        if latest_log:
            context = (
                f"Latest footprint: "
                f"{json.dumps(latest_log)}"
            )

        prompt = f"""
        {SYSTEM_PROMPT}

        {context}

        Recent Chat:
        {json.dumps(chat_history[-5:])}

        User:
        {user_message}

        Respond in {language}.
        """

        response = await self._call_gemini(
            prompt
        )

        if response:
            return response.strip()

        return self._get_mock_chat_response(
            user_message,
            latest_log
        )

    # =====================================================
    # WEEKLY REPORT
    # =====================================================

    async def get_weekly_report(
        self,
        history: List[Dict[str, Any]],
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:

        try:

            if not history:
                return {
                    "summary":
                        "No footprint logs available.",

                    "trends":
                        "Insufficient data.",

                    "savings":
                        "0.00 kg CO2",

                    "recommendations": [
                        "Start logging daily emissions.",
                        "Track travel activity.",
                        "Monitor home electricity use."
                    ],

                    "score_change": 0
                }

            history = history[:7]

            prompt = f"""
            Create a sustainability report.

            User:
            {json.dumps(user_profile)}

            Logs:
            {json.dumps(history)}

            Return ONLY JSON:

            {{
                "summary":"...",
                "trends":"...",
                "savings":"...",
                "recommendations":["a","b","c"],
                "score_change":5
            }}
            """

            response = await self._call_gemini(
                prompt
            )

            if response:

                try:

                    cleaned = (
                        response
                        .replace("```json", "")
                        .replace("```", "")
                        .strip()
                    )

                    report = json.loads(
                        cleaned
                    )

                    return {
                        "summary":
                            report.get(
                                "summary",
                                "Weekly report generated."
                            ),

                        "trends":
                            report.get(
                                "trends",
                                "No trends available."
                            ),

                        "savings":
                            report.get(
                                "savings",
                                "0.00 kg CO2"
                            ),

                        "recommendations":
                            report.get(
                                "recommendations",
                                []
                            ),

                        "score_change":
                            int(
                                report.get(
                                    "score_change",
                                    0
                                )
                            )
                    }

                except Exception as e:
                    logger.warning(
                        f"Failed parsing report: {e}"
                    )

            return self._get_mock_weekly_report(
                history,
                user_profile
            )

        except Exception as e:

            logger.exception(
                f"Weekly report error: {e}"
            )

            return {
                "summary":
                    "Unable to generate report.",

                "trends":
                    "Unavailable.",

                "savings":
                    "0.00 kg CO2",

                "recommendations": [
                    "Continue tracking footprints."
                ],

                "score_change": 0
            }

    # =====================================================
    # MOCK COACH
    # =====================================================

    def _get_mock_coach_insights(
        self,
        latest_log
    ):

        return {
            "insights": [
                "Continue tracking your emissions."
            ],

            "strategies": [
                "Use public transport.",
                "Reduce electricity consumption."
            ],

            "tips": [
                "LED bulbs reduce emissions.",
                "Cycling is carbon-free.",
                "Plant-based diets help climate."
            ]
        }

    # =====================================================
    # MOCK CHAT
    # =====================================================

    def _get_mock_chat_response(
        self,
        user_message,
        latest_log
    ):

        msg = user_message.lower()

        if any(
            x in msg
            for x in ["hi", "hello", "hey"]
        ):
            return (
                "Hello! I am GreenMind AI. "
                "How can I help you today?"
            )

        if "reduce" in msg:
            return (
                "You can reduce emissions by "
                "using public transport, "
                "saving electricity and "
                "reducing food waste."
            )

        return (
            "Sustainable choices in travel, "
            "energy usage and food habits "
            "can significantly reduce "
            "your carbon footprint."
        )

    # =====================================================
    # MOCK WEEKLY REPORT
    # =====================================================

    def _get_mock_weekly_report(
        self,
        history,
        user_profile
    ):

        count = len(history)

        avg = round(
            sum(
                x.get(
                    "daily_emissions",
                    0
                )
                for x in history
            ) / count,
            2
        )

        return {

            "summary":
                f"{user_profile.get('username')} "
                f"recorded {count} logs. "
                f"Average emissions: {avg} kg CO2.",

            "trends":
                "Your emissions remained stable.",

            "savings":
                f"{round(max(0,16-avg)*count,2)} kg CO2",

            "recommendations": [

                "Use public transport more often.",

                "Reduce unnecessary electricity usage.",

                "Increase plant-based meals."
            ],

            "score_change": 5
        }


# Global instance
ai_service = AIService()