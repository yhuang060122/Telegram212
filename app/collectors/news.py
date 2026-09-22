import os
from dataclasses import dataclass
from datetime import date, timedelta
from app.collectors.base import BaseCollector, CollectorError
from app.logger import log

@dataclass
class NewsItem:
    ticker: str
    title: str
    summary: str
    source: str
    url: str
    published_at: str
    sentiment: str = "Unknown"

class NewsCollector(BaseCollector):

    BASE_URL = "https://finnhub.io/api/v1"

    def __init__(self):
        self.api_key = os.getenv("FINNHUB_API_KEY")

    def _company_news(self, ticker: str):
        today = date.today()
        week = today - timedelta(days=3)

        url = f"{self.BASE_URL}/company-news"
        params = {
            "symbol": ticker,
            "form": week.isoformat(),
            "to": today.isoformat(),
            "token": self.api_key,
        }

        try:
            result = self.safe_get(url, params=params)

            log.success(
                "Finnhub",
                f"{len(result)} news"
            )

            return result

        except CollectorError as e:
            log.error(
                "Finnhub",
                str(e)
            )
            return []

    def collect(self, tickers: list[str]):

        results = []

        for ticker in tickers:
            news = self._company_news(ticker)

            for item in news[:3]:

                results.append(NewsItem(
                    ticker=ticker,
                    title=item["headline"],
                    summary=item["summary"],
                    source=item["source"],
                    url=item["url"],
                    published_at=item["datetime"],
                    )
                )
        return results
