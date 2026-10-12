from datetime import date, datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

import app.infrastructure.supabase as supabase_module
from app.infrastructure.supabase import SupabaseClient


class FakeQuery:
    """模拟 Supabase 的链式查询接口。"""

    def __init__(self, data=None, error=None):
        self.data = data if data is not None else []
        self.error = error
        self.calls = []
        self.payload = None

    def select(self, *args, **kwargs):
        self.calls.append(("select", args, kwargs))
        return self

    def upsert(self, payload, **kwargs):
        self.payload = payload
        self.calls.append(("upsert", payload, kwargs))
        return self

    def order(self, *args, **kwargs):
        self.calls.append(("order", args, kwargs))
        return self

    def limit(self, *args, **kwargs):
        self.calls.append(("limit", args, kwargs))
        return self

    def eq(self, *args, **kwargs):
        self.calls.append(("eq", args, kwargs))
        return self

    def gte(self, *args, **kwargs):
        self.calls.append(("gte", args, kwargs))
        return self

    def execute(self):
        if self.error:
            raise self.error
        return SimpleNamespace(data=self.data)


@pytest.fixture
def client(monkeypatch):
    """创建不连接真实数据库的 SupabaseClient。"""
    instance = object.__new__(SupabaseClient)
    instance.db = MagicMock()
    return instance


def configure_queries(client, *queries):
    client.db.table.side_effect = queries


