class BillAnalyzer:
    async def analyze_pdf(self, pdf_bytes):
        # Placeholder: parse PDF and extract monthly kWh
        return {"consumption": 0}

    async def analyze_consumption(self, data):
        """Estimate annual CO2 based on monthly_kwh or meter readings."""
        monthly = data.get("monthly_kwh")
        if monthly:
            factor = 0.233
            annual = float(monthly) * 12 * factor
            return {"predicted_annual_co2_kg": round(annual, 2), "monthly_kwh": float(monthly)}
        # fallback simplistic calculation from meter_readings
        readings = data.get("meter_readings") or []
        if readings:
            avg = sum(readings) / len(readings)
            factor = 0.233
            annual = avg * 12 * factor
            return {"predicted_annual_co2_kg": round(annual, 2), "monthly_kwh_estimate": round(avg,2)}
        return {"predicted_annual_co2_kg": 0.0}
