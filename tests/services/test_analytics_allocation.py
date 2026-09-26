import pytest

from app.services.analytics_service import AnalyticsService


class TestAllocationMetrics:

    @pytest.fixture
    def service(self):
        return AnalyticsService()

    def test_sector_allocation(self, service, portfolio):
        """
        Portfolio Fixture

        NVDA 40%  Technology
        MSFT 35%  Technology
        AAPL 25%  Technology

        Technology = 100%
        """

        analytics = service.calculate(
            portfolio=portfolio,
            history=[],
            cashflows=[],
        )

        sector = {}

        assert len(sector) == 1
        assert sector["Technology"] == pytest.approx(100.0)

    def test_hhi(self, service, portfolio):
        """
        HHI = Σ(weight²)

        0.40² + 0.35² + 0.25²
        = 0.345
        """

        analytics = service.calculate(
            portfolio=portfolio,
            history=[],
            cashflows=[],
        )

        assert analytics.risk.concentration.herfindahl == pytest.approx(0.345, abs=0.001)

    def test_concentration(self, service, portfolio):
        """
        Top1 = 40
        Top3 = 100
        Top5 = 100
        """

        analytics = service.calculate(
            portfolio=portfolio,
            history=[],
            cashflows=[],
        )

        c = analytics.risk.concentration

        assert c.top1 == pytest.approx(40.0)
        assert c.top3 == pytest.approx(100.0)
        assert c.top5 == pytest.approx(100.0)
        assert c.risk_level == "High"

    def test_single_sector(self, service, portfolio):
        """
        All positions are Technology.
        """

        analytics = service.calculate(
            portfolio=portfolio,
            history=[],
            cashflows=[],
        )

        assert list(analytics.risk.sector.keys()) == ["Technology"]

    def test_concentration_bounds(self, service, portfolio):
        """
        Concentration should always satisfy

        Top1 ≤ Top3 ≤ Top5 ≤ 100
        """

        analytics = service.calculate(
            portfolio=portfolio,
            history=[],
            cashflows=[],
        )

        c = analytics.risk.concentration

        assert c.top1 <= c.top3
        assert c.top3 <= c.top5
        assert c.top5 <= 100
