from app.storage import Storage

from app.domain.portfolio import Portfolio
from app.domain.news import NewsItem
from app.domain.earnings import EarningsEvent
from app.domain.macro import MacroData
from app.domain.report import Report
from app.domain.position import Position


class Repository:

    def __init__(self):
        self.storage = Storage()

    @property
    def _db(self):
        return self.storage.client

    def health_check(self) -> bool:
        return self._db.health_check()

    # =====================================================
    # Write
    # =====================================================

    def save_snapshot(self, portfolio: Portfolio):
        self._db.save_snapshot(portfolio)

    def save_positions(self, portfolio: Portfolio):
        self._db.save_positions(portfolio)

    def save_news(self, news: list[NewsItem]):
        self._db.save_news(news)

    def save_earnings(self, earnings: list[EarningsEvent]):
        self._db.save_earnings(earnings)

    def save_macro(self, macro: MacroData):
        self._db.save_macro(macro)

    def save_report(self, report: Report):
        self._db.save_report(report)

    # =====================================================
    # Read
    # =====================================================

    def latest_snapshot(self):
        return self._db.latest_snapshot()

    def latest_positions(self) -> list[Position]:
        return self._db.latest_positions()

    def latest_report(self) -> Report | None:
        return self._db.latest_report()

    def today_news(self) -> list[NewsItem]:
        return self._db.today_news()

    def history(self, days: int = 30):
        return self._db.history(days)

    def position_history(self, ticker: str):
        return self._db.position_history(ticker)

    def monthly_returns(self):
        return self._db.monthly_returns()