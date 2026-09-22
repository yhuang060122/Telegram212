from app.trading212 import Trading212Client
from app.portfolio import Portfolio
from app.research import ResearchContext
from app.repository import Repository
from app.analyst import Analyst

class DailyPipeline:

    def __init__(self):
        self.repo = Repository()

        self.client = Trading212Client()
        self.analyst = Analyst()

    def run(self):

        # 1. Portfolio
        summary = self.client.account_summary()
        positions = self.client.positions()

        portfolio = Portfolio(summary, positions)

        # 2. Research
        context = ResearchContext.build(portfolio)

        # 3. Persist today's data
        self.repo.db.save_snapshot(portfolio)
        self.repo.db.save_positions(portfolio)
        self.repo.db.save_news(context["news"])
        self.repo.db.save_earnings(context["earnings"])

        # 4. Load updated history
        history = self.repo.db.get_history(days=30)

        # 5. AI analysis (graceful fallback)
        report = self.analyst.analyze(
            context=context,
            history=history
        )

        self.repo.db.save_report(report)

        return portfolio, report, history