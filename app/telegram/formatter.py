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
            f"Trading212  {icon.get(s.trading212,'➖')}",
            f"Finnhub     {icon.get(s.finnhub,'➖')}",
            f"FRED        {icon.get(s.fred,'➖')}",
            f"Gemini      {icon.get(s.gemini,'➖')}",
        ])

    # =====================================================
    # Daily
    # =====================================================

    @staticmethod
    def daily(portfolio: Portfolio, report: Report | None):

        if report is None:

            return "\n".join([
                "🕐 *Daily Portfolio Report*",
                "",
                f"💰 Portfolio: €{portfolio.total_value:,.0f}",
                f"💵 Cash: {portfolio.cash_ratio:.1f}%",
                "",
                "⚠️ *AI analysis is temporarily unavailable.*",
                "Market data updated successfully.",
            ])

        p = report.portfolio_rating

        emoji = {
            "Positive": "🟢",
            "Neutral": "🟡",
            "Negative": "🔴",
        }[p.overall_sentiment]

        lines = [
            "📊 *AI Daily Brief*",
            "",
            f"💰 Portfolio: €{portfolio.total_value:,.0f}",
            f"💵 Cash: {portfolio.cash_ratio:.1f}%",
            "",
            f"📈 Sentiment: {emoji} *{p.overall_sentiment}*",
            "",
            p.summary,
        ]

        if report.positions_ratings:

            lines += ["", "🧠 *Top Ideas*"]

            for stock in report.positions_ratings[:5]:

                e = {
                    "Buy": "🟢",
                    "Hold": "🟡",
                    "Reduce": "🔴",
                    "Sell": "🔴",
                }[stock.rating]

                ticker = stock.ticker.replace("_US_EQ", "")

                lines.append(
                    f"{e} *{ticker}* — {stock.rating}"
                )

        lines.append(Formatter.data_sources(report))

        return "\n".join(lines)

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
                f"{i}. *{p.ticker.replace('_US_EQ','')}* `{p.weight:.1f}%`"
            )

            text.append(
                f"   {emoji} {p.quantity:.2f} sh | {p.return_pct:+.1f}%"
            )

        return "\n".join(text)

    # =====================================================
    # Risk
    # =====================================================

    @staticmethod
    def risk(portfolio: Portfolio):

        concentration = portfolio.concentration

        risk = concentration["risk"]

        emoji = {
            "Low": "🟢",
            "Medium": "🟡",
            "High": "🔴",
        }[risk]

        cash = portfolio.cash_ratio

        if cash < 5:
            cash_text = "Very Low"
        elif cash < 15:
            cash_text = "Healthy"
        else:
            cash_text = "Defensive"

        lines = [
            "*⚠️ Portfolio Risk Report*",
            "",
            f"Overall Risk : {emoji} *{risk}*",
            "",
            "*Concentration*",
            f"• Top 5 Holdings : *{concentration['top5_weight']:.1f}%*",
            "",
            "*Liquidity*",
            f"• Cash Ratio : *{cash:.1f}%* ({cash_text})",
            "",
            "*Largest Positions*",
        ]

        for p in portfolio.top_positions[:5]:

            lines.append(
                f"• {p.ticker.replace('_US_EQ','')} — {p.weight:.1f}%"
            )

        return "\n".join(lines)

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
                f"• {p.ticker.replace('_US_EQ','')}  {p.weight:.1f}%"
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