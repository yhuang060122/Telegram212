from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict


class EarningsEvent(BaseModel):
    """Upcoming earnings event."""

    model_config = ConfigDict(frozen=True)

    ticker: str
    company: str

    earnings_date: date

    session: Literal[
        "BMO",
        "AMC",
        "UNKNOWN",
    ] = "UNKNOWN"

    eps_estimate: float | None = None

    revenue_estimate: float | None = None