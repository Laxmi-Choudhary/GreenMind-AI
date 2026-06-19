from pydantic import BaseModel

class GoalInput(BaseModel):
    title: str
    target_reduction_pct: float

class PlanOutput(BaseModel):
    id: str
    status: str
