from app.collectors.news import NewsCollector
from app.collectors.earnings import EarningsCollector
from app.collectors.macro import MacroCollector


class ResearchContext:

    @classmethod
    def build(cls, portfolio):

        tickers = [
            p["ticker"].replace("_US_EQ", "")
            for p in portfolio.top_positions()
        ]

        news = NewsCollector().collect(tickers)

        earnings = EarningsCollector().collect(tickers)

        macro = MacroCollector().collect()

        return {
            "portfolio": portfolio.to_gpt_json(),
            "news": [vars(n) for n in news],
            "earnings": [vars(e) for e in earnings],
            "macro": macro,
        }