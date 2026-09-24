from pydantic import BaseModel, ConfigDict
from .position import Position

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

    @property
    def sector_allocation(self) -> dict[str, float]:
        allocation: dict[str, float] = {}

        for position in self.positions:
            allocation[position.sector] = (
                allocation.get(position.sector, 0)
                + position.market_value
            )

        return {
            sector: round(value / self.total_value * 100, 1)
            for sector, value in allocation.items()
        }

    @property
    def concentration(self) -> dict[str, float | str]:
        weights = sorted(
            (position.weight for position in self.positions),
            reverse=True,
        )

        top5 = round(sum(weights[:5]), 1)

        if top5 >= 70:
            risk = "High"
        elif top5 >= 50:
            risk = "Medium"
        else:
            risk = "Low"

        return {
            "top5_weight": top5,
            "risk": risk,
        }

    def get_position(self, ticker: str) -> Position | None:
        return next(
            (
                position
                for position in self.positions
                if position.ticker == ticker
            ),
            None,
        )

    def position_weights(self):
        weights = {}

        for p in self.positions:
            ticker = p.ticker
            value = p.market_value

            weights[ticker] = round(
                value / self.total_value * 100,
                2
            )

        return weights