from types import SimpleNamespace

import pytest

from app.telegram.formatter import Formatter


def ns(**kwargs):
    return SimpleNamespace(**kwargs)


def make_position(
    ticker="NVDA_US_EQ",
    name="NVIDIA",
    weight=20.0,
    quantity=2.0,
    avg_price=100.0,
    current_price=120.0,
    return_pct=20.0,
):
    return ns(
        ticker=ticker,
        name=name,
        weight=weight,
        quantity=quantity,
        avg_price=avg_price,
        current_price=current_price,
        return_pct=return_pct,
    )


def make_portfolio(positions=None):
    return ns(
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
        positions=positions or [],
        top_positions=positions or [],
    )


def make_analytics():
    concentration = ns(
        top1=30.0,
        top3=60.0,
        top5=80.0,
        herfindahl=0.25,
        risk_level="High",
    )
    performance = ns(
        daily_return=1.2,
        weekly_return=2.5,
        monthly_return=4.0,
        twr=8.0,
        xirr=7.5,
    )
    risk = ns(
        concentration=concentration,
        drawdown=-2.0,
        max_drawdown=-10.0,
        volatility=15.0,
        sharpe=1.25,
    )
    return ns(performance=performance, risk=risk)


def make_report(
    summary="Portfolio looks healthy.",
    sentiment="positive",
    rating="Buy",
):
    portfolio_rating = ns(
        overall_sentiment=sentiment,
        summary=summary,
        cash_strategy="Keep sufficient cash.",
        macro_outlook="Macro conditions are mixed.",
    )
    stock_rating = ns(
        rating=rating,
        rationale="Strong fundamentals.",
    )
    data_status = ns(
        trading212="ok",
        finnhub="failed",
        fred="partial",
        gemini="unknown",
    )
    return ns(
        portfolio_rating=portfolio_rating,
        positions_ratings=[stock_rating],
        data_status=data_status,
    )


def make_snapshot(total_value):
    return ns(total_value=total_value)


# ------------------------------------------------------------------
# Shared
# ------------------------------------------------------------------


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        ("ok", "✅"),
        ("failed", "❌"),
        ("partial", "⚠️"),
        ("unknown", "➖"),
        ("unexpected", "➖"),
    ],
)
def test_data_sources_status_icons(status, expected):
    report = make_report()
    report.data_status.trading212 = status

    result = Formatter.data_sources(report)

    assert f"Trading212  {expected}" in result


def test_data_sources_includes_all_providers():
    result = Formatter.data_sources(make_report())

    assert "Trading212" in result
    assert "Finnhub" in result
    assert "FRED" in result
    assert "Gemini" in result


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (12.345, "+12.35%"),
        (-1.234, "-1.23%"),
        (0, "+0.00%"),
        (None, "N/A"),
    ],
)
def test_pct(value, expected):
    assert Formatter.pct(value) == expected


# ------------------------------------------------------------------
# Daily
# ------------------------------------------------------------------


def test_daily_formats_metrics_and_report():
    result = Formatter.daily(
        make_portfolio(),
        make_analytics(),
        make_report(),
    )

    assert "Daily Portfolio Report" in result
    assert "Performance" in result
    assert "Risk" in result
    assert "Allocation" in result
    assert "Portfolio looks healthy." in result
    assert "+1.20%" in result
    assert "1.25" in result


def test_daily_handles_missing_report():
    result = Formatter.daily(
        make_portfolio(),
        make_analytics(),
        None,
    )

    assert "AI Summary" in result
    assert "Unavailable" in result


def test_daily_handles_missing_sharpe():
    analytics = make_analytics()
    analytics.risk.sharpe = None

    result = Formatter.daily(make_portfolio(), analytics, None)

    assert "Sharpe    : N/A" in result


# ------------------------------------------------------------------
# Portfolio
# ------------------------------------------------------------------


def test_portfolio_formats_top_holdings():
    positions = [
        make_position(),
        make_position(
            ticker="TSLA_US_EQ",
            name="Tesla",
            return_pct=-5.0,
        ),
    ]

    result = Formatter.portfolio(make_portfolio(positions))

    assert "Current Portfolio" in result
    assert "Total Value" in result
    assert "Available Cash" in result
    assert "NVDA" in result
    assert "TSLA" in result
    assert "🟢" in result
    assert "🔴" in result
    assert "_US_EQ" not in result


def test_portfolio_handles_no_positions():
    result = Formatter.portfolio(make_portfolio())

    assert "Current Portfolio" in result
    assert "Top Holdings" in result


