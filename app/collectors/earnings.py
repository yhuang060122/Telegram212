from dataclasses import dataclass
from datetime import date, timedelta
import os
import requests

@dataclass
class EarningsEvent:
    ticker: str
    company: str
    date: str
    session: str
    eps_estimate: float | None


class EarningsCollector:

    BASE = "https://finnhub.io/api/v1"

    def __init__(self):
        self.api_key = os.getenv("FINNHUB_API_KEY")

    def collect(self, tickers: list[str]):

        today = date.today()
        future = today + timedelta(days=14)

        r = requests.get(
            f"{self.BASE}/calendar/earnings",
            params={
                "from": today.isoformat(),
                "to": future.isoformat(),
                "token": self.api_key
            },
            timeout=15
        )

        r.raise_for_status()

        calendar = r.json()["earningsCalendar"]

        result = []

        watch = set(tickers)

        for e in calendar:

            if e["symbol"] not in watch:
                continue

            result.append(
                EarningsEvent(
                    ticker=e["symbol"],
                    company=e["company"],
                    date=e["date"],
                    session=e["hour"],
                    eps_estimate=e.get("epsEstimate"),
                )
            )

        return result