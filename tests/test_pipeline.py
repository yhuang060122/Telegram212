from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.domain.macro import MacroData
from app.domain.research import ResearchContext
from app.pipeline import DailyPipeline


class TestDailyPipeline:
    @pytest.fixture
    def pipeline(self, portfolio, history, cashflows, monkeypatch):
        # Tests must not send real Telegram messages.
        monkeypatch.setattr(
            "app.pipeline.log.flush",
            lambda *args, **kwargs: None,
        )

        pipeline = DailyPipeline()

        # -------------------------------------------------
        # Repository
        # -------------------------------------------------
        repo = Mock()

        # The pipeline requests both 365-day and 30-day history.
        repo.history.side_effect = [history, history]
        repo.cashflows.return_value = cashflows

        pipeline.repo = repo

        # -------------------------------------------------
        # Portfolio Service
        # -------------------------------------------------
        portfolio_service = Mock()
        portfolio_service.build.return_value = portfolio

        pipeline.portfolio_service = portfolio_service

        # -------------------------------------------------
        # Research Service
        # -------------------------------------------------
        research = ResearchContext(
            portfolio=portfolio,
            news=[],
            earnings=[],
            macro=MacroData(),
            status={},
        )

        research_service = Mock()
        research_service.build.return_value = research

        pipeline.research_service = research_service

        # -------------------------------------------------
        # Validation Service
        # -------------------------------------------------
        validation_result = SimpleNamespace(
            valid=True,
            issues=[],
            cleaned=history,
        )

        validation_service = Mock()
        validation_service.validate_history.return_value = validation_result

        pipeline.validation_service = validation_service

        # -------------------------------------------------
        # Analytics Service
        # -------------------------------------------------
        analytics = SimpleNamespace(
            performance=SimpleNamespace(
                daily_return=1.5,
                weekly_return=2.3,
                monthly_return=8.2,
                total_return=9.0,
                twr=8.7,
                xirr=10.1,
            ),
            risk=SimpleNamespace(
                drawdown=-4.5,
                max_drawdown=-12.3,
                volatility=18.1,
                sharpe=1.21,
                concentration=SimpleNamespace(
                    top1=40.0,
                    top3=100.0,
                    top5=100.0,
                    herfindahl=0.345,
                    risk_level="High",
                ),
            ),
            sector_allocation=[],
            position_allocation=[],
        )

        analytics_service = Mock()
        analytics_service.calculate.return_value = analytics

        pipeline.analytics_service = analytics_service

        # -------------------------------------------------
        # AI Service
        # -------------------------------------------------
        report = SimpleNamespace(
            portfolio_rating=SimpleNamespace(
                overall_sentiment="Positive",
                summary="Healthy portfolio.",
                cash_strategy="Maintain adequate cash reserves.",
                macro_outlook="Neutral",
            ),
            positions_ratings=[],
            data_status=SimpleNamespace(
                trading212="ok",
                finnhub="ok",
                fred="ok",
                gemini="ok",
            ),
        )

        ai_service = Mock()
        ai_service.analyze.return_value = report

        pipeline.ai_service = ai_service

        return pipeline

    # -------------------------------------------------
    # Success
    # -------------------------------------------------
    def test_pipeline_success(self, pipeline):
        portfolio, analytics, report, history = pipeline.run()

        assert portfolio is not None
        assert analytics is not None
        assert report is not None
        assert history is not None

        pipeline.portfolio_service.build.assert_called_once()
        pipeline.research_service.build.assert_called_once()

        pipeline.validation_service.validate_history.assert_called_once()

        pipeline.analytics_service.calculate.assert_called_once()
        pipeline.ai_service.analyze.assert_called_once()

        pipeline.repo.save_snapshot.assert_called_once()
        pipeline.repo.save_positions.assert_called_once()
        pipeline.repo.save_news.assert_called_once()
        pipeline.repo.save_earnings.assert_called_once()
        pipeline.repo.save_macro.assert_called_once()
        pipeline.repo.save_report.assert_called_once()

    # -------------------------------------------------
    # AI Failure
    # -------------------------------------------------
    def test_ai_failure(self, pipeline):
        pipeline.ai_service.analyze.return_value = None

        _, _, report, _ = pipeline.run()

        assert report is None
        pipeline.repo.save_report.assert_not_called()

    # -------------------------------------------------
    # Validation Failure
    # -------------------------------------------------
    def test_validation_failure(self, pipeline):
        invalid = SimpleNamespace(
            valid=False,
            issues=["INVALID_HISTORY"],
            cleaned=[],
        )

        pipeline.validation_service.validate_history.return_value = invalid

        with pytest.raises(ValueError):
            pipeline.run()

        pipeline.analytics_service.calculate.assert_not_called()
        pipeline.ai_service.analyze.assert_not_called()
        pipeline.repo.save_report.assert_not_called()

    # -------------------------------------------------
    # Repository Calls
    # -------------------------------------------------
    def test_repository_methods_called(self, pipeline):
        pipeline.run()

        pipeline.repo.save_snapshot.assert_called_once()
        pipeline.repo.save_positions.assert_called_once()

        pipeline.repo.save_news.assert_called_once()
        pipeline.repo.save_earnings.assert_called_once()
        pipeline.repo.save_macro.assert_called_once()

        pipeline.repo.history.assert_any_call(365)
        pipeline.repo.history.assert_any_call(30)
        assert pipeline.repo.history.call_count == 2

        pipeline.repo.cashflows.assert_called_once_with(365)

    # -------------------------------------------------
    # Analytics Input
    # -------------------------------------------------
    def test_analytics_receives_correct_objects(
        self,
        pipeline,
        portfolio,
        history,
        cashflows,
    ):
        pipeline.run()

        pipeline.analytics_service.calculate.assert_called_once_with(
            portfolio=portfolio,
            history=history,
            cashflows=cashflows,
        )

    # -------------------------------------------------
    # AI Input
    # -------------------------------------------------
    def test_ai_receives_context(self, pipeline):
        pipeline.run()

        pipeline.ai_service.analyze.assert_called_once()

        _, kwargs = pipeline.ai_service.analyze.call_args

        assert isinstance(kwargs["context"], ResearchContext)

    # -------------------------------------------------
    # History Output
    # -------------------------------------------------
    def test_history_returned(self, pipeline, history):
        _, _, _, result = pipeline.run()

        assert result == history