def test_portfolio_limits_holdings_to_ten():
    positions = [make_position(ticker=f"STOCK{i}", weight=float(i)) for i in range(12)]

    result = Formatter.portfolio(make_portfolio(positions))

    assert "10. " in result
    assert "11. " not in result


# ------------------------------------------------------------------
# Risk
# ------------------------------------------------------------------


def test_risk_formats_risk_metrics():
    result = Formatter.risk(make_analytics())

    assert "Portfolio Risk" in result
    assert "Current DD" in result
    assert "Max DD" in result
    assert "Volatility" in result
    assert "Sharpe" in result
    assert "Top1" in result
    assert "HHI" in result
    assert "High" in result


# ------------------------------------------------------------------
# Stock analysis
# ------------------------------------------------------------------


@pytest.mark.parametrize(
    ("rating", "emoji"),
    [
        ("Buy", "🟢"),
        ("Hold", "🟡"),
        ("Reduce", "🔴"),
        ("Sell", "🔴"),
    ],
)
def test_stock_analysis_rating_icons(rating, emoji):
    position = make_position()
    report = make_report(rating=rating)

    result = Formatter.stock_analysis(position, report, [])

    assert emoji in result
    assert rating in result
    assert "N/A" in result
    assert "Strong fundamentals." in result


@pytest.mark.parametrize(
    ("first_weight", "last_weight", "expected"),
    [
        (10.0, 20.0, "Increasing"),
        (20.0, 10.0, "Decreasing"),
        (10.0, 10.0, "Stable"),
    ],
)
def test_stock_analysis_position_trend(
    first_weight,
    last_weight,
    expected,
):
    history = [
        {"weight": first_weight},
        {"weight": last_weight},
    ]

    result = Formatter.stock_analysis(
        make_position(),
        make_report(),
        history,
    )

    assert expected in result


# ------------------------------------------------------------------
# History
# ------------------------------------------------------------------


def test_history_handles_empty_data():
    result = Formatter.history("NVDA", [])

    assert "NVDA" in result
    assert "No historical data available." in result


@pytest.mark.parametrize(
    ("first", "last", "expected"),
    [
        (10.0, 20.0, "Increasing"),
        (20.0, 10.0, "Decreasing"),
        (10.0, 10.0, "Stable"),
    ],
)
def test_history_formats_trend(first, last, expected):
    history = [
        {
            "snapshot_date": "2026-10-01",
            "quantity": 2,
            "weight": first,
        },
        {
            "snapshot_date": "2026-10-12",
            "quantity": 3,
            "weight": last,
        },
    ]

    result = Formatter.history("NVDA", history)

    assert "NVDA" in result
    assert expected in result
    assert f"{last:.1f}%" in result
    assert "10-01" in result
    assert "10-12" in result


# ------------------------------------------------------------------
# Market close
# ------------------------------------------------------------------


def test_market_close_without_history_or_report():
    result = Formatter.market_close(
        make_portfolio(),
        None,
        [],
    )

    assert "Market Close Report" in result
    assert "Today's Change" in result
    assert "€+0.00" in result
    assert "AI Closing View" not in result


def test_market_close_positive_change_with_report():
    result = Formatter.market_close(
        make_portfolio(),
        make_report(),
        [
            make_snapshot(9000.0),
            make_snapshot(10000.0),
        ],
    )

    assert "🟢" in result
    assert "€+1,000.00" in result
    assert "+11.11%" in result
    assert "AI Closing View" in result
    assert "Portfolio looks healthy." in result


def test_market_close_negative_change():
    result = Formatter.market_close(
        make_portfolio(),
        None,
        [
            make_snapshot(10000.0),
            make_snapshot(9000.0),
        ],
    )

    assert "🔴" in result
    assert "€-1,000.00" in result
    assert "-10.00%" in result


def test_market_close_limits_top_holdings_to_five():
    positions = [make_position(ticker=f"STOCK{i}", weight=float(i)) for i in range(7)]

    result = Formatter.market_close(
        make_portfolio(positions),
        None,
        [],
    )

    assert "STOCK4" in result
    assert "STOCK5" not in result


# ------------------------------------------------------------------
# Help
# ------------------------------------------------------------------


def test_help_lists_commands():
    result = Formatter.help()

    assert "/daily" in result
    assert "/portfolio" in result
    assert "/risk" in result
    assert "/stock nvda" in result
    assert "/history NVDA" in result
