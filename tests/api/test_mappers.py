import pytest
from fastapi import HTTPException

from app.api.mappers import map_portfolio
from app.domain.position import Position


@pytest.fixture
def snapshot_rows() -> list[dict]:
    return [
        {
            "snapshot_date": "2026-10-11",
            "currency": "EUR",
            "total_value": 12_500.00,
            "current_value": 10_000.00,
            "invested": 9_000.00,
            "cash": 3_500.00,
            "cash_ratio": 28.0,
            "unrealized_pnl": 1_000.00,
            "realized_pnl": 250.00,
        }
    ]


@pytest.fixture
def positions() -> list[Position]:
    """模拟 Repository 返回的持仓。"""
    return [
        Position(
            ticker="AAPL",
            name="Apple Inc.",
            quantity=10,
            avg_price=150.0,
            current_price=180.0,
            market_value=1_800.0,
            cost=1_500.0,
            pnl=300.0,
            weight=18.0,
            currency="USD",
            sector="Technology",
        )
    ]


def test_map_portfolio_without_snapshot_returns_404(
    positions: list[Position],
) -> None:
    """没有快照时，Mapper 应抛出 HTTP 404。"""
    with pytest.raises(HTTPException) as exc_info:
        map_portfolio([], positions)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "No portfolio snapshot is available."


def test_map_portfolio_maps_snapshot_fields_correctly(
    snapshot_rows: list[dict],
    positions: list[Position],
) -> None:
    """确认快照字段和持仓被正确映射到 API Response。"""
    result = map_portfolio(snapshot_rows, positions)

    assert result.snapshot_date.isoformat() == "2026-10-11"
    assert result.currency == "EUR"
    assert result.total_value == 12_500.00
    assert result.current_value == 10_000.00
    assert result.invested == 9_000.00
    assert result.unrealized_pnl == 1_000.00
    assert result.realized_pnl == 250.00
    assert result.positions == positions


def test_map_portfolio_preserves_cash_amount_and_percentage(
    snapshot_rows: list[dict],
    positions: list[Position],
) -> None:
    """现金金额和现金占比应保持原值，不重复计算或缩放。"""
    result = map_portfolio(snapshot_rows, positions)

    assert result.cash == 3_500.00
    assert result.cash_ratio == 28.0

    # 明确区分金额和百分比：
    # 3,500 EUR / 12,500 EUR = 28%
    assert result.cash != result.cash_ratio
