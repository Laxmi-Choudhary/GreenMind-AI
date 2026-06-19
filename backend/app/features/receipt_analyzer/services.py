class ReceiptAnalyzer:
    async def parse_image(self, image_bytes):
        """Stub OCR + mapping: returns extracted items and estimated CO2.
        Replace with OCR (Tesseract/Cloud OCR) + item matching to emission factors.
        """
        # Very naive stub: return empty items and zero total
        return {"items": [], "total": 0.0, "estimated_co2_kg": 0.0}

    async def estimate_from_items(self, items):
        """Estimate CO2 from a list of items (each with name and price).
        This is a simplistic heuristic: price -> estimated weight -> CO2.
        """
        total = 0.0
        estimated_co2 = 0.0
        results = []
        for it in items:
            name = it.get("name")
            price = float(it.get("price", 0.0))
            total += price
            # heuristic: assume price roughly correlates with kg produced (very rough)
            kg = price * 0.1
            co2 = kg * 3.0  # assume 3 kgCO2 per kg product (placeholder)
            estimated_co2 += co2
            results.append({"name": name, "price": price, "estimated_co2_kg": round(co2, 2)})
        return {"items": results, "total": round(total, 2), "estimated_co2_kg": round(estimated_co2, 2)}
