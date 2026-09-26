from datetime import datetime
from typing import cast

from pydantic import HttpUrl

from app.domain.macro import MacroData
from app.domain.news import NewsItem
from app.domain.research import (
    CollectorStatus,
    ResearchContext,
)


class TestResearch:

    def test_create_context(self, portfolio):
        context = ResearchContext(
            portfolio=portfolio,
            news=[],
            earnings=[],
            macro=MacroData(),
            status={},
        )

        assert context.portfolio.currency == "EUR"

    def test_for_ticker(self, portfolio):
        news = [
            NewsItem(
                ticker="NVDA",
                title="NVDA News",
                summary="NVIDIA released strong earnings.",
                source="Reuters",
                sentiment="Bullish",
                url=cast(HttpUrl, cast(object, "https://example.com/1")),
                published_at=datetime(2026, 1, 1, 10, 0),
            ),
            NewsItem(
                ticker="MSFT",
                title="MSFT News",
                summary="Microsoft announced Azure growth.",
                source="Reuters",
                sentiment="Neutral",
                url=cast(HttpUrl, cast(object, "https://example.com/2")),
                published_at=datetime(2026, 1, 1, 10, 0),
            ),
        ]

        context = ResearchContext(
            portfolio=portfolio,
            news=news,
            earnings=[],
            macro=MacroData(),
            status={},
        )

        nvda = context.for_ticker("NVDA")

        assert len(nvda.news) == 1
        assert nvda.news[0].ticker == "NVDA"

    def test_collector_status_ok(self):
        status = CollectorStatus(
            status="ok",
            count=12,
        )

        assert status.status == "ok"
        assert status.count == 12
        assert status.error is None

    def test_collector_status_failed(self):
        status = CollectorStatus(
            status="failed",
            error="401 Unauthorized",
        )

        assert status.status == "failed"
        assert status.error == "401 Unauthorized"

    def test_macro(self):
        macro = MacroData(
            fed_rate=4.25,
            us10y=4.11,
            dxy=105.3,
            vix=18.4,
        )

        assert macro.fed_rate == 4.25

    def test_empty_macro(self):
        macro = MacroData()

        assert macro.fed_rate is None
        assert macro.vix is None
