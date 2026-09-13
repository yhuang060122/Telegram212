from dataclasses import dataclass

@dataclass
class Position:
    ticker: str
    name: str
    quantity: float
    avg_price: float
    current_price: float
    sector: str = "Unknown"

    @property
    def cost(self):
        return self.quantity * self.avg_price

    @property
    def market_value(self):
        return self.quantity * self.current_price

    @property
    def pnl(self):
        return self.market_value - self.cost

    @property
    def return_pct(self):
        if self.cost == 0:
            return 0
        return self.pnl / self.cost * 100