from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class PortfolioRating(BaseModel):
    model_config = ConfigDict(frozen=True)

    overall_sentiment: Literal[
        "Positive",
        "Neutral",
        "Negative",
    ]

    summary: str

    cash_strategy: str

    macro_outlook: str


class PositionRating(BaseModel):
    model_config = ConfigDict(frozen=True)

    ticker: str

    name: str

    rating: Literal[
        "Buy",
        "Hold",
        "Reduce",
        "Sell",
    ]

    rationale: str


class DataStatus(BaseModel):
    model_config = ConfigDict(frozen=True)

    trading212: str = "ok"

    finnhub: str = "ok"

    fred: str = "ok"

    gemini: str = "ok"


class Report(BaseModel):
    """Final AI analysis report."""

    model_config = ConfigDict(frozen=True)

    portfolio_rating: PortfolioRating

    positions_ratings: list[PositionRating] = Field(
        default_factory=list
    )

    data_status: DataStatus = Field(
        default_factory=DataStatus
    )