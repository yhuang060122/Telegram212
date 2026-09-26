from pydantic import BaseModel, ConfigDict, computed_field


class Position(BaseModel):
    """A normalized portfolio position"""

    model_config = ConfigDict(frozen=True)

    ticker: str
    name: str

    quantity: float

    avg_price: float
    current_price: float

    market_value: float
    cost: float
    pnl: float

    weight: float

    fx_impact: float = 0.0

    currency: str
    sector: str = "Unknown"

    @property
    def is_profitable(self) -> bool:
        return self.pnl >= 0

    @computed_field
    @property
    def return_pct(self) -> float:
        if self.cost == 0:
            return 0.0

        return round(self.pnl / self.cost * 100, 2)