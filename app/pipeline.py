from app.trading212 import Trading212Client
from app.portfolio import Portfolio
from app.research import ResearchContext
from app.repository import Repository
from app.analyst import Analyst
from app.logger import log

class DailyPipeline:

    def __init__(self):
        self.repo = Repository()

        self.client = Trading212Client()
        self.analyst = Analyst()

    def run(self):

        # 1. Portfolio
        summary = self.client.account_summary()
        positions = self.client.positions()

        log.success(
            "Trading212",
            "Connected"
        )

        portfolio = Portfolio(summary, positions)

        log.success(
            "Portfolio",
            f"{len(portfolio.positions)} positions (€{portfolio.total_value:,.0f})"
        )

        # Persist today's data
        self.repo.db.save_snapshot(portfolio)
        self.repo.db.save_positions(portfolio)

        log.success(
            "Supabase",
            "Snapshot and Positions Saved"
        )

        # 2. Research
        context = ResearchContext.build(portfolio)

        # Persist today's data
        if context.news:
            self.repo.db.save_news(context.news)

            log.success(
                "Supabase",
                "News Saved"
            )

        # Persist today's data
        if context.earnings:
            self.repo.db.save_earnings(context["earnings"])

            log.success(
                "Supabase",
                "Earnings Saved"
            )

        # TODO: add macro to supabase

        # 4. Load updated history
        history = self.repo.db.get_history(days=30)

        # 5. AI analysis (graceful fallback)
        report = self.analyst.analyze(
            context=context,
            history=history
        )

        if report is None:
            log.warning("Gemini", "No report generated")

            return portfolio, None, history

        log.success("Gemini", "Report generated")

        report.data_status.trading212 = "ok"
        report.data_status.finnhub = context.status.get("news", "failed")
        report.data_status.fred = context.status.get("macro", "failed")
        report.data_status.gemini = "ok"

        self.repo.db.save_report(report)

        log.success(
            "Supabase",
            "Report Saved"
        )

        return portfolio, report, history