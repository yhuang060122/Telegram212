from dataclasses import dataclass
from datetime import date, timedelta
import os

from app.collectors.base import BaseCollector, CollectorError
from app.logger import log

@dataclass
class EarningsEvent:
    ticker: str
    company: str
    date: str
    session: str
    eps_estimate: float | None


class EarningsCollector(BaseCollector):

    BASE = "https://finnhub.io/api/v1"

    def __init__(self):
        self.api_key = os.getenv("FINNHUB_API_KEY")

    def collect(self, tickers: list[str]) -> list[EarningsEvent]:

        if not tickers:
            return []

        today = date.today()
        future = today + timedelta(days=14)

        try:
            data = self.safe_get(
                f"{self.BASE}/calendar/earnings",
                {
                    "from": today.isoformat(),
                    "to": future.isoformat(),
                    "token": self.api_key,
                },
            )
            log.success(
                "Earnings",
                f"{len(data['earningsCalendar'])} earnings found"
            )
        except CollectorError as e:
            log.error(
                "Earnings",
                str(e)
            )
            return []

        calendar = data.get("earningsCalendar", [])
        watch = set(tickers)

        result: list[EarningsEvent] = []

        for e in calendar:

            symbol = e.get("symbol")
            if symbol not in watch:
                continue

            result.append(
                EarningsEvent(
                    ticker=symbol,
                    company=e.get("company", ""),
                    date=e.get("date", ""),
                    session=e.get("hour", "Unknown"),
                    eps_estimate=e.get("epsEstimate"),
                )
            )

        log.success(
            "Earnings",
            f"{len(result)} earnings matched"
        )

        return result