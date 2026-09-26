from app.domain.position import Position
from app.repository import Repository
from app.services.ai_analysis_service import AIAnalysisService
from app.services.portfolio_service import PortfolioService
from app.services.research_service import ResearchService
from app.telegram.formatter import Formatter

portfolio_service = PortfolioService()
research_service = ResearchService()
analyst_service = AIAnalysisService()
repo = Repository()


def load_portfolio():
    """Load the current portfolio from Trading212."""
    return portfolio_service.build()


# =====================================================
# /daily
# =====================================================

def daily():
    ptf = load_portfolio()

    context = research_service.build(ptf)

    hty = repo.history(30)

    report = analyst_service.analyze(
        context=context,
        history=hty,
    )

    return Formatter.daily(
        ptf,
        report,
    )


# =====================================================
# /portfolio
# =====================================================

def portfolio():
    return Formatter.portfolio(
        load_portfolio()
    )


# =====================================================
# /history NVDA
# =====================================================

def history(message: str):
    parts = message.split()

    if len(parts) < 2:
        return "Usage: `/history NVDA`"

    ticker = parts[1].upper()

    data = repo.position_history(
        f"{ticker}_US_EQ"
    )

    return Formatter.history(
        ticker,
        data,
    )


# =====================================================
# /risk
# =====================================================

def risk():
    return Formatter.risk(
        load_portfolio()
    )


# =====================================================
# /stock NVDA
# =====================================================

def analyze_stock(ticker: str):
    ticker = ticker.upper()

    full_ticker = f"{ticker}_US_EQ"

    ptf = load_portfolio()

    position: Position | None = ptf.get_position(
        full_ticker
    )

    if position is None:
        return f"❌ *{ticker}* is not in your portfolio."

    context = research_service.build(
        portfolio=ptf,
        tickers=[ticker],
    )

    hty = repo.position_history(full_ticker)

    report = analyst_service.analyze(
        context=context,
        history=hty,
    )

    if report is None:
        return f"⚠️ AI analysis unavailable for *{ticker}*."

    return Formatter.stock_analysis(
        position=position,
        report=report,
        history=hty,
    )
