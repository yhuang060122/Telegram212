from unittest.mock import MagicMock

import pytest

from app.domain.earnings import EarningsEvent
from app.domain.macro import MacroData
from app.domain.news import NewsItem
from app.domain.position import Position
from app.domain.research import ResearchContext
from app.services.research_service import ResearchService


@pytest.fixture
def service():
    """Create ResearchService without real external API clients."""
    instance = ResearchService()
    instance.news_client = MagicMock()
    instance.fred = MagicMock()
    return instance


@pytest.fixture
def portfolio():
    from tests.fixtures.portfolio import create_portfolio

    return create_portfolio()


@pytest.fixture
def macro_data():
    """Build a valid MacroData instance using its defaults."""
    return MacroData()


def make_position(ticker: str) -> Position:
    return Position(
        ticker=ticker,
        name=ticker,
        quantity=10,
        avg_price=100,
        current_price=110,
        market_value=1100,
        cost=1000,
        pnl=100,
        weight=50,
        currency="USD",
        sector="Technology",
    )


class TestResearchServiceBuild:
    def test_returns_research_context(self, service, portfolio, macro_data):
        service.news_client.news.return_value = []
        service.news_client.earnings.return_value = []
        service.fred.snapshot.return_value = macro_data

        result = service.build(portfolio)

        assert isinstance(result, ResearchContext)
        assert result.portfolio is portfolio
        assert result.news == []
        assert result.earnings == []
        assert result.macro == macro_data
        assert set(result.status) == {"news", "earnings", "macro"}

    def test_uses_tickers_from_portfolio(self, service, portfolio, macro_data):
        portfolio = portfolio.model_copy(
            update={
                "positions": [
                    make_position("AAPL_US_EQ"),
                    make_position("NVDA_US_EQ"),
                ]
            }
        )

        service.news_client.news.return_value = []
        service.news_client.earnings.return_value = []
        service.fred.snapshot.return_value = macro_data

        result = service.build(portfolio)

        service.news_client.news.assert_called_once_with(["AAPL", "NVDA"])
        service.news_client.earnings.assert_called_once_with(["AAPL", "NVDA"])
        assert result.portfolio is portfolio

    def test_uses_explicit_tickers(self, service, portfolio, macro_data):
        service.news_client.news.return_value = []
        service.news_client.earnings.return_value = []
        service.fred.snapshot.return_value = macro_data

        service.build(portfolio, tickers=["MSFT", "TSLA"])

        service.news_client.news.assert_called_once_with(["MSFT", "TSLA"])
        service.news_client.earnings.assert_called_once_with(["MSFT", "TSLA"])

    def test_news_success(self, service, portfolio, macro_data):
        news_item = MagicMock(spec=NewsItem)
        service.news_client.news.return_value = [news_item]
        service.news_client.earnings.return_value = []
        service.fred.snapshot.return_value = macro_data

        result = service.build(portfolio)

        assert result.news == [news_item]
        assert result.status["news"].status == "ok"
        assert result.status["news"].count == 1

    def test_news_empty(self, service, portfolio, macro_data):
        service.news_client.news.return_value = []
        service.news_client.earnings.return_value = []
        service.fred.snapshot.return_value = macro_data

        result = service.build(portfolio)

        assert result.status["news"].status == "empty"
        assert result.status["news"].count == 0

    def test_news_failure_does_not_stop_other_collectors(
        self, service, portfolio, macro_data
    ):
        service.news_client.news.side_effect = RuntimeError("Finnhub news unavailable")
        service.news_client.earnings.return_value = []
        service.fred.snapshot.return_value = macro_data

        result = service.build(portfolio)

        assert result.status["news"].status == "failed"
        assert result.status["news"].error == "Finnhub news unavailable"
        assert result.status["earnings"].status in {
            "ok",
            "empty",
        }
        service.fred.snapshot.assert_called_once()

    def test_earnings_success(self, service, portfolio, macro_data):
        event = MagicMock(spec=EarningsEvent)
        service.news_client.news.return_value = []
        service.news_client.earnings.return_value = [event]
        service.fred.snapshot.return_value = macro_data

        result = service.build(portfolio)

        assert result.earnings == [event]
        assert result.status["earnings"].status == "ok"
        assert result.status["earnings"].count == 1

    def test_earnings_empty(self, service, portfolio, macro_data):
        service.news_client.news.return_value = []
        service.news_client.earnings.return_value = []
        service.fred.snapshot.return_value = macro_data

        result = service.build(portfolio)

        assert result.status["earnings"].status == "empty"
        assert result.status["earnings"].count == 0

    def test_earnings_failure(self, service, portfolio, macro_data):
        service.news_client.news.return_value = []
        service.news_client.earnings.side_effect = RuntimeError(
            "Earnings API unavailable"
        )
        service.fred.snapshot.return_value = macro_data

        result = service.build(portfolio)

        assert result.status["earnings"].status == "failed"
        assert result.status["earnings"].error == "Earnings API unavailable"
        service.fred.snapshot.assert_called_once()

    def test_macro_failure(self, service, portfolio):
        service.news_client.news.return_value = []
        service.news_client.earnings.return_value = []
        service.fred.snapshot.side_effect = RuntimeError("FRED unavailable")

        result = service.build(portfolio)

        assert result.status["macro"].status == "failed"
        assert result.status["macro"].error == "FRED unavailable"
        assert result.macro == MacroData()

    def test_all_collectors_can_fail(self, service, portfolio):
        service.news_client.news.side_effect = RuntimeError("News error")
        service.news_client.earnings.side_effect = RuntimeError("Earnings error")
        service.fred.snapshot.side_effect = RuntimeError("Macro error")

        result = service.build(portfolio)

        assert result.status["news"].status == "failed"
        assert result.status["earnings"].status == "failed"
        assert result.status["macro"].status == "failed"
        assert result.news == []
        assert result.earnings == []
        assert result.macro == MacroData()

    def test_empty_ticker_list_falls_back_to_portfolio(
        self, service, portfolio, macro_data
    ):
        portfolio = portfolio.model_copy(
            update={"positions": [make_position("AAPL_US_EQ")]}
        )

        service.news_client.news.return_value = []
        service.news_client.earnings.return_value = []
        service.fred.snapshot.return_value = macro_data

        service.build(portfolio, tickers=[])

        service.news_client.news.assert_called_once_with(["AAPL"])
        service.news_client.earnings.assert_called_once_with(["AAPL"])
