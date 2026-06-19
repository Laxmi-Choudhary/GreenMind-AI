from pydantic import BaseModel

class BillInput(BaseModel):
    period_start: str
    period_end: str

class BillOutput(BaseModel):
    consumption_kwh: float
