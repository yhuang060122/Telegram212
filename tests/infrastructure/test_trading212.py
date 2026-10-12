from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock, call

import pytest
import requests
from requests.auth import HTTPBasicAuth

import app.infrastructure.trading212 as t212_module
from app.domain.cashflow import CashFlowType
from app.infrastructure.trading212 import Trading212Client


@pytest.fixture
def client():
    """Create a client without requiring real API credentials."""
    instance = Trading212Client.__new__(Trading212Client)
    instance.session = MagicMock()
    return instance


@pytest.fixture
def transaction():
    return {
        "reference": "tx-001",
        "dateTime": "2026-10-10T12:30:00Z",
        "amount": "100.50",
        "currency": "EUR",
        "type": "DEPOSIT",
    }


def make_response(
    status_code=200,
    json_data=None,
    text="",
    headers=None,
    url="https://live.trading212.com/api/v0/equity/test",
):
    response = MagicMock()
    response.status_code = status_code
    response.text = text
    response.headers = headers or {}
    response.json.return_value = json_data
    response.request.url = url
    response.raise_for_status.return_value = None
    return response


class TestTrading212Initialization:
    def test_missing_api_key(self, monkeypatch):
        monkeypatch.delenv("T212_API_KEY", raising=False)
        monkeypatch.setenv("T212_API_SECRET", "secret")

        with pytest.raises(ValueError, match="T212_API_KEY missing"):
            Trading212Client()

    def test_missing_api_secret(self, monkeypatch):
        monkeypatch.setenv("T212_API_KEY", "key")
        monkeypatch.delenv("T212_API_SECRET", raising=False)

        with pytest.raises(ValueError, match="T212_API_SECRET missing"):
            Trading212Client()

    def test_initializes_session_with_basic_auth(self, monkeypatch):
        session = MagicMock()
        monkeypatch.setenv("T212_API_KEY", "test-key")
        monkeypatch.setenv("T212_API_SECRET", "test-secret")
        monkeypatch.setattr(
            t212_module.requests,
            "Session",
            lambda: session,
        )

        instance = Trading212Client()

        assert instance.session is session
        assert isinstance(session.auth, HTTPBasicAuth)
        assert session.auth.username == "test-key"
        assert session.auth.password == "test-secret"

    def test_close_closes_session(self, client):
        client.close()

        client.session.close.assert_called_once_with()


class TestTrading212Get:
    def test_get_returns_json(self, client, monkeypatch):
        response = make_response(json_data={"ok": True})
        client.session.get.return_value = response
        success = MagicMock()
        monkeypatch.setattr(t212_module.log, "success", success)

        result = client._get("account/summary")

        assert result == {"ok": True}
        client.session.get.assert_called_once_with(
            f"{client.BASE_URL}/account/summary",
            params=None,
            timeout=20,
        )
        response.raise_for_status.assert_called_once_with()
        success.assert_called_once()

    def test_get_passes_query_parameters(self, client):
        response = make_response(json_data=[{"id": 1}])
        client.session.get.return_value = response
        params = {"limit": 50}

        result = client._get("positions", params=params)

        assert result == [{"id": 1}]
        client.session.get.assert_called_once_with(
            f"{client.BASE_URL}/positions",
            params=params,
            timeout=20,
        )

    def test_get_logs_non_200_response(self, client, monkeypatch):
        response = make_response(
            status_code=500,
            text="Internal Server Error",
        )
        response.raise_for_status.side_effect = requests.HTTPError("500 Server Error")
        client.session.get.return_value = response
        error_log = MagicMock()
        monkeypatch.setattr(t212_module.log, "error", error_log)
        monkeypatch.setattr(t212_module.log, "success", MagicMock())

        with pytest.raises(requests.HTTPError):
            client._get("positions")

        error_log.assert_called_once()
        response.raise_for_status.assert_called_once_with()

    def test_get_retries_after_rate_limit(self, client, monkeypatch):
        limited = make_response(
            status_code=429,
            headers={"Retry-After": "3"},
        )
        success = make_response(json_data={"ok": True})
        client.session.get.side_effect = [limited, success]
        sleep = MagicMock()
        monkeypatch.setattr(t212_module, "sleep", sleep)
        monkeypatch.setattr(t212_module.log, "error", MagicMock())
        monkeypatch.setattr(t212_module.log, "success", MagicMock())

        result = client._get("positions")

        assert result == {"ok": True}
        assert client.session.get.call_count == 2
        sleep.assert_called_once_with(3)

    def test_get_uses_default_retry_delay(self, client, monkeypatch):
        limited = make_response(status_code=429)
        success = make_response(json_data=[])
        client.session.get.side_effect = [limited, success]
        sleep = MagicMock()
        monkeypatch.setattr(t212_module, "sleep", sleep)
        monkeypatch.setattr(t212_module.log, "error", MagicMock())
        monkeypatch.setattr(t212_module.log, "success", MagicMock())

        client._get("positions")

        sleep.assert_called_once_with(60)

    def test_get_propagates_request_exception(self, client):
        client.session.get.side_effect = requests.Timeout("request timed out")

        with pytest.raises(requests.Timeout):
            client._get("positions")


