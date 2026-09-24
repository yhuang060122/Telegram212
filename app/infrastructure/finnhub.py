import os
from datetime import date, timedelta, datetime

import requests
from dotenv import load_dotenv

from app.domain.news import NewsItem
from app.domain.earnings import EarningsEvent

from app.logger import log

load_dotenv()

class FinnhubClient:

    BASE_URL = "https://finnhub.io/api/v1"


    VALID_SENTIMENT = {
        "Bullish",
        "Neutral",
        "Bearish",
        "Unknown",
    }

    def __init__(self):

        self.api_key = os.getenv("FINNHUB_API_KEY")

        if not self.api_key:
            raise ValueError("FINNHUB_API_KEY missing")

    def _get(self, endpoint: str, **params):

        params["token"] = self.api_key

        r = requests.get(
            f"{self.BASE_URL}/{endpoint}",
            params=params,
            timeout=20,
        )

        r.raise_for_status()

        return r.json()

    # ---------------------------------
    # News
    # ---------------------------------

    def news(
        self,
        tickers: list[str],
    ) -> list[NewsItem]:

        today = date.today()
        start = today - timedelta(days=3)

        result: list[NewsItem] = []

        for ticker in tickers:

            try:
                items = self._get(
                    "company-news",
                    symbol=ticker,
                    _from=start.isoformat(),
                    to=today.isoformat(),
                )

                log.success(
                    "Finnhub",
                    f"{len(items)} news"
                )

                for item in items[:3]:
                    # sentiment = item.sentiment or "Unknown"
                    #
                    # if sentiment not in self.VALID_SENTIMENT:
                    #     sentiment = "Unknown"

                    result.append(
                        NewsItem(
                            ticker=ticker,
                            title=item["headline"],
                            summary=item.get("summary", ""),
                            source=item["source"],
                            url=item["url"],
                            published_at=datetime.fromtimestamp(
                                item["datetime"]
                            ),
                            sentiment="Unknown",
                        )
                    )
            except Exception as e:
                log.error(
                    "Finnhub",
                    str(e)
                )

        result.sort(
            key=lambda x: x.published_at,
            reverse=True,
        )

        return result

    # ---------------------------------
    # Earnings
    # ---------------------------------

    def earnings(
        self,
        tickers: list[str],
    ) -> list[EarningsEvent]:

        today = date.today()
        end = today + timedelta(days=14)

        try:
            data = self._get(
                "calendar/earnings",
                _from=today.isoformat(),
                to=end.isoformat(),
            )
            log.success(
                "Earnings",
                f"{len(data['earningsCalendar'])} earnings found"
            )
        except Exception as e:
            log.error(
                "Earnings",
                str(e)
            )
            return []

        events: list[EarningsEvent] = []

        for row in data.get("earningsCalendar", []):

            if row["symbol"] not in tickers:
                continue

            events.append(
                EarningsEvent(
                    ticker=row["symbol"],
                    company=row.get("company", ""),
                    earnings_date=datetime.strptime(
                        row["date"],
                        "%Y-%m-%d",
                    ).date(),
                    session=row.get("hour", "UNKNOWN"),
                    eps_estimate=row.get("epsEstimate"),
                    revenue_estimate=row.get("revenueEstimate"),
                )
            )

        log.success(
            "Earnings",
            f"{len(events)} earnings matched"
        )

        return sorted(
            events,
            key=lambda x: x.earnings_date,
        )