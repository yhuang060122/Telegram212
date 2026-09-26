from datetime import datetime
from decimal import Decimal

import pytest

from app.domain.cashflow import CashFlow, CashFlowType
from app.services.analytics_service import AnalyticsService
from tests.fixtures.history import create_history


class TestAnalyticsService:

    @pytest.fixture
    def service(self):
        return AnalyticsService()

    @pytest.fixture
    def simple_history(self):
        return [
            create_history(1, 10000, 1000),
            create_history(2, 11000, 1000),
        ]

    @pytest.fixture
    def drawdown_history(self):
        return [
            create_history(1, 100),
            create_history(2, 120),
            create_history(3, 110),
            create_history(4, 130),
            create_history(5, 100),
        ]

    @pytest.fixture
    def twr_history(self):
        return [
            create_history(1, 10000),
            create_history(2, 10200),
            create_history(3, 15500),
            create_history(4, 16000),
        ]

    @pytest.fixture
    def deposit_cashflow(self):
        return [
            CashFlow(
                reference="TX1",
                datetime=datetime(2026, 1, 3, 9, 0),
                amount=Decimal("-5000"),
                currency="EUR",
                type=CashFlowType.DEPOSIT,
            )
        ]

    # -------------------------------------------------
    # Daily Return
    # -------------------------------------------------

    def test_daily_return(self, service, simple_history, portfolio):
        analytics = service.calculate(
            portfolio=portfolio,
            history=simple_history,
            cashflows=[],
        )

        assert analytics.performance.daily_return == pytest.approx(10.0, abs=0.01)

    # -------------------------------------------------
    # Total Return
    # -------------------------------------------------

    def test_total_return(self, service, simple_history, portfolio):
        analytics = service.calculate(
            portfolio=portfolio,
            history=simple_history,
            cashflows=[],
        )

        assert analytics.performance.total_return == pytest.approx(10.0, abs=0.01)

    # -------------------------------------------------
    # Drawdown
    # -------------------------------------------------

    def test_current_drawdown(self, service, drawdown_history, portfolio):
        analytics = service.calculate(
            portfolio=portfolio,
            history=drawdown_history,
            cashflows=[],
        )

        assert analytics.risk.drawdown == pytest.approx(-23.08, abs=0.01)

    def test_max_drawdown(self, service, drawdown_history, portfolio):
        analytics = service.calculate(
            portfolio=portfolio,
            history=drawdown_history,
            cashflows=[],
        )

        assert analytics.risk.max_drawdown == pytest.approx(-23.08, abs=0.01)

    # -------------------------------------------------
    # Volatility
    # -------------------------------------------------

    def test_volatility_positive(self, service, drawdown_history, portfolio):
        analytics = service.calculate(
            portfolio=portfolio,
            history=drawdown_history,
            cashflows=[],
        )

        assert analytics.risk.volatility > 0

    # -------------------------------------------------
    # Sharpe
    # -------------------------------------------------

    def test_sharpe_exists(self, service, drawdown_history, portfolio):
        analytics = service.calculate(
            portfolio=portfolio,
            history=drawdown_history,
            cashflows=[],
            risk_free_rate=2.0,
        )

        assert analytics.risk.sharpe is not None

    # -------------------------------------------------
    # TWR
    # -------------------------------------------------

    def test_twr_without_cashflow(self, service, simple_history, portfolio):
        analytics = service.calculate(
            portfolio=portfolio,
            history=simple_history,
            cashflows=[],
        )

        assert analytics.performance.twr == pytest.approx(10.0, abs=0.01)

    def test_twr_with_deposit(self, service, twr_history, deposit_cashflow, portfolio):
        analytics = service.calculate(
            portfolio=portfolio,
            history=twr_history,
            cashflows=deposit_cashflow,
        )

        assert analytics.performance.twr == pytest.approx(6.86, abs=0.05)

    # -------------------------------------------------
    # XIRR
    # -------------------------------------------------

    def test_xirr_single_period(self, service, portfolio):
        flows = [
            CashFlow(
                reference="A",
                datetime=datetime(2026, 1, 1),
                amount=Decimal("-10000"),
                currency="EUR",
                type=CashFlowType.DEPOSIT,
            ),
            CashFlow(
                reference="B",
                datetime=datetime(2027, 1, 1),
                amount=Decimal("11000"),
                currency="EUR",
                type=CashFlowType.WITHDRAWAL,
            ),
        ]

        rate = service.calculate_xirr(portfolio, flows)

        assert rate == pytest.approx(10.0, abs=0.1)

    def test_xirr_multiple_cashflows(self, service, portfolio):
        flows = [
            CashFlow(
                reference="A",
                datetime=datetime(2026, 1, 1),
                amount=Decimal("-10000"),
                currency="EUR",
                type=CashFlowType.DEPOSIT,
            ),
            CashFlow(
                reference="B",
                datetime=datetime(2026, 6, 1),
                amount=Decimal("-5000"),
                currency="EUR",
                type=CashFlowType.DEPOSIT,
            ),
            CashFlow(
                reference="C",
                datetime=datetime(2027, 1, 1),
                amount=Decimal("17000"),
                currency="EUR",
                type=CashFlowType.WITHDRAWAL,
            ),
        ]

        rate = service.calculate_xirr(portfolio, flows)

        assert rate > 0

    # -------------------------------------------------
    # Empty History
    # -------------------------------------------------

    def test_empty_history(self, service, portfolio):
        analytics = service.calculate(
            portfolio=portfolio,
            history=[],
            cashflows=[],
        )

        assert analytics.performance.daily_return is None
        assert analytics.performance.twr is None
        assert analytics.risk.drawdown is None

    # -------------------------------------------------
    # One Snapshot
    # -------------------------------------------------

    def test_single_snapshot(self, service, portfolio):
        history = [
            create_history(1, 10000)
        ]

        analytics = service.calculate(
            portfolio=portfolio,
            history=history,
            cashflows=[],
        )

        assert analytics.performance.total_return == 0
        assert analytics.risk.volatility == 0