class TestPortfolioEndpoints:
    def test_account_summary(self, client):
        expected = {"totalValue": 1000}
        client._get = MagicMock(return_value=expected)

        result = client.account_summary()

        assert result == expected
        client._get.assert_called_once_with("account/summary")

    def test_positions(self, client):
        expected = [{"ticker": "AAPL"}]
        client._get = MagicMock(return_value=expected)

        result = client.positions()

        assert result == expected
        client._get.assert_called_once_with("positions")


class TestCashflowConversion:
    @pytest.mark.parametrize(
        ("tx_type", "amount", "expected_type", "expected_amount"),
        [
            ("DEPOSIT", "100.50", CashFlowType.DEPOSIT, "-100.50"),
            ("WITHDRAW", "50", CashFlowType.WITHDRAWAL, "50"),
            ("FEE", "2.25", CashFlowType.FEE, "-2.25"),
            (
                "INTEREST_ON_FREE_CASH",
                "1.25",
                CashFlowType.INTEREST,
                "1.25",
            ),
            (
                "LENDING_INTEREST",
                "0.75",
                CashFlowType.INTEREST,
                "0.75",
            ),
            ("TRANSFER", "20", CashFlowType.TRANSFER, "0"),
        ],
    )
    def test_converts_transaction_types(
        self,
        transaction,
        tx_type,
        amount,
        expected_type,
        expected_amount,
    ):
        transaction["type"] = tx_type
        transaction["amount"] = amount

        result = Trading212Client._to_cashflow(transaction)

        assert result.reference == transaction["reference"]
        assert result.type == expected_type
        assert result.amount == Decimal(expected_amount)
        assert result.currency == "EUR"
        assert result.datetime == datetime(2026, 10, 10, 12, 30, tzinfo=timezone.utc)

    def test_unknown_transaction_type_raises_key_error(self, transaction):
        transaction["type"] = "UNKNOWN_TYPE"

        with pytest.raises(KeyError, match="UNKNOWN_TYPE"):
            Trading212Client._to_cashflow(transaction)

    def test_invalid_datetime_raises_value_error(self, transaction):
        transaction["dateTime"] = "not-a-date"

        with pytest.raises(ValueError):
            Trading212Client._to_cashflow(transaction)


class TestTransactionsSince:
    def test_fetches_transactions_since_reference(self, client, transaction):
        client._get = MagicMock(
            return_value={
                "items": [transaction],
                "nextPagePath": None,
            }
        )

        result = client.transactions_since("cursor-123")

        assert len(result) == 1
        assert result[0].reference == "tx-001"

        endpoint, params = client._get.call_args.args

        assert endpoint == "history/transactions"
        assert params["cursor"] == "cursor-123"
        assert params["limit"] == 50

        # Validate ISO 8601 UTC timestamp without mocking datetime.now().
        timestamp = datetime.fromisoformat(params["time"].replace("Z", "+00:00"))
        assert timestamp.tzinfo == timezone.utc

    def test_returns_empty_list_when_no_transactions(self, client):
        client._get = MagicMock(return_value={"items": [], "nextPagePath": None})

        assert client.transactions_since(None) == []

    def test_stops_after_first_page_when_next_page_exists(
        self, client, transaction, monkeypatch
    ):
        client._get = MagicMock(
            return_value={
                "items": [transaction],
                "nextPagePath": ("/api/v0/equity/history/transactions?cursor=next"),
            }
        )
        monkeypatch.setattr(t212_module, "sleep", MagicMock())

        result = client.transactions_since(None)

        assert len(result) == 1
        client._get.assert_called_once()
        t212_module.sleep.assert_not_called()


class TestTransactions:
    def test_fetches_transactions(self, client, transaction):
        client._get = MagicMock(
            return_value={
                "items": [transaction],
                "nextPagePath": None,
            }
        )

        result = client.transactions()

        assert len(result) == 1
        assert result[0].reference == "tx-001"
        client._get.assert_called_once_with(
            "history/transactions",
            {"limit": 50},
        )

    def test_sorts_transactions_by_datetime(self, client):
        later = {
            "reference": "later",
            "dateTime": "2026-10-12T12:00:00Z",
            "amount": "10",
            "currency": "EUR",
            "type": "DEPOSIT",
        }
        earlier = {
            "reference": "earlier",
            "dateTime": "2026-10-10T12:00:00Z",
            "amount": "20",
            "currency": "EUR",
            "type": "WITHDRAW",
        }
        client._get = MagicMock(
            return_value={
                "items": [later, earlier],
                "nextPagePath": None,
            }
        )

        result = client.transactions()

        assert [item.reference for item in result] == [
            "earlier",
            "later",
        ]

    def test_stops_after_five_page_transitions(self, client, transaction, monkeypatch):
        page = {
            "items": [transaction],
            "nextPagePath": ("/api/v0/equity/history/transactions?cursor=next"),
        }
        client._get = MagicMock(return_value=page)
        sleep = MagicMock()
        monkeypatch.setattr(t212_module, "sleep", sleep)

        result = client.transactions()

        # Current implementation stops after five page transitions.
        assert len(result) == 5
        assert client._get.call_count == 5
        assert sleep.call_count == 4
        sleep.assert_has_calls([call(10)] * 4)
