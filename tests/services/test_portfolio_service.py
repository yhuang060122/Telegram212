import json
from unittest.mock import MagicMock

import pytest

import app.services.portfolio_service as portfolio_module
from app.domain.portfolio import Portfolio
from app.services.portfolio_service import PortfolioService


@pytest.fixture
def service(tmp_path, monkeypatch):
    """Create PortfolioService with mocked dependencies and sector data."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "sectors.json").write_text(
        json.dumps(
            {
                "AAPL_US_EQ": "Technology",
                "NVDA_US_EQ": "Semiconductors",
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)

    client = MagicMock()
    db = MagicMock()

    monkeypatch.setattr(
        portfolio_module,
        "Trading212Client",
        lambda: client,
    )
    monkeypatch.setattr(
        portfolio_module,
        "SupabaseClient",
        lambda: db,
    )

    instance = PortfolioService()

    # Expose mocks for assertions in each test.
    instance.client = client
    instance.db = db

    return instance


@pytest.fixture
def account_summary():
    return {
        "currency": "EUR",
        "totalValue": 12_000,
        "investments": {
            "currentValue": 10_000,
            "totalCost": 9_000,
            "unrealizedProfitLoss": 1_000,
            "realizedProfitLoss": 200,
        },
        "cash": {
            "availableToTrade": 1_500,
            "reservedForOrders": 500,
        },
    }


@pytest.fixture
def raw_position():
    return {
        "instrument": {
            "ticker": "AAPL_US_EQ",
            "name": "Apple",
            "currency": "USD",
        },
        "quantity": 10,
        "averagePricePaid": 150,
        "currentPrice": 180,
        "walletImpact": {
            "totalCost": 1_500,
            "unrealizedProfitLoss": 300,
            "currentValue": 1_800,
            "fxImpact": 25,
        },
    }


class TestPortfolioServiceBuild:
    def test_build_returns_portfolio(self, service, account_summary, raw_position):
        service.client.account_summary.return_value = account_summary
        service.client.positions.return_value = [raw_position]

        result = service.build()

        assert isinstance(result, Portfolio)
        assert result.currency == "EUR"
        assert result.total_value == 12_000
        assert result.invested == 9_000
        assert result.current_value == 10_000
        assert result.cash_available == 1_500
        assert result.cash_reserved == 500
        assert result.unrealized_pnl == 1_000
        assert result.realized_pnl == 200

        service.client.account_summary.assert_called_once_with()
        service.client.positions.assert_called_once_with()

    def test_build_maps_position_fields(self, service, account_summary, raw_position):
        service.client.account_summary.return_value = account_summary
        service.client.positions.return_value = [raw_position]

        result = service.build()
        position = result.positions[0]

        assert position.ticker == "AAPL_US_EQ"
        assert position.name == "Apple"
        assert position.quantity == 10
        assert position.avg_price == 150
        assert position.current_price == 180
        assert position.market_value == 1_800
        assert position.cost == 1_500
        assert position.pnl == 300
        assert position.weight == 18.0
        assert position.fx_impact == 25
        assert position.currency == "USD"
        assert position.sector == "Technology"

    def test_unknown_sector_defaults_to_unknown(
        self, service, account_summary, raw_position
    ):
        raw_position["instrument"]["ticker"] = "UNKNOWN_US_EQ"
        service.client.account_summary.return_value = account_summary
        service.client.positions.return_value = [raw_position]

        result = service.build()

        assert result.positions[0].sector == "Unknown"

    def test_missing_fx_impact_defaults_to_zero(
        self, service, account_summary, raw_position
    ):
        raw_position["walletImpact"].pop("fxImpact")
        service.client.account_summary.return_value = account_summary
        service.client.positions.return_value = [raw_position]

        result = service.build()

        assert result.positions[0].fx_impact == 0.0

    def test_none_fx_impact_defaults_to_zero(
        self, service, account_summary, raw_position
    ):
        raw_position["walletImpact"]["fxImpact"] = None
        service.client.account_summary.return_value = account_summary
        service.client.positions.return_value = [raw_position]

        result = service.build()

        assert result.positions[0].fx_impact == 0.0

    def test_empty_positions(self, service, account_summary):
        service.client.account_summary.return_value = account_summary
        service.client.positions.return_value = []

        result = service.build()

        assert result.positions == []
        assert result.total_value == 12_000

    def test_zero_current_value_gives_zero_weight(
        self, service, account_summary, raw_position
    ):
        account_summary["investments"]["currentValue"] = 0
        raw_position["walletImpact"]["currentValue"] = 500

        service.client.account_summary.return_value = account_summary
        service.client.positions.return_value = [raw_position]

        result = service.build()

        assert result.positions[0].weight == 0

    def test_weights_are_rounded_to_two_decimals(
        self, service, account_summary, raw_position
    ):
        account_summary["investments"]["currentValue"] = 3
        raw_position["walletImpact"]["currentValue"] = 1

        service.client.account_summary.return_value = account_summary
        service.client.positions.return_value = [raw_position]

        result = service.build()

        assert result.positions[0].weight == 33.33

    def test_missing_sector_file_uses_unknown(
        self, tmp_path, monkeypatch, account_summary, raw_position
    ):
        monkeypatch.chdir(tmp_path)

        client = MagicMock()
        db = MagicMock()

        monkeypatch.setattr(portfolio_module, "Trading212Client", lambda: client)
        monkeypatch.setattr(portfolio_module, "SupabaseClient", lambda: db)

        service = PortfolioService()
        client.account_summary.return_value = account_summary
        client.positions.return_value = [raw_position]

        result = service.build()

        assert result.positions[0].sector == "Unknown"


class TestPortfolioServiceSyncCashflows:
    def test_sync_cashflows_saves_flows(self, service, monkeypatch):
        latest = "2026-10-10T00:00:00Z"
        flows = [{"id": "flow-1"}, {"id": "flow-2"}]

        service.db.latest_cashflow_reference.return_value = latest
        service.client.transactions_since.return_value = flows

        success = MagicMock()
        monkeypatch.setattr(portfolio_module.log, "success", success)

        service.sync_cashflows()

        service.db.latest_cashflow_reference.assert_called_once_with()
        service.client.transactions_since.assert_called_once_with(latest)
        service.db.save_cashflows.assert_called_once_with(flows)
        success.assert_called_once_with(
            "Cashflows",
            "sync 2 cashflows",
        )

    def test_sync_cashflows_when_no_flows(self, service, monkeypatch):
        service.db.latest_cashflow_reference.return_value = None
        service.client.transactions_since.return_value = []

        success = MagicMock()
        monkeypatch.setattr(portfolio_module.log, "success", success)

        service.sync_cashflows()

        service.client.transactions_since.assert_called_once_with(None)
        service.db.save_cashflows.assert_called_once_with([])
        success.assert_called_once_with(
            "Cashflows",
            "sync 0 cashflows",
        )

    def test_sync_cashflows_propagates_client_error(self, service):
        service.db.latest_cashflow_reference.return_value = None
        service.client.transactions_since.side_effect = RuntimeError(
            "Trading212 unavailable"
        )

        with pytest.raises(RuntimeError, match="Trading212 unavailable"):
            service.sync_cashflows()

        service.db.save_cashflows.assert_not_called()
