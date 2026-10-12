from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

import app.services.ai_analysis_service as ai_module
from app.domain.report import Report
from app.services.ai_analysis_service import AIAnalysisService


@pytest.fixture
def service(monkeypatch):
    """Create the service without a real Gemini API client."""
    client = MagicMock()
    monkeypatch.setattr(
        ai_module.genai,
        "Client",
        lambda **kwargs: client,
    )
    monkeypatch.setattr(ai_module.time, "sleep", MagicMock())
    monkeypatch.setattr(ai_module.log, "info", MagicMock())
    monkeypatch.setattr(ai_module.log, "warning", MagicMock())
    monkeypatch.setattr(ai_module.log, "error", MagicMock())

    instance = AIAnalysisService()
    instance.client = client

    return instance


@pytest.fixture
def inputs():
    """Minimal objects supporting the model_dump calls in analyze()."""
    portfolio = MagicMock()
    portfolio.model_dump.return_value = {"total_value": 10000}

    analytics = MagicMock()
    analytics.model_dump.return_value = {"return": 5.0}

    news_item = MagicMock()
    news_item.model_dump.return_value = {"ticker": "AAPL"}

    earnings_event = MagicMock()
    earnings_event.model_dump.return_value = {"ticker": "NVDA"}

    macro = MagicMock()
    macro.model_dump.return_value = {"interest_rate": 4.0}

    context = SimpleNamespace(
        portfolio=portfolio,
        analytics=analytics,
        news=[news_item],
        earnings=[earnings_event],
        macro=macro,
    )

    snapshot = MagicMock()
    snapshot.model_dump.return_value = {"total_value": 10000}

    return context, [snapshot], analytics


def make_response(parsed):
    response = MagicMock()
    response.parsed = parsed
    return response


class TestAIAnalysisService:
    def test_returns_report_on_first_model_success(self, service, inputs):
        context, history, analytics = inputs
        report = MagicMock(spec=Report)

        chat = service.client.chats.create.return_value
        chat.send_message.return_value = make_response(report)

        result = service.analyze(context, history, analytics)

        assert result is report
        service.client.chats.create.assert_called_once()
        chat.send_message.assert_called_once()

        args, _ = chat.send_message.call_args
        assert "total_value" in args[0]
        assert "AAPL" in args[0]

        ai_module.log.info.assert_any_call(
            "Analyze",
            f"Trying model: {service.MODELS[0]}",
        )
        ai_module.log.info.assert_any_call(
            "Analyze",
            f"Model {service.MODELS[0]} succeeded",
        )

    def test_retries_next_model_when_parsed_response_is_none(self, service, inputs):
        context, history, analytics = inputs
        report = MagicMock(spec=Report)

        chat = service.client.chats.create.return_value
        chat.send_message.side_effect = [
            make_response(None),
            make_response(report),
        ]

        result = service.analyze(context, history, analytics)

        assert result is report
        assert service.client.chats.create.call_count == 2
        assert chat.send_message.call_count == 2

        ai_module.log.warning.assert_called_once()
        ai_module.time.sleep.assert_not_called()

    def test_retries_after_model_exception(self, service, inputs):
        context, history, analytics = inputs
        report = MagicMock(spec=Report)

        chat = service.client.chats.create.return_value
        chat.send_message.side_effect = [
            RuntimeError("Gemini unavailable"),
            make_response(report),
        ]

        result = service.analyze(context, history, analytics)

        assert result is report
        assert service.client.chats.create.call_count == 2
        ai_module.time.sleep.assert_called_once_with(2)

    def test_returns_none_when_all_models_return_empty_response(self, service, inputs):
        context, history, analytics = inputs
        chat = service.client.chats.create.return_value
        chat.send_message.return_value = make_response(None)

        result = service.analyze(context, history, analytics)

        assert result is None
        assert service.client.chats.create.call_count == len(service.MODELS)
        assert chat.send_message.call_count == len(service.MODELS)

        ai_module.log.error.assert_called_once_with(
            "Analyze",
            "All Gemini models failed.",
        )

    def test_returns_none_when_all_models_raise_exception(self, service, inputs):
        context, history, analytics = inputs
        chat = service.client.chats.create.return_value
        chat.send_message.side_effect = RuntimeError("API error")

        result = service.analyze(context, history, analytics)

        assert result is None
        assert service.client.chats.create.call_count == len(service.MODELS)
        assert ai_module.time.sleep.call_count == len(service.MODELS)
        assert ai_module.log.error.called

    def test_uses_json_response_configuration(self, service, inputs):
        context, history, analytics = inputs
        report = MagicMock(spec=Report)

        chat = service.client.chats.create.return_value
        chat.send_message.return_value = make_response(report)

        service.analyze(context, history, analytics)

        kwargs = service.client.chats.create.call_args.kwargs
        config = kwargs["config"]

        assert kwargs["model"] == service.MODELS[0]
        assert config.response_mime_type == "application/json"
        assert config.response_schema is Report
        assert config.temperature == 0.2

    def test_model_creation_exception_retries(self, service, inputs):
        context, history, analytics = inputs
        report = MagicMock(spec=Report)
        chat = MagicMock()
        chat.send_message.return_value = make_response(report)

        service.client.chats.create.side_effect = [
            RuntimeError("Model creation failed"),
            chat,
        ]

        result = service.analyze(context, history, analytics)

        assert result is report
        assert service.client.chats.create.call_count == 2
        ai_module.time.sleep.assert_called_once_with(2)
