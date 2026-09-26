from app.infrastructure.trading212 import Trading212Client
from app.logger import log
from app.repository import Repository
from app.services.ai_analysis_service import AIAnalysisService
from app.services.analytics_service import AnalyticsService
from app.services.portfolio_service import PortfolioService
from app.services.research_service import ResearchService


class DailyPipeline:
    """Main application workflow."""

    def __init__(self):

        self.portfolio_service = PortfolioService()
        self.research_service = ResearchService()
        self.analyst_service = AIAnalysisService()
        self.trading212 = Trading212Client()
        self.analytics_service = AnalyticsService()

        self.repo = Repository()

    def run(self):
        """
        Returns:
            tuple[Portfolio, Report | None, list]
        """

        if not self.repo.health_check():
            log.error(
                "Health check",
                "Supabase connection failed",
            )
            raise RuntimeError("Supabase connection failed")

        # =====================================================
        # Portfolio
        # =====================================================

        portfolio = self.portfolio_service.build()

        log.success(
            "Portfolio",
            f"{len(portfolio.positions)} positions (€{portfolio.total_value:,.0f})",
        )

        self.repo.save_snapshot(portfolio)
        self.repo.save_positions(portfolio)

        # =====================================================
        # Research
        # =====================================================

        context = self.research_service.build(portfolio)

        self.repo.save_news(context.news)
        self.repo.save_earnings(context.earnings)
        self.repo.save_macro(context.macro)

        log.success(
            "Research",
            f"{len(context.news)} news · {len(context.earnings)} earnings · marco",
        )

        # =====================================================
        # Portfolio Analytics
        # =====================================================

        # CashFlows
        cashflows = self.trading212.transactions()

        self.repo.save_cashflows(cashflows)

        # History
        history = self.repo.history(365)

        cashflows = self.repo.cashflows(365)

        analytics = self.analytics_service.calculate(
            portfolio=portfolio,
            history=history,
            cashflows=cashflows,
        )

        # =====================================================
        # AI Analysis
        # =====================================================

        history = self.repo.history(30)

        report = self.analyst_service.analyze(
            context=context,
            history=history,
        )

        if report:

            self.repo.save_report(report)

            log.success(
                "Gemini",
                report.portfolio_rating.overall_sentiment,
            )

        else:

            log.warning(
                "Gemini",
                "No report generated",
            )

        # =====================================================
        # Done
        # =====================================================

        return portfolio, report, history
