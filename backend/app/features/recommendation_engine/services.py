class RecommendationService:
    async def suggest(self, user_id: str, context: dict = None):
        """Return simple recommendations based on user profile or context.
        Replace with personalization + RAG + model scoring in production.
        """
        # Very simple rule-based suggestions
        suggestions = [
            {"title": "Reduce thermostat by 1°C", "estimated_savings_kgco2": 15},
            {"title": "Replace incandescent bulbs with LED", "estimated_savings_kgco2": 5},
            {"title": "Use public transport twice a week", "estimated_savings_kgco2": 20},
        ]
        # Optionally tailor based on context
        if context and context.get("has_solar"):
            suggestions.insert(0, {"title": "Shift heavy appliance use to daytime", "estimated_savings_kgco2": 10})
        return suggestions
