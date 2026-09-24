from app.domain.earnings import EarningsEvent
from app.domain.macro import MacroData
from app.domain.news import NewsItem
from app.domain.research import CollectorStatus, ResearchContext
from app.domain.portfolio import Portfolio

from app.infrastructure.finnhub import FinnhubClient
from app.infrastructure.fred import FredClient

class ResearchService:
    def __init__(self):
        self.news_client = FinnhubClient()
        self.fred = FredClient()

    def build(
            self,
            portfolio: Portfolio,
            tickers: list[str] | None = None,
    ) -> ResearchContext:

        tickers = tickers or [
            p.ticker.replace("_US_EQ", "")
            for p in portfolio.positions
        ]
        news: list[NewsItem] = []
        earnings: list[EarningsEvent] = []
        macro = MacroData()
        status = {}

        # ---------- NEWS ----------

        try:

            news = self.news_client.news(tickers)

            status["news"] = CollectorStatus(
                status="ok",
                count=len(news),
            )

        except Exception as e:

            status["news"] = CollectorStatus(
                status="failed",
                error=str(e),
            )

        # ---------- EARNINGS ----------

        try:

            earnings = self.news_client.earnings(
                tickers
            )

            status["earnings"] = CollectorStatus(
                status="ok",
                count=len(earnings),
            )

        except Exception as e:

            status["earnings"] = CollectorStatus(
                status="failed",
                error=str(e),
            )

        # ---------- MACRO ----------

        try:

            macro = self.fred.snapshot()

            status["macro"] = CollectorStatus(
                status="ok",
                count=1,
            )

        except Exception as e:

            status["macro"] = CollectorStatus(
                status="failed",
                error=str(e),
            )

        return ResearchContext(
            portfolio=portfolio,
            news=news,
            earnings=earnings,
            macro=macro,
            status=status,
        )

