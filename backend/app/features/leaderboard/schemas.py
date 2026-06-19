from pydantic import BaseModel

class LeaderEntry(BaseModel):
    user_id: str
    points: int

class LeaderboardOutput(BaseModel):
    leaders: list
