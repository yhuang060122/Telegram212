from unittest.mock import Mock

from fastapi.testclient import TestClient

from app.api.dependencies import get_repository
from app.api.main import app


def test_get_portfolio_returns_latest_snapshot() -> None:
    repository = Mock()

    repository.latest_snapshot.return_value = [
        {
            "snapshot_date": "2026-10-11",
            "currency": "EUR",
            "total_value": 12_500.0,
            "current_value": 10_000.0,
            "invested": 9_000.0,
            "cash": 3_500.0,
            "cash_ratio": 28.0,
            "unrealized_pnl": 1_000.0,
            "realized_pnl": 250.0,
        }
    ]
    repository.latest_positions.return_value = []

    app.dependency_overrides[get_repository] = lambda: repository

    try:
        with TestClient(app) as client:
            response = client.get("/api/portfolio")

        assert response.status_code == 200

        data = response.json()
        assert data["snapshot_date"] == "2026-10-11"
        assert data["currency"] == "EUR"
        assert data["cash"] == 3_500.0
        assert data["cash_ratio"] == 28.0
        assert data["positions"] == []

        repository.latest_snapshot.assert_called_once()
        repository.latest_positions.assert_called_once()
    finally:
        app.dependency_overrides.clear()


def test_get_portfolio_without_snapshot_returns_404() -> None:
    repository = Mock()
    repository.latest_snapshot.return_value = []
    repository.latest_positions.return_value = []

    app.dependency_overrides[get_repository] = lambda: repository

    try:
        with TestClient(app) as client:
            response = client.get("/api/portfolio")

        assert response.status_code == 404
        assert response.json()["detail"] == ("No portfolio snapshot is available.")
    finally:
        app.dependency_overrides.clear()
