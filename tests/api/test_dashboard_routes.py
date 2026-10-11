from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_repository
from app.api.main import app
from app.domain.position import Position
from app.domain.report import (
    DataStatus,
    PortfolioRating,
    PositionRating,
    Report,
)


@pytest.fixture
def repository():
    repo = Mock()
    app.dependency_overrides[get_repository] = lambda: repo

    yield repo

    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app)


def test_positions_endpoint(client, repository):
    repository.latest_positions.return_value = [
        Position(
            ticker="AAPL",
            name="Apple Inc.",
            quantity=10,
            avg_price=150,
            current_price=180,
            market_value=1800,
            cost=1500,
            pnl=300,
            weight=18,
            currency="USD",
            sector="Technology",
        )
    ]

    response = client.get("/api/positions")

    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert data["items"][0]["ticker"] == "AAPL"
    assert data["items"][0]["return_pct"] == 20.0


def test_history_endpoint(client, repository):
    repository.history.return_value = []

    response = client.get("/api/history?days=30")

    assert response.status_code == 200
    assert response.json() == {
        "days": 30,
        "count": 0,
        "items": [],
    }
    repository.history.assert_called_once_with(days=30)


@pytest.mark.parametrize("days", [0, 366])
def test_history_rejects_invalid_days(client, repository, days):
    response = client.get(f"/api/history?days={days}")

    assert response.status_code == 422
    repository.history.assert_not_called()


def test_latest_report_endpoint(client, repository):
    repository.latest_report.return_value = Report(
        portfolio_rating=PortfolioRating(
            overall_sentiment="Positive",
            summary="Test summary",
            cash_strategy="Test cash strategy",
            macro_outlook="Test macro outlook",
        ),
        positions_ratings=[
            PositionRating(
                ticker="AAPL",
                name="Apple Inc.",
                rating="Hold",
                rationale="Test rationale",
            )
        ],
        data_status=DataStatus(),
    )

    response = client.get("/api/reports/latest")

    assert response.status_code == 200
    data = response.json()
    assert data["report"]["portfolio_rating"]["overall_sentiment"] == "Positive"
    assert data["report"]["positions_ratings"][0]["ticker"] == "AAPL"


def test_latest_report_returns_404_when_missing(client, repository):
    repository.latest_report.return_value = None

    response = client.get("/api/reports/latest")

    assert response.status_code == 404
    assert response.json()["detail"] == "No AI report is available."


def test_analytics_endpoint(client, repository, monkeypatch):
    from app.api.routes import analytics as analytics_route

    repository.latest_snapshot.return_value = [
        {
            "snapshot_date": "2026-10-11",
            "currency": "EUR",
            "total_value": 12500.0,
            "current_value": 10000.0,
            "invested": 9000.0,
            "cash": 3500.0,
            "cash_ratio": 28.0,
            "unrealized_pnl": 1000.0,
            "realized_pnl": 250.0,
        }
    ]
    repository.latest_positions.return_value = []
    repository.history.return_value = []
    repository.cashflows.return_value = []

    class FakeAnalyticsService:
        def calculate(self, portfolio, history, cashflows):
            assert portfolio.cash == 3500.0
            return {
                "performance": {"total_return": 10.0},
                "risk": {"volatility": 5.0},
                "sector_allocation": [],
                "position_allocation": [],
            }

    monkeypatch.setattr(
        analytics_route,
        "AnalyticsService",
        FakeAnalyticsService,
    )

    response = client.get("/api/analytics")

    assert response.status_code == 200
    data = response.json()
    assert data["performance"]["total_return"] == 10.0
    assert data["sector_allocation"] == []


def test_analytics_returns_404_without_snapshot(client, repository):
    repository.latest_snapshot.return_value = []

    response = client.get("/api/analytics")

    assert response.status_code == 404
    assert response.json()["detail"] == ("No portfolio snapshot is available.")
