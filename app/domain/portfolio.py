from datetime import date

from pydantic import BaseModel, ConfigDict

from .position import Position


class PortfolioSnapshot(BaseModel):
    snapshot_date: date
    total_value: float
    cash: float
    cash_ratio: float
    invested: float
    current_value: float
    unrealized_pnl: float
    realized_pnl: float
    currency: str


class Portfolio(BaseModel):
    """Normalized Trading212 portfolio."""
    model_config = ConfigDict(frozen=True)

    currency: str

    total_value: float
    current_value: float
    invested: float

    cash_available: float
    cash_reserved: float

    unrealized_pnl: float
    realized_pnl: float

    positions: list[Position]

    @property
    def cash(self):
        return self.cash_reserved + self.cash_available

    @property
    def cash_ratio(self) -> float:
        if self.total_value == 0:
            return 0
        return self.cash / self.total_value * 100

    @property
    def return_pct(self) -> float:
        if self.invested == 0:
            return 0
        return self.unrealized_pnl / self.invested * 100

    @property
    def top_positions(self) -> list[Position]:
        return sorted(
            self.positions,
            key=lambda position: position.market_value,
            reverse=True,
        )

    def get_position(self, ticker: str) -> Position | None:
        return next(
            (
                position
                for position in self.positions
                if position.ticker == ticker
            ),
            None,
        )
