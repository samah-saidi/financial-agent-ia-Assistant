from pydantic import BaseModel
from typing import Optional

class StockFeatures(BaseModel):
    Open: float
    High: float
    Low: float
    Close: float
    Volume: float
    Adj_Close: float 

class PredictionResponse(BaseModel):
    churn_probability: float  # Peut-être renommer en "up_probability" ?
    prediction: int
    risk_level: str

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
