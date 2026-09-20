from app.schema import Report

class Formatter:

    @staticmethod
    def daily(portfolio, report):

        if report is None:
            return (
                "📊 *Daily Portfolio Report*\n\n"
                f"Portfolio: €{portfolio.total_value:,.0f}\n"
                f"Cash: {portfolio.cash_ratio:.1f}%\n\n"
                "⚠️ AI analysis is temporarily unavailable.\n"
                "Market data and portfolio history were updated successfully."
            )

        p = report.portfolio_rating

        emoji = {
            "Positive": "🟢",
            "Neutral": "🟡",
            "Negative": "🔴"
        }[p.overall_sentiment]

        lines = [
            "*📊 AI Daily Brief*",
            "",
            f"Portfolio: €{portfolio.total_value:,.0f}",
            f"Cash: {portfolio.cash_ratio:.1f}%",
            "",
            f"Sentiment: {emoji} *{p.overall_sentiment}*",
            "",
            p.summary,
            "",
            "*Top Ideas*"
        ]

        for stock in report.positions_ratings[:5]:
            e = {
                "Buy": "🟢",
                "Hold": "🟡",
                "Reduce": "🔴",
                "Sell": "🔴"
            }[stock.rating]

            lines.append(
                f"{e} *{stock.ticker.replace('_US_EQ', '')}* — {stock.rating}"
            )

        return "\n".join(lines)

    @staticmethod
    def history(ticker: str, history: list[dict]) -> str:
        """
        history:
        [
            {
                "snapshot_date": "2026-09-10",
                "quantity": 22,
                "weight": 18.6,
                "market_value": 15720
            },
            ...
        ]
        """

        if not history:
            return f"*{ticker}*\n\nNo historical data available."

        lines = [
            f"*📈 {ticker} · Position History*",
            ""
        ]

        first = history[0]["weight"]
        last = history[-1]["weight"]

        if last > first:
            trend = "Increasing 📈"
        elif last < first:
            trend = "Decreasing 📉"
        else:
            trend = "Stable ➖"

        for row in history:
            date = row["snapshot_date"][5:]  # MM-DD
            qty = row["quantity"]
            weight = row["weight"]

            lines.append(
                f"`{date}`  {qty:.0f} sh   {weight:.1f}%"
            )

        lines.extend([
            "",
            f"*Trend:* {trend}",
            f"*Current Weight:* {last:.1f}%"
        ])

        return "\n".join(lines)

    @staticmethod
    def risk(portfolio):

        concentration = portfolio.concentration()

        cash = portfolio.cash_ratio
        top5 = concentration["top5_weight"]
        risk_level = concentration["risk"]

        # Emoji
        if risk_level == "Low":
            emoji = "🟢"
        elif risk_level == "Medium":
            emoji = "🟡"
        else:
            emoji = "🔴"

        # Cash interpretation
        if cash < 5:
            cash_text = "Very Low"
        elif cash < 15:
            cash_text = "Healthy"
        else:
            cash_text = "Defensive"

        lines = [
            "*⚠️ Portfolio Risk Report*",
            "",
            f"Overall Risk : {emoji} *{risk_level}*",
            "",
            "*Concentration*",
            f"• Top 5 Holdings : *{top5:.1f}%*",
            "",
            "*Liquidity*",
            f"• Cash Ratio : *{cash:.1f}%* ({cash_text})",
            "",
            "*Largest Positions*"
        ]

        for pos in portfolio.top_positions()[:5]:
            lines.append(
                f"• {pos['ticker']} — {pos['weight']:.1f}%"
            )

        return "\n".join(lines)

    @staticmethod
    def stock_analysis(position, report: Report, history):

        portfolio_view = report.portfolio_rating
        stock = report.positions_ratings[0]

        emoji = {
            "Buy": "🟢",
            "Hold": "🟡",
            "Reduce": "🔴",
            "Sell": "🔴",
        }.get(stock.rating, "⚪")

        current = position["current_price"]
        avg = position["avg_price"]

        pnl_pct = (
            position["pnl"] / position["cost"] * 100
            if position["cost"] else 0
        )

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
            f"*📈 {stock.name}*",
            f"`{stock.ticker}`",
            "",
            f"*AI Rating:* {emoji} *{stock.rating}*",
            f"*Sentiment:* {portfolio_view.overall_sentiment}",
            "",
            "*Current Position*",
            f"• Weight: {position['weight']:.1f}%",
            f"• Shares: {position['quantity']:.2f}",
            f"• Avg Cost: €{avg:.2f}",
            f"• Current Price: €{current:.2f}",
            f"• Unrealized: {pnl_pct:+.2f}%",
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

    @staticmethod
    def portfolio(portfolio):

        positions = portfolio.top_positions()

        text = [
            "📊 *Current Portfolio*",
            "",
            f"**Total Value:** {portfolio.currency} {portfolio.total_value:,.2f}",
            f"**Available Cash:** {portfolio.currency} {portfolio.cash_available_to_trade:,.2f}",
            f"**Cash Ratio:** {portfolio.cash_ratio:.1f}%",
            f"**Unrealized P/L:** {portfolio.currency} {portfolio.unrealized_pnl:,.2f}",
            f"**Return:** {portfolio.return_pct:+.2f}%",
            "",
            "*Top Holdings*"
        ]

        for i, p in enumerate(positions[:10], start=1):
            rtn = (
                p["pnl"] / p["cost"] * 100
                if p["cost"] else 0
            )

            emoji = "🟢" if rtn >= 0 else "🔴"

            text.append(
                f"{i}. *{p['ticker'].replace('_US_EQ', '')}* "
                f"`{p['weight']:.1f}%`"
            )
            text.append(
                f"   {emoji} {p['quantity']:.2f} sh | {rtn:+.1f}%"
            )

        return "\n".join(text)

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

    @staticmethod
    def market_close(portfolio, report, history):

        today = history[-1] if history else None
        yesterday = history[-2] if len(history) >= 2 else None

        daily_change = 0.0
        daily_pct = 0.0

        if today and yesterday:
            daily_change = today["total_value"] - yesterday["total_value"]
            daily_pct = daily_change / yesterday["total_value"] * 100

        emoji = "🟢" if daily_change >= 0 else "🔴"

        lines = [
            "🌙 *Market Close Report*",
            "",
            f"**Portfolio Value:** €{portfolio.total_value:,.2f}",
            f"**Today's Change:** {emoji} €{daily_change:+,.2f} ({daily_pct:+.2f}%)",
            f"**Cash:** {portfolio.cash_ratio:.1f}%",
            "",
            "*Top Holdings*"
        ]

        for p in portfolio.top_positions()[:5]:
            lines.append(
                f"• {p['ticker'].replace('_US_EQ', '')}  {p['weight']:.1f}%"
            )

        if report is not None:
            lines.extend([
                "",
                "*AI Closing View*",
                report.portfolio_rating.summary
            ])

        return "\n".join(lines)