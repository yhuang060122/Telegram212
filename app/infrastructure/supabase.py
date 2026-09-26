import os
from collections import defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal

from dotenv import load_dotenv
from supabase import Client, create_client

from app.domain.cashflow import CashFlow, CashFlowType
from app.domain.earnings import EarningsEvent
from app.domain.macro import MacroData
from app.domain.news import NewsItem
from app.domain.portfolio import Portfolio
from app.domain.position import Position
from app.domain.report import Report

load_dotenv()


class SupabaseClient:

    def __init__(self):

        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY")

        if not url or not key:
            raise ValueError("SUPABASE_URL or SUPABASE_SERVICE_KEY is missing.")

        self.db: Client = create_client(url, key)

    # ---------------------------------
    # Snapshot
    # ---------------------------------

    def save_snapshot(
            self,
            portfolio: Portfolio,
    ):

        self.db.table("snapshots").upsert(
            {
                "snapshot_date": date.today().isoformat(),
                "total_value": portfolio.total_value,
                "cash": portfolio.cash,
                "cash_ratio": portfolio.cash_ratio,
                "invested": portfolio.invested,
                "current_value": portfolio.current_value,
                "unrealized_pnl": portfolio.unrealized_pnl,
                "realized_pnl": portfolio.realized_pnl,
                "currency": portfolio.currency,
            }
        ).execute()

    # ---------------------------------
    # Positions
    # ---------------------------------

    def save_positions(
            self,
            portfolio: Portfolio,
    ):

        rows = []

        for p in portfolio.positions:
            rows.append(
                {
                    "snapshot_date": date.today().isoformat(),
                    "ticker": p.ticker,
                    "name": p.name,
                    "quantity": p.quantity,
                    "avg_price": p.avg_price,
                    "current_price": p.current_price,
                    "market_value": p.market_value,
                    "cost": p.cost,
                    "pnl": p.pnl,
                    "weight": p.weight,
                    "return_pct": p.return_pct,
                    "sector": p.sector,
                    "fx_impact": p.fx_impact,
                    "inst_currency": p.currency,
                }
            )

        self.db.table("positions").upsert(rows).execute()

    # ---------------------------------
    # News
    # ---------------------------------

    def save_news(
            self,
            news: list[NewsItem],
    ):

        if not news:
            return

        rows = [
            {
                "published_at": item.published_at.isoformat(),
                "ticker": item.ticker,
                "title": item.title,
                "summary": item.summary,
                "source": item.source,
                "url": str(item.url),
                "sentiment": item.sentiment,
            }
            for item in news
        ]

        self.db.table("news").upsert(rows, on_conflict="ticker,published_at,url").execute()

    # ---------------------------------
    # Earnings
    # ---------------------------------

    def save_earnings(
            self,
            earnings: list[EarningsEvent],
    ):

        if not earnings:
            return

        rows = [
            {
                "snapshot_date": date.today().isoformat(),
                "ticker": e.ticker,
                "company": e.company,
                "earnings_date": e.earnings_date.isoformat(),
                "session": e.session,
                "eps_estimate": e.eps_estimate,
                "revenue_estimate": e.revenue_estimate,
            }
            for e in earnings
        ]

        self.db.table("earnings").upsert(rows, on_conflict="ticker,earnings_date").execute()

    # ---------------------------------
    # Macro
    # ---------------------------------
    def save_macro(self, macro: MacroData):
        self.db.table("macro").upsert(
            {
                "snapshot_date": date.today().isoformat(),
                **macro.model_dump(mode="json"),
            }
        ).execute()

    # ---------------------------------
    # Report
    # ---------------------------------

    def save_report(
            self,
            report: Report,
    ):

        self.db.table("reports").upsert(
            {
                "snapshot_date": date.today().isoformat(),
                "report": report.model_dump(mode="json"),
                "overall_sentiment": (
                    report.portfolio_rating.overall_sentiment
                ),
            }
        ).execute()

    def save_cashflows(
            self,
            cashflows: list[CashFlow],
    ) -> None:

        if not cashflows:
            return

        rows = [
            {
                "reference": c.reference,
                "datetime": c.datetime.isoformat(),
                "amount": float(c.amount),
                "currency": c.currency,
                "type": c.type.value,
            }
            for c in cashflows
        ]

        self.db.table("cashflows").upsert(
            rows,
            on_conflict="reference",
        ).execute()

    # ---------------------------------
    # Read
    # ---------------------------------

    def latest_snapshot(self):

        return (
            self.db.table("snapshots")
            .select("*")
            .order("snapshot_date", desc=True)
            .limit(1)
            .execute()
            .data
        )

    def latest_positions(self) -> list[Position]:

        latest = (
            self.db.table("snapshots")
            .select("snapshot_date")
            .order("snapshot_date", desc=True)
            .limit(1)
            .execute()
            .data
        )

        if not latest:
            return []

        snapshot_date = latest[0]["snapshot_date"]

        rows = (
            self.db.table("positions")
            .select("*")
            .eq("snapshot_date", snapshot_date)
            .order("market_value", desc=True)
            .execute()
            .data
        )

        return [
            Position(
                ticker=row["ticker"],
                name=row["name"],
                quantity=row["quantity"],
                avg_price=row["avg_price"],
                current_price=row["current_price"],
                market_value=row["market_value"],
                cost=row["market_value"] - row["pnl"],
                pnl=row["pnl"],
                weight=row["weight"],
                fx_impact=0,
                currency=row["inst_currency"],
                sector=row["sector"] or "Unknown",
            )
            for row in rows
        ]

    def history(self, days: int = 30):

        return (
            self.db.table("snapshots")
            .select("*")
            .order("snapshot_date", desc=False)
            .limit(days)
            .execute()
            .data
        )

    def position_history(self, ticker: str):

        return (
            self.db.table("positions")
            .select("*")
            .eq("ticker", ticker)
            .order("snapshot_date")
            .execute()
            .data
        )

    def today_news(self) -> list[NewsItem]:

        rows = (
            self.db.table("news")
            .select("*")
            .eq("published_date", date.today().isoformat())
            .order("published_at", desc=True)
            .execute()
            .data
        )

        return [
            NewsItem(
                ticker=row["ticker"],
                title=row["title"],
                summary=row["summary"],
                source=row["source"],
                url=row["url"],
                published_at=row["published_at"],
                sentiment=row["sentiment"],
            )
            for row in rows
        ]

    def latest_report(self):

        data = (
            self.db.table("reports")
            .select("*")
            .order("snapshot_date", desc=True)
            .limit(1)
            .execute()
            .data
        )

        if not data:
            return None

        return Report.model_validate(data[0]["report"])

    def monthly_returns(self) -> list[dict]:

        rows = (
            self.db.table("snapshots")
            .select("snapshot_date,total_value")
            .order("snapshot_date")
            .execute()
            .data
        )

        if not rows:
            return []

        months = defaultdict(list)

        for row in rows:
            month = row["snapshot_date"][:7]
            months[month].append(row)

        result = []

        for month, values in sorted(months.items()):
            start = values[0]["total_value"]
            end = values[-1]["total_value"]

            pct = (
                (end - start) / start * 100
                if start
                else 0
            )

            result.append(
                {
                    "month": month,
                    "start": round(start, 2),
                    "end": round(end, 2),
                    "return_pct": round(pct, 2),
                }
            )

        return result

    def health_check(self) -> bool:

        try:
            self.db.table("snapshots").select(
                "snapshot_date"
            ).limit(1).execute()
            return True
        except Exception:
            return False

    def cashflows(
            self,
            days: int = 365,
    ) -> list[CashFlow]:

        since = (
                datetime.utcnow() - timedelta(days=days)
        ).isoformat()

        result = (
            self.db.table("cashflows")
            .select("*")
            .gte("datetime", since)
            .order("datetime")
            .execute()
        )

        return [
            CashFlow(
                reference=row["reference"],
                datetime=datetime.fromisoformat(row["datetime"]),
                amount=Decimal(str(row["amount"])),
                currency=row["currency"],
                type=CashFlowType(row["type"]),
            )
            for row in result.data
        ]

    def latest_cashflow_reference(self) -> str | None:
        """
        Return the newest Trading212 transaction reference stored locally.
        """

        result = (
            self.db.table("cashflows")
            .select("reference")
            .order("datetime", desc=True)
            .limit(1)
            .execute()
        )

        if not result.data:
            return None

        return result.data[0]["reference"]
