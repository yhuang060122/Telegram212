from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

import app.telegram.handlers as handlers


@pytest.fixture
def services(monkeypatch):
    """隔离所有外部服务，避免真实 API 和数据库调用。"""
    portfolio_service = MagicMock()
    research_service = MagicMock()
    analyst_service = MagicMock()
    analytics_service = MagicMock()
    repo = MagicMock()

    monkeypatch.setattr(handlers, "portfolio_service", portfolio_service)
    monkeypatch.setattr(handlers, "research_service", research_service)
    monkeypatch.setattr(handlers, "analyst_service", analyst_service)
    monkeypatch.setattr(handlers, "analytics_service", analytics_service)
    monkeypatch.setattr(handlers, "repo", repo)

    portfolio = make_portfolio()
    portfolio_service.build.return_value = portfolio

    return SimpleNamespace(
        portfolio_service=portfolio_service,
        research_service=research_service,
        analyst_service=analyst_service,
        analytics_service=analytics_service,
        repo=repo,
        portfolio=portfolio,
    )


def make_position(
    ticker="NVDA_US_EQ",
    name="NVIDIA",
    weight=20.0,
    quantity=2.0,
    return_pct=10.0,
):
    return SimpleNamespace(
        ticker=ticker,
        name=name,
        weight=weight,
        quantity=quantity,
        avg_price=100.0,
        current_price=110.0,
        market_value=220.0,
        cost=200.0,
        pnl=20.0,
        return_pct=return_pct,
        sector="Technology",
        currency="USD",
    )


def make_portfolio(positions=None):
    positions = positions or []

    return SimpleNamespace(
        total_value=10000.0,
        cash=2000.0,
        cash_available=2000.0,
        cash_ratio=20.0,
        invested=8000.0,
        current_value=8000.0,
        unrealized_pnl=500.0,
        realized_pnl=100.0,
        return_pct=5.0,
        currency="EUR",
        positions=positions,
        top_positions=positions,
        get_position=MagicMock(return_value=None),
    )


# ------------------------------------------------------------------
# load_portfolio
# ------------------------------------------------------------------


def test_load_portfolio_calls_portfolio_service(services):
    result = handlers.load_portfolio()

    assert result is services.portfolio
    services.portfolio_service.build.assert_called_once_with()


# ------------------------------------------------------------------
# /daily
# ------------------------------------------------------------------


def test_daily_builds_analytics_and_formats_report(services, monkeypatch):
    context = object()
    history = [{"snapshot_date": "2026-10-12"}]
    cashflows = [{"reference": "CF-001"}]
    analytics = object()
    report = object()

    services.research_service.build.return_value = context
    services.repo.history.return_value = history
    services.repo.cashflows.return_value = cashflows
    services.analytics_service.calculate.return_value = analytics
    services.analyst_service.analyze.return_value = report

    formatter = MagicMock(return_value="daily message")
    monkeypatch.setattr(handlers.Formatter, "daily", formatter)

    result = handlers.daily()

    assert result == "daily message"
    services.portfolio_service.build.assert_called_once_with()
    services.research_service.build.assert_called_once_with(services.portfolio)
    services.repo.history.assert_called_once_with(365)
    services.repo.cashflows.assert_called_once_with(365)
    services.analytics_service.calculate.assert_called_once_with(
        services.portfolio,
        history,
        cashflows,
    )
    services.analyst_service.analyze.assert_called_once_with(
        context=context,
        history=history,
        analytics=analytics,
    )
    formatter.assert_called_once_with(
        services.portfolio,
        analytics,
        report,
    )


# ------------------------------------------------------------------
# /portfolio
# ------------------------------------------------------------------


def test_portfolio_formats_current_portfolio(services, monkeypatch):
    formatter = MagicMock(return_value="portfolio message")
    monkeypatch.setattr(handlers.Formatter, "portfolio", formatter)

    result = handlers.portfolio()

    assert result == "portfolio message"
    formatter.assert_called_once_with(services.portfolio)


# ------------------------------------------------------------------
# /history
# ------------------------------------------------------------------


def test_history_requires_ticker():
    assert handlers.history("/history") == ("Usage: `/history NVDA`")


def test_history_queries_uppercase_ticker(services, monkeypatch):
    history_rows = [{"snapshot_date": "2026-10-12", "weight": 20.0}]
    services.repo.position_history.return_value = history_rows

    formatter = MagicMock(return_value="history message")
    monkeypatch.setattr(handlers.Formatter, "history", formatter)

    result = handlers.history("/history nvda")

    assert result == "history message"
    services.repo.position_history.assert_called_once_with("NVDA_US_EQ")
    formatter.assert_called_once_with("NVDA", history_rows)


