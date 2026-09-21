from pathlib import Path
import sqlite3
from .entities import Snapshot, PositionRecord
from datetime import date
from app.schema import Report

class Database:

    def __init__(self, db_path="data/portfolio.db"):

        self.path = Path(db_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row

        self.create_tables()

    def create_tables(self):
        self.conn.executescript("""

        CREATE TABLE IF NOT EXISTS snapshots(
            snapshot_date TEXT PRIMARY KEY,
            total_value REAL,
            cash REAL,
            cash_ratio REAL,
            invested REAL,
            current_value REAL,
            unrealized_pnl REAL,
            realized_pnl REAL,
            currency TEXT
        );

        CREATE TABLE IF NOT EXISTS positions(
            snapshot_date TEXT,
            ticker TEXT,
            name TEXT,
            quantity REAL,
            avg_price REAL,
            current_price REAL,
            market_value REAL,
            cost REAL,
            pnl REAL,
            weight REAL,
            return_pct REAL,
            sector TEXT,
            fx_impact REAL,
            inst_currency TEXT,
            PRIMARY KEY(snapshot_date, ticker)
        );

        CREATE TABLE IF NOT EXISTS news(
            snapshot_date TEXT,
            ticker TEXT,
            title TEXT,
            source TEXT,
            sentiment TEXT,
            url TEXT
        );

        CREATE TABLE IF NOT EXISTS earnings(
            snapshot_date TEXT,
            ticker TEXT,
            earnings_date TEXT,
            session TEXT
        );

        CREATE TABLE IF NOT EXISTS reports(
            snapshot_date TEXT PRIMARY KEY,
            json TEXT
        );

        """)

    def save_snapshot(self, portfolio):

        snapshot = Snapshot(
            snapshot_date=date.today(),
            total_value=portfolio["total_value"],
            cash=portfolio["cash"],
            cash_ratio=portfolio["cash_ratio"],
            invested=portfolio["invested"],
            current_value=portfolio["current_value"],
            unrealized_pnl=portfolio["unrealized_pnl"],
            realized_pnl=portfolio["realized_pnl"],
            currency=portfolio["currency"]
        )

        self.conn.execute(
            """
            INSERT OR REPLACE INTO snapshots
            VALUES (?,?,?,?,?,?,?,?,?)
            """,
            (
                snapshot.snapshot_date.isoformat(),
                snapshot.total_value,
                snapshot.cash,
                snapshot.cash_ratio,
                snapshot.invested,
                snapshot.current_value,
                snapshot.unrealized_pnl,
                snapshot.realized_pnl,
                snapshot.currency
            )
        )

        self.conn.commit()

    def save_positions(self, portfolio):
        today = date.today().isoformat()

        sql = """
        INSERT OR REPLACE INTO positions
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """

        for p in portfolio["positions"]:
            row = PositionRecord(
                snapshot_date=date.today(),
                ticker=p["ticker"],
                name=p["name"],
                quantity=p["quantity"],
                avg_price=p["avg_price"],
                current_price=p["current_price"],
                market_value=p["market_value"],
                cost=p["cost"],
                pnl=p["pnl"],
                weight=p["weight"],
                return_pct=p["return_pct"],
                sector=p["sector"],
                fx_impact=p["fx_impact"],
                inst_currency=p["inst_currency"]
            )

            self.conn.execute(sql, (
                today,
                row.ticker,
                row.name,
                row.quantity,
                row.avg_price,
                row.current_price,
                row.market_value,
                row.cost,
                row.pnl,
                row.weight,
                row.return_pct,
                row.sector,
                row.fx_impact,
                row.inst_currency
            ))

        self.conn.commit()

    def save_news(self, news_items):

        today = date.today().isoformat()

        sql = """
        INSERT OR REPLACE INTO news
        VALUES (?,?,?,?,?,?)
        """

        for n in news_items:
            self.conn.execute(sql, (
                today,
                n["ticker"],
                n["title"],
                n["source"],
                n["sentiment"],
                n["url"]
            ))

        self.conn.commit()

    def save_earnings(self, earnings_items):
        today = date.today().isoformat()
        sql = """
        INSERT OR REPLACE INTO earnings
        VALUES (?,?,?,?,?)
        """
        for n in earnings_items:
            self.conn.execute(sql, (
                today,
                n["ticker"],
                n["earnings_date"],
                n["session"]
            ))

    def save_report(self, report):

        self.conn.execute(
            """
            INSERT OR REPLACE INTO reports
            VALUES (?, ?)
            """,
            (
                date.today().isoformat(),
                report.model_dump_json()
            )
        )

        self.conn.commit()

    def get_history(self, days=30):

        cur = self.conn.execute(
            """
            SELECT *
            FROM snapshots
            ORDER BY snapshot_date DESC
            LIMIT ?
            """,
            (days,)
        )

        return [dict(r) for r in cur.fetchall()]

    def get_position_history(self, ticker):

        cur = self.conn.execute(
            """
            SELECT snapshot_date,
                   quantity,
                   weight,
                   market_value
            FROM positions
            WHERE ticker=?
            ORDER BY snapshot_date
            """,
            (ticker,)
        )

        return [dict(r) for r in cur.fetchall()]

    def latest_snapshot(self):

        cur = self.conn.execute(
            """
            SELECT *
            FROM snapshots
            ORDER BY snapshot_date DESC
            LIMIT 1
            """
        )

        row = cur.fetchone()

        return dict(row) if row else None

    def latest_positions(self):

        cur = self.conn.execute(
            """
            SELECT *
            FROM positions
            WHERE snapshot_date = (
                SELECT MAX(snapshot_date)
                FROM positions
            )
            ORDER BY weight DESC
            """
        )

        return [dict(r) for r in cur.fetchall()]

    def today_news(self):

        today = date.today().isoformat()

        cur = self.conn.execute(
            """
            SELECT *
            FROM news
            WHERE snapshot_date = ?
            ORDER BY ticker
            """,
            (today,)
        )

        return [dict(r) for r in cur.fetchall()]

    def latest_report(self):

        cur = self.conn.execute(
            """
            SELECT json
            FROM reports
            ORDER BY snapshot_date DESC
            LIMIT 1
            """
        )

        row = cur.fetchone()

        if row is None:
            return None

        return Report.model_validate_json(row["json"])

    def monthly_returns(self):

        cur = self.conn.execute(
            """
            SELECT
                substr(snapshot_date, 1, 7) AS month,
                MIN(total_value) AS start_value,
                MAX(total_value) AS end_value
            FROM snapshots
            GROUP BY month
            ORDER BY month
            """
        )

        rows = []

        for r in cur.fetchall():
            start = r["start_value"]
            end = r["end_value"]

            pct = (
                (end - start) / start * 100
                if start else 0
            )

            rows.append({
                "month": r["month"],
                "return_pct": round(pct, 2)
            })

        return rows