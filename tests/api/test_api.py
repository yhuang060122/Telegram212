from fastapi.testclient import TestClient

from app.api.dependencies import get_analytics_service, get_repository
from app.api.main import app
from app.domain.analytics import (
    ConcentrationMetrics,
    PerformanceMetrics,
    PortfolioAnalytics,
    RiskMetrics,
)


class FakeRepository:
    def health_check(self):
        return True

    def latest_snapshot(self):
        return [
            {
                "snapshot_date": "2026-10-10",
                "total_value": 12000.0,
                "cash": 2000.0,
                "cash_ratio": 16.67,
                "invested": 10000.0,
                "current_value": 10000.0,
                "unrealized_pnl": 500.0,
                "realized_pnl": 100.0,
                "currency": "EUR",
            }
        ]

    def latest_positions(self):
        return []

    def history(self, days=30):
        return []

    def monthly_returns(self):
        return [{"month": "2026-10", "start": 10000, "end": 12000, "return_pct": 20}]

    def position_history(self, ticker):
        return []

    def cashflows(self, days=365):
        return []

    def latest_report(self):
        return None

    def today_news(self):
        return []

    def upcoming_earnings(self, days=30):
        return []

    def latest_macro(self):
        return None


class FakeAnalyticsService:
    def calculate(self, portfolio, history, cashflows):
        return PortfolioAnalytics(
            performance=PerformanceMetrics(total_return=5.0),
            risk=RiskMetrics(
                concentration=ConcentrationMetrics(
                    top1=0,
                    top3=0,
                    top5=0,
                    herfindahl=0,
                    risk_level="Low",
                ),
                drawdown=0,
                max_drawdown=0,
                volatility=None,
                sharpe=None,
            ),
        )


def setup_function():
    app.dependency_overrides[get_repository] = FakeRepository
    app.dependency_overrides[get_analytics_service] = FakeAnalyticsService


def teardown_function():
    app.dependency_overrides.clear()


def test_root_and_health():
    client = TestClient(app)
    assert client.get("/").status_code == 200
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_portfolio_endpoint_returns_snapshot_and_positions():
    response = TestClient(app).get("/api/portfolio")
    assert response.status_code == 200
    assert response.json()["snapshot"]["currency"] == "EUR"
    assert response.json()["positions"] == []


def test_history_validates_days_parameter():
    client = TestClient(app)
    assert client.get("/api/history?days=30").status_code == 200
    assert client.get("/api/history?days=0").status_code == 422


def test_monthly_returns_endpoint():
    response = TestClient(app).get("/api/monthly-returns")
    assert response.status_code == 200
    assert response.json()[0]["return_pct"] == 20


def test_latest_report_empty_is_json_null():
    response = TestClient(app).get("/api/report/latest")
    assert response.status_code == 200
    assert response.json() is None


def test_analytics_endpoint_uses_analytics_service():
    response = TestClient(app).get("/api/analytics")
    assert response.status_code == 200
    assert response.json()["performance"]["total_return"] == 5.0

def test_positions_history_news_earnings_and_macro_endpoints():
    client = TestClient(app)
    assert client.get("/api/positions").json() == []
    assert client.get("/api/positions/NVDA/history").json() == []
    assert client.get("/api/news").json() == []
    assert client.get("/api/earnings?days=14").json() == []
    assert client.get("/api/earnings?days=400").status_code == 422
    assert client.get("/api/macro/latest").json() is None

class UnhealthyRepository(FakeRepository):
    def health_check(self):
        return False

class EmptyPortfolioRepository(FakeRepository):
    def latest_snapshot(self):
        return []

def test_health_returns_503_when_database_is_unhealthy():
    app.dependency_overrides[get_repository] = UnhealthyRepository
    response = TestClient(app).get("/api/health")
    assert response.status_code == 503

def test_analytics_returns_404_when_no_snapshot_exists():
    app.dependency_overrides[get_repository] = EmptyPortfolioRepository
    response = TestClient(app).get("/api/analytics")
    assert response.status_code == 404
