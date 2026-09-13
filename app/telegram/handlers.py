from app.trading212 import Trading212Client
from app.portfolio import Portfolio
from app.research import ResearchContext
from app.database import Database
from app.analyst import Analyst
from .formatter import Formatter


def load_portfolio():
    client = Trading212Client()

    summary = client.account_summary()
    positions = client.positions()

    portfolio = Portfolio(summary, positions)

    return portfolio

def daily():

    portfolio = load_portfolio()
    context = ResearchContext.build(portfolio)
    db = Database()

    history = db.get_history(30)

    report = Analyst().analyze(
        context,
        history
    )

    return Formatter.daily(
        portfolio,
        report
    )

def portfolio():

    portfolio = load_portfolio()

    return Formatter.portfolio(portfolio)

def history(self, message):

    db = Database()
    ticker = message.split()[1].upper()

    data = db.get_position_history(
        ticker + "_US_EQ"
    )

    return Formatter.history(
        ticker,
        data
    )


def risk():

    portfolio = load_portfolio()

    return Formatter.risk(portfolio)


def analyze_stock(ticker: str):

    ticker = ticker.upper()

    client = Trading212Client()
    db = Database()

    portfolio = Portfolio(
        client.account_summary(),
        client.positions()
    )

    # Trading212 使用 NVDA_US_EQ 这种格式
    full_ticker = f"{ticker}_US_EQ"

    # 检查是否持有
    position = next(
        (p for p in portfolio.top_positions() if p["ticker"] == full_ticker),
        None
    )

    if position is None:
        return f"❌ *{ticker}* is not in your portfolio."

    # 构建完整 Context
    context = ResearchContext.build(portfolio)

    # 只保留当前股票的数据（减少 Token）
    context["portfolio"]["positions"] = [
        p for p in context["portfolio"]["positions"]
        if p["ticker"] == full_ticker
    ]

    context["news"] = [
        n for n in context["news"]
        if n["ticker"] == ticker
    ]

    context["earnings"] = [
        e for e in context["earnings"]
        if e["ticker"] == ticker
    ]

    history = db.get_position_history(full_ticker)

    report = Analyst().analyze(
        context=context,
        history=history
    )

    return Formatter.stock_analysis(
        position=position,
        report=report,
        history=history
    )