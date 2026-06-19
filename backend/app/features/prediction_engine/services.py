"""Prediction engine services (simple heuristic stub)
"""

class PredictionService:
    def __init__(self):
        pass

    async def predict(self, data):
        """Estimate annual CO2 from monthly kWh using a simple grid factor.
        Replace this with ML model or RAG pipeline for production.
        """
        usage = data.get("monthly_kwh") or 100.0
        try:
            usage = float(usage)
        except Exception:
            usage = 100.0
        factor = 0.233  # kg CO2 per kWh (example global average)
        annual = usage * 12 * factor
        return {"predicted_annual_co2_kg": round(annual, 2), "input_summary": {"monthly_kwh": usage}}
