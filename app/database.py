from pathlib import Path
import sqlite3
from .entities import Snapshot, PositionRecord
from datetime import date

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