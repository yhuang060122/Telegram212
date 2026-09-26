from app.domain.portfolio import Portfolio
from app.domain.position import Position


def create_position(
        ticker: str,
        weight: float,
        cost: float,
        current: float,
        sector: str = "Technology",
) -> Position:
    quantity = 10

    return Position(
        ticker=f"{ticker}_US_EQ",
        name=ticker,
        quantity=quantity,
        avg_price=cost / quantity,
        current_price=current / quantity,
        market_value=current,
        cost=cost,
        pnl=current - cost,
        weight=weight,
        fx_impact=0,
        currency="EUR",
        sector=sector,
    )


def create_portfolio() -> Portfolio:
    positions = [
        create_position("NVDA", 40, 4000, 4800),
        create_position("MSFT", 35, 3500, 3700),
        create_position("AAPL", 25, 2500, 2400),
    ]

    current_value = sum(p.market_value for p in positions)
    invested = sum(p.cost for p in positions)
    unrealized = sum(p.pnl for p in positions)

    cash_available = 1200
    cash_reserved = 300

    return Portfolio(
        currency="EUR",
        total_value=current_value + cash_available + cash_reserved,
        invested=invested,
        current_value=current_value,
        cash_available=cash_available,
        cash_reserved=cash_reserved,
        unrealized_pnl=unrealized,
        realized_pnl=150,
        positions=positions,
    )
