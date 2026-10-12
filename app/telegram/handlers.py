from app.domain.position import Position
from app.repository import Repository
from app.services.ai_analysis_service import AIAnalysisService
from app.services.analytics_service import AnalyticsService
from app.services.portfolio_service import PortfolioService
from app.services.research_service import ResearchService
from app.telegram.formatter import Formatter

portfolio_service = PortfolioService()
research_service = ResearchService()
analyst_service = AIAnalysisService()
analytics_service = AnalyticsService()
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

    history = repo.history(365)
    cashflows = repo.cashflows(365)

    analytics = analytics_service.calculate(
        ptf,
        history,
        cashflows,
    )

    report = analyst_service.analyze(
        context=context, history=history, analytics=analytics
    )

    return Formatter.daily(
        ptf,
        analytics,
        report,
    )


# =====================================================
# /portfolio
# =====================================================


def portfolio():
    return Formatter.portfolio(load_portfolio())


# =====================================================
# /history NVDA
# =====================================================


def history(message: str):
    parts = message.split()

    if len(parts) < 2:
        return "Usage: `/history NVDA`"

    ticker = parts[1].upper()

    data = repo.position_history(f"{ticker}_US_EQ")

    return Formatter.history(
        ticker,
        data,
    )


# =====================================================
# /risk
# =====================================================


def risk():
    ptf = load_portfolio()

    history = repo.history(365)
    cashflows = repo.cashflows(365)

    analytics = analytics_service.calculate(
        ptf,
        history,
        cashflows,
    )

    return Formatter.risk(analytics)


# =====================================================
# /performance
# =====================================================
def performance(analytics):
    p = analytics.performance

    return f"""
        📈 *Performance Metrics*
        
        Daily
        {p.daily_return:+.2f}%
        
        Weekly
        {p.weekly_return:+.2f}%
        
        Monthly
        {p.monthly_return:+.2f}%
        
        ━━━━━━━━━━
        
        Total Return
        {p.total_return:+.2f}%
        
        TWR
        {p.twr:+.2f}%
        
        XIRR
        {p.xirr:+.2f}%
        """.strip()


# =====================================================
# /stock NVDA
# =====================================================


def analyze_stock(ticker: str):
    ticker = ticker.upper()

    full_ticker = f"{ticker}_US_EQ"

    ptf = load_portfolio()

    position: Position | None = ptf.get_position(full_ticker)

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
        pos_history=hty,
    )
