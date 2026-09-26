import pytest
from pydantic import ValidationError

from app.domain.position import Position


def create_position(cost=1000, current=1200):
    return Position(
        ticker="NVDA_US_EQ",
        name="NVIDIA",
        quantity=10,
        avg_price=100,
        current_price=current / 10,
        market_value=current,
        cost=cost,
        pnl=current - cost,
        weight=20,
        fx_impact=0,
        currency="EUR",
        sector="Technology",
    )


class TestPosition:

    def test_create_position(self):
        p = create_position()

        assert p.ticker == "NVDA_US_EQ"
        assert p.quantity == 10
        assert p.market_value == 1200

    def test_return_pct_profit(self):
        p = create_position()

        assert p.return_pct == 20.0

    def test_return_pct_loss(self):
        p = create_position(1000, 800)

        assert p.return_pct == -20.0

    def test_zero_cost(self):
        p = create_position(cost=0, current=500)

        assert p.return_pct == 0

    def test_is_profitable(self):
        assert create_position(1000, 1200).is_profitable
        assert not create_position(1000, 800).is_profitable

    def test_frozen_model(self):
        p = create_position()

        with pytest.raises(ValidationError):
            p.weight = 50

    def test_invalid_currency(self):
        with pytest.raises(ValidationError):
            Position(
                ticker="NVDA_US_EQ",
                name="NVIDIA",
                quantity=1,
                avg_price=1,
                current_price=1,
                market_value=1,
                cost=1,
                pnl=0,
                weight=1,
                fx_impact=0,
                currency=None,
                sector="Technology",
            )
