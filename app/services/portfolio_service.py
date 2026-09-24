import json
from pathlib import Path

from app.domain.portfolio import Portfolio
from app.domain.position import Position
from app.infrastructure.trading212 import Trading212Client

class PortfolioService:

    def __init__(self):
        self.client = Trading212Client()

        path = Path("data/sectors.json")

        self.sectors = (json.loads(path.read_text()) if path.exists() else {})

    def build(self) -> Portfolio:

        summary = self.client.account_summary()

        raw_positions = self.client.positions()

        total_current =float(summary["investments"]["currentValue"])

        positions = []

        for raw in raw_positions:

            instrument = raw["instrument"]
            impact = raw["walletImpact"]

            cost = float(impact["totalCost"])
            pnl = float(impact["unrealizedProfitLoss"])

            current = float(impact["currentValue"])

            weight = current / total_current * 100 if total_current else 0

            positions.append(
                Position(
                    ticker=instrument["ticker"],
                    name=instrument["name"],
                    quantity=float(raw["quantity"]),
                    avg_price=float(raw["averagePricePaid"]),
                    current_price=float(raw["currentPrice"]),
                    market_value=current,
                    cost=cost,
                    pnl=pnl,
                    weight=round(weight, 2),
                    fx_impact=float(impact.get("fxImpact") or 0.0),
                    currency=instrument["currency"],
                    sector=self.sectors.get(
                        instrument["ticker"],
                        "Unknown",
                    ),
                )
            )

        return Portfolio(
            currency=summary["currency"],
            total_value=float(
                summary["totalValue"]
            ),
            invested=float(
                summary["investments"]["totalCost"]
            ),
            cash_available=float(
                summary["cash"]["availableToTrade"]
            ),
            cash_reserved=float(
                summary["cash"]["reservedForOrders"]
            ),
            unrealized_pnl=float(
                summary["investments"]["unrealizedProfitLoss"]
            ),
            current_value=float(
                summary["investments"]["currentValue"]
            ),
            realized_pnl=float(
                summary["investments"]["realizedProfitLoss"]
            ),
            positions=positions,
        )
