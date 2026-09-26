import os

import pytest

from tests.fixtures.cashflows import create_cashflows
from tests.fixtures.history import create_history
from tests.fixtures.portfolio import create_portfolio

# ---------- Environment ----------

@pytest.fixture(scope="session", autouse=True)
def test_environment():
    os.environ["TRADING212_API_KEY"] = "test-key"
    os.environ["GEMINI_API_KEY"] = "test-key"
    os.environ["FINNHUB_API_KEY"] = "test-key"
    os.environ["FRED_API_KEY"] = "test-key"

    os.environ["SUPABASE_URL"] = "https://example.supabase.co"
    os.environ["SUPABASE_KEY"] = "test-key"

    yield


# ---------- Temporary Working Directory ----------

@pytest.fixture
def temp_dir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path


# ---------- Domain Fixtures ----------

@pytest.fixture
def portfolio():
    return create_portfolio()


@pytest.fixture
def history():
    return create_history(1, 1000)


@pytest.fixture
def cashflows():
    return create_cashflows()


# ---------- Mock Repository ----------

class FakeRepository:

    def __init__(self):
        self.saved = {}

    def save_snapshot(self, snapshot):
        self.saved["snapshot"] = snapshot

    def save_positions(self, positions):
        self.saved["positions"] = positions

    def save_news(self, news):
        self.saved["news"] = news

    def save_earnings(self, earnings):
        self.saved["earnings"] = earnings

    def save_macro(self, macro):
        self.saved["macro"] = macro

    def save_report(self, report):
        self.saved["report"] = report

    def history(self, days=30):
        return create_history()

    def cashflows(self):
        return create_cashflows()


@pytest.fixture
def fake_repo():
    return FakeRepository()
