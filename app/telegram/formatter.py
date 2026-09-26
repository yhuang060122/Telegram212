from app.domain.portfolio import Portfolio
from app.domain.position import Position
from app.domain.report import Report


class Formatter:

    # =====================================================
    # Shared
    # =====================================================

    @staticmethod
    def data_sources(report: Report) -> str:

        icon = {
            "ok": "✅",
            "failed": "❌",
            "partial": "⚠️",
            "unknown": "➖",
        }

        s = report.data_status

        return "\n".join([
            "",
            "📡 *Data Sources*",
            f"Trading212  {icon.get(s.trading212, '➖')}",
            f"Finnhub     {icon.get(s.finnhub, '➖')}",
            f"FRED        {icon.get(s.fred, '➖')}",
            f"Gemini      {icon.get(s.gemini, '➖')}",
        ])

    @staticmethod
    def pct(value: float | None) -> str:
        """Format percentage, displaying N/A when unavailable."""
        if value is None:
            return "N/A"

        return f"{value:+.2f}%"

    # =====================================================
    # Daily
    # =====================================================
    @staticmethod
    def daily(portfolio, analytics, report):

        c = analytics.risk.concentration
        p = analytics.performance
        r = analytics.risk

        return f"""
            📊 *Daily Portfolio Report*
        
            💼 Value: €{portfolio.total_value:,.0f}
            💰 Cash: {portfolio.cash_ratio:.1f}%
        
            ━━━━━━━━━━
        
            📈 *Performance*
        
            Today: {Formatter.pct(p.daily_return)}
            Week : {Formatter.pct(p.weekly_return)}
            Month: {Formatter.pct(p.monthly_return)}
        
            TWR  : {Formatter.pct(p.twr)}
            XIRR : {Formatter.pct(p.xirr)}
        
            ━━━━━━━━━━
        
            ⚠️ *Risk*
        
            Drawdown : {Formatter.pct(r.drawdown)}
            Max DD   : {Formatter.pct(r.max_drawdown)}
        
            Volatility: {Formatter.pct(r.volatility)}
            Sharpe    : {"N/A" if r.sharpe is None else f"{r.sharpe:.2f}"}
        
            ━━━━━━━━━━
        
            🏦 *Allocation*
        
            Top 5 : {c.top5:.1f}%
            HHI   : {c.herfindahl:.3f}
            Risk  : {c.risk_level}
        
            ━━━━━━━━━━
        
            🤖 *AI Summary*
        
            {report.portfolio_rating.summary if report else "Unavailable"}
            """.strip()

    # =====================================================
    # Portfolio
    # =====================================================

    @staticmethod
    def portfolio(portfolio: Portfolio):

        text = [
            "📊 *Current Portfolio*",
            "",
            f"**Total Value:** {portfolio.currency} {portfolio.total_value:,.2f}",
            f"**Available Cash:** {portfolio.currency} {portfolio.cash_available:,.2f}",
            f"**Cash Ratio:** {portfolio.cash_ratio:.1f}%",
            f"**Unrealized P/L:** {portfolio.currency} {portfolio.unrealized_pnl:,.2f}",
            f"**Return:** {portfolio.return_pct:+.2f}%",
            "",
            "*Top Holdings*",
        ]

        for i, p in enumerate(portfolio.top_positions[:10], start=1):
            emoji = "🟢" if p.return_pct >= 0 else "🔴"

            text.append(
                f"{i}. *{p.ticker.replace('_US_EQ', '')}* `{p.weight:.1f}%`"
            )

            text.append(
                f"   {emoji} {p.quantity:.2f} sh | {p.return_pct:+.1f}%"
            )

        return "\n".join(text)

    # =====================================================
    # Risk
    # =====================================================

    @staticmethod
    def risk(analytics):

        c = analytics.risk.concentration

        return f"""
            ⚠️ *Portfolio Risk*
        
            Current DD
            {analytics.risk.drawdown:.2f}%
        
            Max DD
            {analytics.risk.max_drawdown:.2f}%
        
            Volatility
            {analytics.risk.volatility:.2f}%
        
            Sharpe
            {analytics.risk.sharpe:.2f}
        
            ━━━━━━━━━━
        
            Top1  {c.top1:.1f}%
            Top3  {c.top3:.1f}%
            Top5  {c.top5:.1f}%
        
            HHI   {c.herfindahl:.3f}
            Risk  {c.risk_level}
            """.strip()

    # =====================================================
    # Stock Analysis
    # =====================================================

    @staticmethod
    def stock_analysis(
            position: Position,
            report: Report,
            history: list[dict],
    ):

        portfolio_view = report.portfolio_rating

        stock = report.positions_ratings[0]

        emoji = {
            "Buy": "🟢",
            "Hold": "🟡",
            "Reduce": "🔴",
            "Sell": "🔴",
        }[stock.rating]

        trend = "N/A"

        if len(history) >= 2:

            first = history[0]["weight"]
            last = history[-1]["weight"]

            if last > first:
                trend = "Increasing 📈"
            elif last < first:
                trend = "Decreasing 📉"
            else:
                trend = "Stable ➖"

        lines = [
            f"*📈 {position.name}*",
            f"`{position.ticker}`",
            "",
            f"*AI Rating:* {emoji} *{stock.rating}*",
            f"*Sentiment:* {portfolio_view.overall_sentiment}",
            "",
            "*Current Position*",
            f"• Weight: {position.weight:.1f}%",
            f"• Shares: {position.quantity:.2f}",
            f"• Avg Cost: €{position.avg_price:.2f}",
            f"• Current Price: €{position.current_price:.2f}",
            f"• Unrealized: {position.return_pct:+.2f}%",
            "",
            "*30-Day Trend*",
            f"• {trend}",
            "",
            "*Portfolio View*",
            portfolio_view.summary,
            "",
            "*Cash Strategy*",
            portfolio_view.cash_strategy,
            "",
            "*Macro Outlook*",
            portfolio_view.macro_outlook,
            "",
            "*Investment Rationale*",
            stock.rationale,
        ]

        return "\n\n".join(lines)

    # =====================================================
    # History
    # =====================================================

    @staticmethod
    def history(ticker: str, history: list[dict]):

        if not history:
            return f"*{ticker}*\n\nNo historical data available."

        first = history[0]["weight"]
        last = history[-1]["weight"]

        if last > first:
            trend = "Increasing 📈"
        elif last < first:
            trend = "Decreasing 📉"
        else:
            trend = "Stable ➖"

        lines = [
            f"*📈 {ticker} · Position History*",
            "",
        ]

        for row in history:
            lines.append(
                f"`{row['snapshot_date'][5:]}`  {row['quantity']:.0f} sh   {row['weight']:.1f}%"
            )

        lines += [
            "",
            f"*Trend:* {trend}",
            f"*Current Weight:* {last:.1f}%",
        ]

        return "\n".join(lines)

    # =====================================================
    # Market Close
    # =====================================================

    @staticmethod
    def market_close(
            portfolio: Portfolio,
            report: Report | None,
            history: list[dict],
    ):

        today = history[-1] if history else None
        yesterday = history[-2] if len(history) >= 2 else None

        change = 0
        pct = 0

        if today and yesterday:
            change = (
                    today["total_value"]
                    - yesterday["total_value"]
            )

            pct = (
                    change
                    / yesterday["total_value"]
                    * 100
            )

        emoji = "🟢" if change >= 0 else "🔴"

        lines = [
            "🌙 *Market Close Report*",
            "",
            f"**Portfolio Value:** €{portfolio.total_value:,.2f}",
            f"**Today's Change:** {emoji} €{change:+,.2f} ({pct:+.2f}%)",
            f"**Cash:** {portfolio.cash_ratio:.1f}%",
            "",
            "*Top Holdings*",
        ]

        for p in portfolio.top_positions[:5]:
            lines.append(
                f"• {p.ticker.replace('_US_EQ', '')}  {p.weight:.1f}%"
            )

        if report:
            lines += [
                "",
                "*AI Closing View*",
                report.portfolio_rating.summary,
            ]

        return "\n".join(lines)

    # =====================================================
    # Help
    # =====================================================

    @staticmethod
    def help():

        return """
*Trading212 AI Bot*

/daily - AI Daily Report
/portfolio - Current holdings
/risk - Portfolio risk
/stock nvda - Analyze NVDA
/history NVDA - 30-day history
"""
