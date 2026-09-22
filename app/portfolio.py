from collections import defaultdict


class Portfolio:

    def __init__(self, summary: dict, positions: list):
        """
        summary  : GET /equity/account/summary
        positions: GET /equity/positions
        """
        self.summary = summary
        self.positions = positions

    # ---------- Account ----------

    @property
    def currency(self):
        return self.summary["currency"]

    @property
    def cash_available_to_trade(self):
        return self.summary["cash"]["availableToTrade"]

    @property
    def cash_reserved(self):
        return self.summary["cash"]["reservedForOrders"]

    @property
    def cash_in_pies(self):
        return self.summary["cash"]["inPies"]

    @property
    def total_value(self):
        return self.summary["totalValue"]

    @property
    def invested(self):
        return self.summary["investments"]["totalCost"]

    @property
    def current_value(self):
        return self.summary["investments"]["currentValue"]

    @property
    def unrealized_pnl(self):
        return self.summary["investments"]["unrealizedProfitLoss"]

    @property
    def realized_pnl(self):
        return self.summary["investments"]["realizedProfitLoss"]

    @property
    def return_pct(self):
        if self.invested == 0:
            return 0
        return self.unrealized_pnl / self.invested * 100

    @property
    def cash_ratio(self):
        if self.total_value == 0:
            return 0
        return (self.cash_available_to_trade + self.cash_reserved) / self.total_value * 100

    # ---------- Positions ----------

    def position_weights(self):
        """每个仓位占组合比例"""
        weights = {}

        for p in self.positions:
            ticker = p["instrument"]["ticker"]
            value = p["walletImpact"]["currentValue"]

            weights[ticker] = round(
                value / self.total_value * 100,
                2
            )

        return weights

    def top_positions(self, sector_map=None):
        """按市值排序"""

        if sector_map is None:
            sector_map = {}

        weights = self.position_weights()

        data = []

        for p in self.positions:
            ticker = p["instrument"]["ticker"]

            data.append({
                "ticker": ticker,
                "name": p["instrument"]["name"],
                "quantity": p["quantity"],
                "avg_price": p["averagePricePaid"],
                "current_price": p["currentPrice"],
                "market_value": p["walletImpact"]["currentValue"],
                "cost": p["walletImpact"]["totalCost"],
                "pnl": p["walletImpact"]["unrealizedProfitLoss"],
                "weight": weights[ticker],
                "fx_impact": p["walletImpact"]["fxImpact"],
                "inst_currency": p["instrument"]["currency"],
                "return_pct": round(
                    p["walletImpact"]["unrealizedProfitLoss"] / p["walletImpact"]["totalCost"] * 100,
                    2
                ) if p["walletImpact"]["totalCost"] else 0,
                "sector": sector_map.get(
                    ticker,
                    "Unknown"
                ),
            })

        return sorted(
            data,
            key=lambda x: x["market_value"],
            reverse=True
        )

    # ---------- Sector ----------

    def sector_allocation(self, sector_map: dict):
        """
        sector_map = {
            'NVDA_US_EQ':'AI',
            'AAPL_US_EQ':'Consumer Tech'
        }
        """

        sectors = defaultdict(float)

        for p in self.positions:
            ticker = p["instrument"]["ticker"]
            sector = sector_map.get(ticker, "Unknown")

            sectors[sector] += p["walletImpact"]["currentValue"]

        return {
            k: round(v / self.total_value * 100, 1)
            for k, v in sectors.items()
        }

    # ---------- Risk ----------

    def concentration(self):

        weights = sorted(
            self.position_weights().values(),
            reverse=True
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
            "risk": risk
        }

    # ---------- Report ----------

    def report(self):

        lines = [
            "=" * 50,
            "Portfolio Summary",
            "=" * 50,
            f"Portfolio Value : {self.currency} {self.total_value:,.2f}",
            f"Available Cash  : {self.currency} {self.cash_available_to_trade:,.2f}",
            f"Cash Ratio      : {self.cash_ratio:.2f}%",
            f"Invested Cost   : {self.currency} {self.invested:,.2f}",
            f"Current Value   : {self.currency} {self.current_value:,.2f}",
            f"Unrealized P/L  : {self.currency} {self.unrealized_pnl:,.2f}",
            f"Return          : {self.return_pct:.2f}%",
            "",
            "Top Positions"
        ]

        for p in self.top_positions():

            rtn = (
                p["pnl"] / p["cost"] * 100
                if p["cost"]
                else 0
            )

            lines.append(
                f"{p['ticker']:<12}"
                f"{p['weight']:>6.2f}%   "
                f"{rtn:+6.2f}%"
            )

        return "\n".join(lines)