def make_position(**overrides):
    values = {
        "ticker": "NVDA",
        "name": "NVIDIA",
        "quantity": 2,
        "avg_price": 100.0,
        "current_price": 120.0,
        "market_value": 240.0,
        "cost": 200.0,
        "pnl": 40.0,
        "weight": 0.2,
        "return_pct": 20.0,
        "sector": "Technology",
        "fx_impact": 0.0,
        "currency": "USD",
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def make_portfolio(positions=None):
    return SimpleNamespace(
        positions=positions or [],
        total_value=1000.0,
        cash=200.0,
        cash_ratio=0.2,
        invested=800.0,
        current_value=800.0,
        unrealized_pnl=50.0,
        realized_pnl=10.0,
        currency="EUR",
    )


# ------------------------------------------------------------------
# Constructor
# ------------------------------------------------------------------


def test_init_requires_environment_variables(monkeypatch):
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_KEY", raising=False)

    with pytest.raises(ValueError, match="SUPABASE_URL"):
        SupabaseClient()


def test_init_creates_supabase_client(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-key")

    create_client = MagicMock(return_value=MagicMock())
    monkeypatch.setattr(supabase_module, "create_client", create_client)

    instance = SupabaseClient()

    create_client.assert_called_once_with(
        "https://example.supabase.co",
        "test-key",
    )
    assert instance.db is create_client.return_value


# ------------------------------------------------------------------
# Writes
# ------------------------------------------------------------------


def test_save_snapshot(client):
    query = FakeQuery()
    configure_queries(client, query)

    client.save_snapshot(make_portfolio())

    assert query.payload["total_value"] == 1000.0
    assert query.payload["cash"] == 200.0
    assert query.payload["currency"] == "EUR"
    assert query.payload["snapshot_date"] == date.today().isoformat()


def test_save_positions(client):
    query = FakeQuery()
    configure_queries(client, query)

    client.save_positions(make_portfolio([make_position()]))

    assert len(query.payload) == 1
    assert query.payload[0]["ticker"] == "NVDA"
    assert query.payload[0]["inst_currency"] == "USD"
    assert query.payload[0]["market_value"] == 240.0


def test_save_positions_with_empty_portfolio(client):
    query = FakeQuery()
    configure_queries(client, query)

    client.save_positions(make_portfolio())

    assert query.payload == []


def test_save_news_skips_empty_list(client):
    client.save_news([])

    client.db.table.assert_not_called()


def test_save_news_upserts_rows(client):
    query = FakeQuery()
    configure_queries(client, query)

    item = SimpleNamespace(
        published_at=datetime(2026, 10, 12, 10, 30),
        ticker="NVDA",
        title="Test news",
        summary="Test summary",
        source="Test source",
        url="https://example.com/news",
        sentiment="positive",
    )

    client.save_news([item])

    assert query.payload[0]["ticker"] == "NVDA"
    assert query.payload[0]["published_at"] == item.published_at.isoformat()
    assert query.payload[0]["url"] == "https://example.com/news"
    assert query.calls[-1][2]["on_conflict"] == ("ticker,published_at,url")


def test_save_earnings_skips_empty_list(client):
    client.save_earnings([])

    client.db.table.assert_not_called()


def test_save_earnings_upserts_rows(client):
    query = FakeQuery()
    configure_queries(client, query)

    event = SimpleNamespace(
        ticker="NVDA",
        company="NVIDIA",
        earnings_date=date(2026, 11, 18),
        session="amc",
        eps_estimate=1.2,
        revenue_estimate=50_000_000_000,
    )

    client.save_earnings([event])

    assert query.payload[0]["ticker"] == "NVDA"
    assert query.payload[0]["earnings_date"] == "2026-11-18"
    assert query.calls[-1][2]["on_conflict"] == ("ticker,earnings_date,session")


def test_save_macro(client):
    query = FakeQuery()
    configure_queries(client, query)

    macro = MagicMock()
    macro.model_dump.return_value = {"vix": 20.0}

    client.save_macro(macro)

    assert query.payload["vix"] == 20.0
    assert query.payload["snapshot_date"] == date.today().isoformat()


def test_save_report(client):
    query = FakeQuery()
    configure_queries(client, query)

    report = MagicMock()
    report.model_dump.return_value = {"summary": "Test report"}
    report.portfolio_rating.overall_sentiment = "positive"

    client.save_report(report)

    assert query.payload["report"] == {"summary": "Test report"}
    assert query.payload["overall_sentiment"] == "positive"


def test_save_cashflows_skips_empty_list(client):
    client.save_cashflows([])

    client.db.table.assert_not_called()


def test_save_cashflows_upserts_rows(client):
    query = FakeQuery()
    configure_queries(client, query)

    cashflow = SimpleNamespace(
        reference="CF-001",
        datetime=datetime(2026, 10, 12, 9, 0),
        amount=Decimal("125.50"),
        currency="EUR",
        type=SimpleNamespace(value="DIVIDEND"),
    )

    client.save_cashflows([cashflow])

    assert query.payload[0]["reference"] == "CF-001"
    assert query.payload[0]["amount"] == 125.5
    assert query.payload[0]["type"] == "DIVIDEND"
    assert query.calls[-1][2]["on_conflict"] == "reference"


# ------------------------------------------------------------------
# Reads
# ------------------------------------------------------------------


def test_latest_snapshot_returns_data(client):
    expected = [{"snapshot_date": "2026-10-12", "total_value": 1000}]
    query = FakeQuery(data=expected)
    configure_queries(client, query)

    assert client.latest_snapshot() == expected


def test_latest_positions_returns_empty_when_no_snapshot(client):
    query = FakeQuery(data=[])
    configure_queries(client, query)

    assert client.latest_positions() == []


def test_latest_positions_maps_database_rows(client, monkeypatch):
    snapshot_query = FakeQuery(data=[{"snapshot_date": "2026-10-12"}])
    positions_query = FakeQuery(
        data=[
            {
                "ticker": "NVDA",
                "name": "NVIDIA",
                "quantity": 2,
                "avg_price": 100.0,
                "current_price": 120.0,
                "market_value": 240.0,
                "pnl": 40.0,
                "weight": 0.2,
                "inst_currency": "USD",
                "sector": None,
            }
        ]
    )
    configure_queries(client, snapshot_query, positions_query)

    position_factory = MagicMock(return_value="mapped-position")
    monkeypatch.setattr(supabase_module, "Position", position_factory)

    result = client.latest_positions()

    assert result == ["mapped-position"]
    position_factory.assert_called_once_with(
        ticker="NVDA",
        name="NVIDIA",
        quantity=2,
        avg_price=100.0,
        current_price=120.0,
        market_value=240.0,
        cost=200.0,
        pnl=40.0,
        weight=0.2,
        fx_impact=0,
        currency="USD",
        sector="Unknown",
    )


def test_history_maps_rows(client, monkeypatch):
    query = FakeQuery(
        data=[
            {
                "snapshot_date": "2026-10-12",
                "total_value": 1000,
                "cash": 200,
                "cash_ratio": 0.2,
                "invested": 800,
                "current_value": 800,
                "unrealized_pnl": 50,
                "realized_pnl": 10,
                "currency": "EUR",
            }
        ]
    )
    configure_queries(client, query)

    factory = MagicMock(return_value="snapshot")
    monkeypatch.setattr(supabase_module, "PortfolioSnapshot", factory)

    assert client.history() == ["snapshot"]
    factory.assert_called_once()


def test_position_history_returns_rows(client):
    expected = [{"ticker": "NVDA"}]
    query = FakeQuery(data=expected)
    configure_queries(client, query)

    assert client.position_history("NVDA") == expected
    assert ("eq", ("ticker", "NVDA"), {}) in query.calls


def test_today_news_maps_rows(client, monkeypatch):
    query = FakeQuery(
        data=[
            {
                "ticker": "NVDA",
                "title": "Test",
                "summary": "Summary",
                "source": "Source",
                "url": "https://example.com",
                "published_at": "2026-10-12T10:00:00",
                "sentiment": "positive",
            }
        ]
    )
    configure_queries(client, query)

    factory = MagicMock(return_value="news-item")
    monkeypatch.setattr(supabase_module, "NewsItem", factory)

    assert client.today_news() == ["news-item"]
    factory.assert_called_once()


def test_latest_report_returns_none_when_empty(client):
    configure_queries(client, FakeQuery(data=[]))

    assert client.latest_report() is None


def test_latest_report_validates_report(client, monkeypatch):
    configure_queries(
        client,
        FakeQuery(data=[{"report": {"summary": "test"}}]),
    )

    expected = object()
    validate = MagicMock(return_value=expected)
    monkeypatch.setattr(
        supabase_module.Report,
        "model_validate",
        validate,
    )

    assert client.latest_report() is expected
    validate.assert_called_once_with({"summary": "test"})


def test_monthly_returns_empty_when_no_rows(client):
    configure_queries(client, FakeQuery(data=[]))

    assert client.monthly_returns() == []


def test_monthly_returns_groups_by_month(client):
    rows = [
        {"snapshot_date": "2026-01-01", "total_value": 100},
        {"snapshot_date": "2026-01-31", "total_value": 110},
        {"snapshot_date": "2026-02-01", "total_value": 110},
        {"snapshot_date": "2026-02-28", "total_value": 99},
        {"snapshot_date": "2026-03-01", "total_value": 0},
    ]
    configure_queries(client, FakeQuery(data=rows))

    result = client.monthly_returns()

    assert result == [
        {
            "month": "2026-01",
            "start": 100,
            "end": 110,
            "return_pct": 10.0,
        },
        {
            "month": "2026-02",
            "start": 110,
            "end": 99,
            "return_pct": -10.0,
        },
        {
            "month": "2026-03",
            "start": 0,
            "end": 0,
            "return_pct": 0,
        },
    ]


def test_health_check_returns_true(client):
    configure_queries(client, FakeQuery())

    assert client.health_check() is True


def test_health_check_returns_false_on_error(client):
    configure_queries(
        client,
        FakeQuery(error=RuntimeError("database unavailable")),
    )

    assert client.health_check() is False


def test_cashflows_maps_rows(client, monkeypatch):
    query = FakeQuery(
        data=[
            {
                "reference": "CF-001",
                "datetime": "2026-10-12T09:00:00",
                "amount": "125.50",
                "currency": "EUR",
                "type": "deposit",
            }
        ]
    )
    configure_queries(client, query)

    factory = MagicMock(return_value="cashflow")
    monkeypatch.setattr(supabase_module, "CashFlow", factory)

    assert client.cashflows() == ["cashflow"]
    factory.assert_called_once_with(
        reference="CF-001",
        datetime=datetime.fromisoformat("2026-10-12T09:00:00"),
        amount=Decimal("125.50"),
        currency="EUR",
        type=supabase_module.CashFlowType("deposit"),
    )


def test_cashflows_returns_empty_when_no_rows(client):
    configure_queries(client, FakeQuery(data=[]))

    assert client.cashflows() == []


def test_latest_cashflow_reference_returns_reference(client):
    configure_queries(
        client,
        FakeQuery(data=[{"reference": "CF-001"}]),
    )

    assert client.latest_cashflow_reference() == "CF-001"


def test_latest_cashflow_reference_returns_none(client):
    configure_queries(client, FakeQuery(data=[]))

    assert client.latest_cashflow_reference() is None
