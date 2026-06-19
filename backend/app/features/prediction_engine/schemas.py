from pydantic import BaseModel

class PredictionInput(BaseModel):
    features: dict

class PredictionOutput(BaseModel):
    prediction: float
    confidence: float
