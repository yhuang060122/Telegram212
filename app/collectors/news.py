import os
from dataclasses import dataclass
from datetime import date, timedelta

import requests

@dataclass
class NewsItem:
    ticker: str
    title: str
    summary: str
    source: str
    url: str
    published_at: str
    sentiment: str = "Unknown"

class NewsCollector:

    BASE_URL = "https://finnhub.io/api/v1"

    def __init__(self):
        self.api_key = os.getenv("FINNHUB_API_KEY")

    def _company_news(self, ticker: str):
        today = date.today()
        week = today - timedelta(days=3)

        r = requests.get(
            f"{self.BASE_URL}/company-news",
            params={
                "symbol": ticker,
                "form": week.isoformat(),
                "to": today.isoformat(),
                "token": self.api_key,
            },
            timeout=15
        )

        r.raise_for_status()

        return r.json()

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
