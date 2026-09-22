from app.collectors.news import NewsCollector
from app.collectors.earnings import EarningsCollector
from app.collectors.macro import MacroCollector
from app.portfolio import Portfolio
from dataclasses import dataclass


@dataclass
class ResearchContext:

    portfolio: Portfolio

    news: list
    earnings: list
    macro: dict

    status: dict

    @classmethod
    def build(cls, portfolio):

        status = {}

        tickers = [
            p["ticker"].replace("_US_EQ", "")
            for p in portfolio.top_positions()
        ]

        try:
            news = NewsCollector().collect(tickers)
            status["news"] = "ok"
        except Exception:
            news = []
            status["news"] = "failed"

        try:
            earnings = EarningsCollector().collect(tickers)
            status["earnings"] = "ok"
        except Exception:
            earnings = []
            status["earnings"] = "failed"

        try:
            macro = MacroCollector().collect()
            status["macro"] = "ok"
        except Exception:
            macro = {}
            status["macro"] = "failed"

        return cls(
            portfolio=portfolio,
            news=news,
            earnings=earnings,
            macro=macro,
            status=status,
        )