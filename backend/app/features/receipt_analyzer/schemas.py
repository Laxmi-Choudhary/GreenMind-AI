from pydantic import BaseModel
from typing import List, Optional

class ReceiptItem(BaseModel):
    name: str
    price: float
    estimated_co2_kg: Optional[float] = None

class ReceiptOutput(BaseModel):
    items: List[ReceiptItem]
    total: float
    estimated_co2_kg: float
