from datetime import date

from pydantic import BaseModel, ConfigDict

from app.domain.portfolio import PortfolioSnapshot
from app.domain.position import Position
from app.domain.report import Report


class PortfolioResponse(BaseModel):
    """Portfolio data reconstructed from persisted snapshot data."""

    model_config = ConfigDict(frozen=True)

    snapshot_date: date
    currency: str

    total_value: float
    current_value: float
    invested: float

    cash: float
    cash_ratio: float

    unrealized_pnl: float
    realized_pnl: float

    positions: list[Position]


class PositionsResponse(BaseModel):
    count: int
    items: list[Position]


class HistoryResponse(BaseModel):
    days: int
    count: int
    items: list[PortfolioSnapshot]


class LatestReportResponse(BaseModel):
    report: Report