def test_history_accepts_extra_arguments(services, monkeypatch):
    formatter = MagicMock(return_value="history message")
    monkeypatch.setattr(handlers.Formatter, "history", formatter)

    result = handlers.history("/history nvda extra")

    assert result == "history message"
    services.repo.position_history.assert_called_once_with("NVDA_US_EQ")


# ------------------------------------------------------------------
# /risk
# ------------------------------------------------------------------


def test_risk_calculates_and_formats_risk(services, monkeypatch):
    history = [{"snapshot_date": "2026-10-12"}]
    cashflows = [{"reference": "CF-001"}]
    analytics = object()

    services.repo.history.return_value = history
    services.repo.cashflows.return_value = cashflows
    services.analytics_service.calculate.return_value = analytics

    formatter = MagicMock(return_value="risk message")
    monkeypatch.setattr(handlers.Formatter, "risk", formatter)

    result = handlers.risk()

    assert result == "risk message"
    services.portfolio_service.build.assert_called_once_with()
    services.repo.history.assert_called_once_with(365)
    services.repo.cashflows.assert_called_once_with(365)
    services.analytics_service.calculate.assert_called_once_with(
        services.portfolio,
        history,
        cashflows,
    )
    formatter.assert_called_once_with(analytics)


# ------------------------------------------------------------------
# /performance
# ------------------------------------------------------------------


def test_performance_formats_metrics():
    analytics = SimpleNamespace(
        performance=SimpleNamespace(
            daily_return=1.2,
            weekly_return=2.5,
            monthly_return=-3.0,
            total_return=8.5,
            twr=7.2,
            xirr=6.8,
        )
    )

    result = handlers.performance(analytics)

    assert "Performance Metrics" in result
    assert "Daily" in result
    assert "+1.20%" in result
    assert "+2.50%" in result
    assert "-3.00%" in result
    assert "+8.50%" in result
    assert "+7.20%" in result
    assert "+6.80%" in result


# ------------------------------------------------------------------
# /stock
# ------------------------------------------------------------------


def test_analyze_stock_returns_message_if_not_held(services):
    result = handlers.analyze_stock("nvda")

    assert result == "❌ *NVDA* is not in your portfolio."
    services.portfolio_service.build.assert_called_once_with()
    services.research_service.build.assert_not_called()
    services.analyst_service.analyze.assert_not_called()


def test_analyze_stock_returns_unavailable_if_report_is_none(services):
    position = make_position()
    services.portfolio.get_position.return_value = position

    services.research_service.build.return_value = object()
    services.repo.position_history.return_value = [{"weight": 20.0}]
    services.analyst_service.analyze.return_value = None

    result = handlers.analyze_stock("nvda")

    assert result == "⚠️ AI analysis unavailable for *NVDA*."
    services.portfolio.get_position.assert_called_once_with("NVDA_US_EQ")
    services.research_service.build.assert_called_once_with(
        portfolio=services.portfolio,
        tickers=["NVDA"],
    )
    services.repo.position_history.assert_called_once_with("NVDA_US_EQ")


def test_analyze_stock_formats_successful_report(services, monkeypatch):
    position = make_position()
    context = object()
    history = [{"weight": 15.0}, {"weight": 20.0}]
    report = object()

    services.portfolio.get_position.return_value = position
    services.research_service.build.return_value = context
    services.repo.position_history.return_value = history
    services.analyst_service.analyze.return_value = report

    formatter = MagicMock(return_value="stock analysis")
    monkeypatch.setattr(
        handlers.Formatter,
        "stock_analysis",
        formatter,
    )

    result = handlers.analyze_stock("nvda")

    assert result == "stock analysis"
    services.analyst_service.analyze.assert_called_once_with(
        context=context,
        history=history,
    )
    formatter.assert_called_once_with(
        position=position,
        report=report,
        pos_history=history,
    )


def test_analyze_stock_normalizes_ticker_to_uppercase(services, monkeypatch):
    position = make_position()
    services.portfolio.get_position.return_value = position
    services.research_service.build.return_value = object()
    services.repo.position_history.return_value = []
    services.analyst_service.analyze.return_value = None

    handlers.analyze_stock("nVdA")

    services.portfolio.get_position.assert_called_once_with("NVDA_US_EQ")
