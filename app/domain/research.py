from pydantic import BaseModel, ConfigDict, Field

from .earnings import EarningsEvent
from .macro import MacroData
from .news import NewsItem
from .portfolio import Portfolio


class CollectorStatus(BaseModel):
    """Status of each external data collector."""

    model_config = ConfigDict(frozen=True)

    status: str

    count: int = 0

    error: str | None = None


class ResearchContext(BaseModel):
    """Complete research package consumed by the AI analyst."""

    model_config = ConfigDict(frozen=True)

    portfolio: Portfolio

    news: list[NewsItem] = Field(default_factory=list)

    earnings: list[EarningsEvent] = Field(default_factory=list)

    macro: MacroData = Field(default_factory=MacroData)

    status: dict[str, CollectorStatus] = Field(
        default_factory=dict
    )

    def for_ticker(self, ticker: str) -> "ResearchContext":
        normalized = ticker.upper().replace("_US_EQ", "")

        return self.model_copy(
            update={
                "news": [
                    news
                    for news in self.news
                    if news.ticker == normalized
                ],
                "earnings": [
                    event
                    for event in self.earnings
                    if event.ticker == normalized
                ],
            }
        )