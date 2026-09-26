import pytest

from app.domain.portfolio import Portfolio


class TestPortfolio:

    def test_portfolio_type(self, portfolio):
        assert isinstance(portfolio, Portfolio)

    def test_cash_ratio(self, portfolio):
        assert portfolio.cash_ratio == pytest.approx(12.0968, abs=1e-3)

    def test_return_pct(self, portfolio):
        assert portfolio.return_pct == 9.0

    def test_top_positions(self, portfolio):
        top = portfolio.top_positions

        assert len(top) == 3
        assert top[0].ticker == "NVDA_US_EQ"

    def test_get_position(self, portfolio):
        nvda = portfolio.get_position("NVDA_US_EQ")

        assert nvda is not None
        assert nvda.name == "NVDA"

    def test_get_missing_position(self, portfolio):
        assert portfolio.get_position("TSLA_US_EQ") is None

    def test_total_weight(self, portfolio):
        total = sum(p.weight for p in portfolio.positions)

        assert total == 100

    def test_empty_portfolio(self):
        p = Portfolio(
            currency="EUR",
            total_value=0,
            invested=0,
            current_value=0,
            cash_available=0,
            cash_reserved=0,
            unrealized_pnl=0,
            realized_pnl=0,
            positions=[],
        )

        assert p.cash_ratio == 0
        assert p.return_pct == 0
        assert p.top_positions == []
