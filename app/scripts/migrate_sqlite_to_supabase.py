from __future__ import annotations

import argparse
import os
import sqlite3
import uuid
from pathlib import Path
from typing import Iterable

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

BATCH_SIZE = 500

# ============================================================
# Helpers
# ============================================================

def chunks(items: list[dict], size: int = BATCH_SIZE):
    for i in range(0, len(items), size):
        yield items[i:i + size]

def deterministic_uuid(*parts: str) -> str:
    """
    Generate the same UUID for the same data.
    This makes news/earnings migration idempotent.
    """
    value = "|".join(str(p) for p in parts)
    return str(uuid.uuid5(uuid.NAMESPACE_URL, value))

def get_supabase() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")

    if not url:
        raise RuntimeError("Missing SUPABASE_URL")

    if not key:
        raise RuntimeError("Missing SUPABASE_SERVICE_KEY")

    return create_client(url, key)

def get_sqlite(path: str) -> sqlite3.Connection:

    if not Path(path).exists():
        raise FileNotFoundError(
            f"SQLite database not found: {path}"
        )

    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row

    return conn


# ============================================================
# SQLite
# ============================================================

def read_rows(
    conn: sqlite3.Connection,
    table: str,
) -> list[dict]:

    rows = conn.execute(
        f"SELECT * FROM {table}"
    ).fetchall()

    return [dict(row) for row in rows]


# ============================================================
# Snapshots
# ============================================================

def migrate_snapshots(
    supabase: Client,
    conn: sqlite3.Connection,
) -> int:

    rows = read_rows(conn, "snapshots")

    if not rows:
        return 0

    print(f"Snapshots: {len(rows)}")

    for batch in chunks(rows):

        supabase.table("snapshots").upsert(
            batch
        ).execute()

    return len(rows)


# ============================================================
# Positions
# ============================================================

def migrate_positions(
    supabase: Client,
    conn: sqlite3.Connection,
) -> int:

    rows = read_rows(conn, "positions")

    if not rows:
        return 0

    converted = []

    for row in rows:

        converted.append(
            {
                "snapshot_date": row["snapshot_date"],
                "ticker": row["ticker"],
                "name": row["name"],
                "quantity": row["quantity"],
                "avg_price": row["avg_price"],
                "current_price": row["current_price"],
                "market_value": row["market_value"],
                "cost": row["cost"],
                "pnl": row["pnl"],
                "weight": row["weight"],
                "return_pct": row["return_pct"],
                "sector": row["sector"],
                "fx_impact": row["fx_impact"],
                "inst_currency": row["inst_currency"],
            }
        )

    print(f"Positions: {len(converted)}")

    for batch in chunks(converted):

        supabase.table("positions").upsert(
            batch
        ).execute()

    return len(converted)


# ============================================================
# News
# ============================================================

def migrate_news(
    supabase: Client,
    conn: sqlite3.Connection,
) -> int:

    rows = read_rows(conn, "news")

    if not rows:
        return 0

    converted = []

    for row in rows:

        sentiment = row["sentiment"] or "Unknown"

        # Protect against unexpected historical values
        if sentiment not in {
            "Bullish",
            "Neutral",
            "Bearish",
            "Unknown",
        }:
            sentiment = "Unknown"

        news_id = deterministic_uuid(
            row["snapshot_date"],
            row["ticker"],
            row["title"],
            row["source"] or "",
            row["url"] or "",
        )

        converted.append(
            {
                "id": news_id,
                "snapshot_date": row["snapshot_date"],
                "ticker": row["ticker"],
                "title": row["title"],
                "source": row["source"],
                "sentiment": sentiment,
                "url": row["url"],
            }
        )

    print(f"News: {len(converted)}")

    for batch in chunks(converted):

        supabase.table("news").upsert(
            batch
        ).execute()

    return len(converted)


# ============================================================
# Earnings
# ============================================================

def migrate_earnings(
    supabase: Client,
    conn: sqlite3.Connection,
) -> int:

    rows = read_rows(conn, "earnings")

    if not rows:
        print("Earnings: 0")
        return 0

    converted = []

    for row in rows:

        earnings_id = deterministic_uuid(
            row["snapshot_date"],
            row["ticker"],
            row["earnings_date"],
            row["session"],
        )

        converted.append(
            {
                "id": earnings_id,
                "snapshot_date": row["snapshot_date"],
                "ticker": row["ticker"],
                "earnings_date": row["earnings_date"],
                "session": row["session"],
            }
        )

    print(f"Earnings: {len(converted)}")

    for batch in chunks(converted):

        supabase.table("earnings").upsert(
            batch
        ).execute()

    return len(converted)


# ============================================================
# Reports
# ============================================================

def migrate_reports(
    supabase: Client,
    conn: sqlite3.Connection,
) -> int:

    # Old database has no reports table.
    tables = conn.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        AND name='reports'
        """
    ).fetchone()

    if not tables:
        print("Reports: old SQLite database has no reports table")
        return 0

    rows = read_rows(conn, "reports")

    if not rows:
        print("Reports: 0")
        return 0

    converted = []

    for row in rows:

        converted.append(
            {
                "snapshot_date": row["snapshot_date"],
                "report": row["json"],
            }
        )

    for batch in chunks(converted):

        supabase.table("reports").upsert(
            batch
        ).execute()

    return len(converted)


# ============================================================
# Verification
# ============================================================

def count_supabase_rows(
    supabase: Client,
    table: str,
) -> int:

    response = (
        supabase.table(table)
        .select("*", count="exact")
        .limit(1)
        .execute()
    )

    return response.count or 0


def verify(supabase: Client):

    print()
    print("========== SUPABASE COUNTS ==========")

    for table in [
        "snapshots",
        "positions",
        "news",
        "earnings",
        "reports",
    ]:
        count = count_supabase_rows(
            supabase,
            table,
        )

        print(f"{table:12} {count}")


# ============================================================
# Main
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description="Migrate SQLite portfolio DB to Supabase"
    )

    parser.add_argument(
        "--sqlite",
        default="portfolio.db",
        help="Path to SQLite database",
    )

    args = parser.parse_args()

    print("====================================")
    print(" SQLite → Supabase Migration")
    print("====================================")
    print(f"SQLite: {args.sqlite}")
    print()

    conn = get_sqlite(args.sqlite)
    supabase = get_supabase()

    try:

        # IMPORTANT:
        # snapshots first because positions/reports
        # have foreign keys to snapshots.

        snapshots = migrate_snapshots(
            supabase,
            conn,
        )

        positions = migrate_positions(
            supabase,
            conn,
        )

        news = migrate_news(
            supabase,
            conn,
        )

        earnings = migrate_earnings(
            supabase,
            conn,
        )

        reports = migrate_reports(
            supabase,
            conn,
        )

        print()
        print("========== MIGRATION ==========")

        print(f"snapshots : {snapshots}")
        print(f"positions : {positions}")
        print(f"news      : {news}")
        print(f"earnings  : {earnings}")
        print(f"reports   : {reports}")

        verify(supabase)

        print()
        print("✅ Migration completed.")

    finally:
        conn.close()


if __name__ == "__main__":
    main()