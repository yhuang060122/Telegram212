# app/schema.py

from pydantic import BaseModel
from typing import Literal

class PortfolioRating(BaseModel):
    overall_sentiment: Literal["Positive", "Neutral", "Negative"]
    summary: str
    cash_strategy: str
    macro_outlook: str

class PositionRating(BaseModel):
    ticker: str
    name: str
    rating: Literal["Buy", "Hold", "Reduce", "Sell"]
    rationale: str

class DataStatus(BaseModel):
    trading212: str = "ok"
    finnhub: str = "ok"
    fred: str = "ok"
    gemini: str = "ok"

class Report(BaseModel):
    portfolio_rating: PortfolioRating
    positions_ratings: list[PositionRating]
    data_status: DataStatus = DataStatus()