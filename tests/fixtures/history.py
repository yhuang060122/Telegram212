from datetime import date

from app.domain.portfolio import PortfolioSnapshot


def create_history(day: int, value: float, cash: float = 0) -> PortfolioSnapshot:
    current = value - cash

    return PortfolioSnapshot(
        snapshot_date=date(2026, 1, day),
        total_value=value,
        cash=cash,
        cash_ratio=round(cash / value * 100, 2) if value else 0,
        invested=current,
        current_value=current,
        unrealized_pnl=0,
        realized_pnl=0,
        currency="EUR",
    )
