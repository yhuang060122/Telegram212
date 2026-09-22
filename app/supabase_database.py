from __future__ import annotations

import os
from datetime import date, timedelta
from typing import Any

from supabase import Client, create_client

from app.schema import Report
from app.storage import Storage
from dotenv import load_dotenv

from app.collectors.news import NewsItem
from app.collectors.earnings import EarningsEvent

load_dotenv()

class SupabaseDatabase(Storage):
    """
    Supabase implementation of the storage layer.

    Tables:
        snapshots
        positions
        news
        earnings
        reports
    """

    VALID_SENTIMENT = {
        "Bullish",
        "Neutral",
        "Bearish",
        "Unknown",
    }

    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY")

        if not url or not key:
            raise ValueError(
                "SUPABASE_URL or SUPABASE_SERVICE_KEY is missing."
            )

        self.db: Client = create_client(url, key)

    # ==========================================================
    # SAVE
    # ==========================================================

    def save_snapshot(self, portfolio) -> None:

        row = {
            "snapshot_date": date.today().isoformat(),
            "total_value": portfolio.total_value,
            "cash": portfolio.cash_available_to_trade + portfolio.cash_reserved,
            "cash_ratio": portfolio.cash_ratio,
            "invested": portfolio.invested,
            "current_value": portfolio.current_value,
            "unrealized_pnl": portfolio.unrealized_pnl,
            "realized_pnl": portfolio.realized_pnl,
            "currency": portfolio.currency,
        }

        self.db.table("snapshots").upsert(row).execute()

    def save_positions(self, portfolio) -> None:

        rows = []

        for p in portfolio.top_positions():

            rows.append(
                {
                    "snapshot_date": date.today().isoformat(),
                    "ticker": p["ticker"],
                    "name": p["name"],
                    "quantity": p["quantity"],
                    "avg_price": p["avg_price"],
                    "current_price": p["current_price"],
                    "market_value": p["market_value"],
                    "cost": p["cost"],
                    "pnl": p["pnl"],
                    "weight": p["weight"],
                    "return_pct": p["return_pct"],
                    "sector": p.get("sector"),
                    "fx_impact": p.get("fx_impact"),
                    "inst_currency": p.get("currency"),
                }
            )

        if rows:
            self.db.table("positions").upsert(rows).execute()

    def save_news(self, news: list[NewsItem]) -> None:

        if not news:
            return

        rows = []

        for n in news:
            sentiment = n.sentiment or "Unknown"

            if sentiment not in self.VALID_SENTIMENT:
                sentiment = "Unknown"

            rows.append(
                {
                    "snapshot_date": date.today().isoformat(),
                    "ticker": n.ticker,
                    "title": n.title,
                    "source": n.source,
                    "sentiment": sentiment,
                    "url": n.url,
                }
            )

        self.db.table("news").insert(rows).execute()

    def save_earnings(self, earnings: list[EarningsEvent]) -> None:

        if not earnings:
            return

        rows = [
            {
                "snapshot_date": date.today().isoformat(),
                "ticker": e.ticker,
                "earnings_date": e.date,
                "session": e.session,
            }
            for e in earnings
        ]

        if rows:
            self.db.table("earnings").insert(rows).execute()

    def save_report(self, report: Report) -> None:

        self.db.table("reports").upsert(
            {
                "snapshot_date": date.today().isoformat(),
                "report": report.model_dump(mode="json"),
            }
        ).execute()

    # ==========================================================
    # READ
    # ==========================================================

    def latest_snapshot(self) -> dict[str, Any] | None:

        r = (
            self.db.table("snapshots")
            .select("*")
            .order("snapshot_date", desc=True)
            .limit(1)
            .execute()
        )

        return r.data[0] if r.data else None

    def latest_positions(self) -> list[dict]:

        snapshot = self.latest_snapshot()

        if snapshot is None:
            return []

        r = (
            self.db.table("positions")
            .select("*")
            .eq("snapshot_date", snapshot["snapshot_date"])
            .order("weight", desc=True)
            .execute()
        )

        return r.data

    def today_news(self) -> list[dict]:

        today = date.today().isoformat()

        r = (
            self.db.table("news")
            .select("*")
            .eq("snapshot_date", today)
            .order("ticker")
            .execute()
        )

        return r.data

    def latest_report(self) -> Report | None:

        r = (
            self.db.table("reports")
            .select("report")
            .order("snapshot_date", desc=True)
            .limit(1)
            .execute()
        )

        if not r.data:
            return None

        return Report.model_validate(r.data[0]["report"])

    def get_history(self, days: int = 30) -> list[dict]:

        since = (
            date.today() - timedelta(days=days)
        ).isoformat()

        r = (
            self.db.table("snapshots")
            .select("*")
            .gte("snapshot_date", since)
            .order("snapshot_date")
            .execute()
        )

        return r.data

    def get_position_history(self, ticker: str) -> list[dict]:

        r = (
            self.db.table("positions")
            .select("snapshot_date, quantity, weight, market_value")
            .eq("ticker", ticker)
            .order("snapshot_date")
            .execute()
        )

        return r.data

    def monthly_returns(self) -> list[dict]:

        history = self.get_history(3650)

        months: dict[str, dict] = {}

        for row in history:

            month = row["snapshot_date"][:7]
            value = float(row["total_value"])

            if month not in months:
                months[month] = {
                    "start": value,
                    "end": value,
                }
            else:
                months[month]["end"] = value

        results = []

        for month in sorted(months):

            start = months[month]["start"]
            end = months[month]["end"]

            pct = 0.0
            if start != 0:
                pct = round((end - start) / start * 100, 2)

            results.append(
                {
                    "month": month,
                    "return_pct": pct,
                }
            )

        return results

    # ==========================================================
    # UTILS
    # ==========================================================

    def delete_today_news(self) -> None:

        self.db.table("news").delete().eq(
            "snapshot_date",
            date.today().isoformat(),
        ).execute()

    def health_check(self) -> bool:

        try:
            self.db.table("snapshots").select(
                "snapshot_date"
            ).limit(1).execute()
            return True
        except Exception:
            return False