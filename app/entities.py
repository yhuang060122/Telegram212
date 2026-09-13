from dataclasses import dataclass
from datetime import date

@dataclass
class Snapshot:
    snapshot_date: date
    total_value: float
    cash: float
    cash_ratio: float
    invested: float
    current_value: float
    unrealized_pnl: float
    realized_pnl: float
    currency: str

@dataclass
class PositionRecord:
    snapshot_date: date
    ticker: str
    name: str
    quantity: float
    avg_price: float
    current_price: float
    market_value: float
    cost: float
    pnl: float
    weight: float
    return_pct: float
    sector: str
    fx_impact: float
    inst_currency: str

@dataclass
class NewsRecord:
    snapshot_date: date
    ticker: str
    title: str
    source: str
    sentiment: str
    url: str

@dataclass
class EarningsRecord:
    snapshot_date: date
    ticker: str
    earnings_date: str
    session: str