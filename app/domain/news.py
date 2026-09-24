from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, HttpUrl


class NewsItem(BaseModel):
    """News collected from Finnhub."""

    model_config = ConfigDict(frozen=True)

    ticker: str

    title: str
    summary: str

    source: str

    url: HttpUrl

    published_at: datetime

    sentiment: Literal[
        "Bullish",
        "Neutral",
        "Bearish",
        "Unknown",
    ] = "Unknown"

    relevance: float = 0.5