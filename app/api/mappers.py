from typing import Any

from fastapi import HTTPException

from app.api.schemas import PortfolioResponse
from app.domain.position import Position


def map_portfolio(
    snapshot_rows: list[dict[str, Any]],
    positions: list[Position],
) -> PortfolioResponse:
    """Convert persisted snapshot rows and positions to an API response"""

    if not snapshot_rows:
        raise HTTPException(
            status_code=404,
            detail="No portfolio snapshot is available.",
        )

    snapshot = snapshot_rows[0]

    return PortfolioResponse(
        snapshot_date=snapshot["snapshot_date"],
        currency=snapshot["currency"],
        total_value=snapshot["total_value"],
        current_value=snapshot["current_value"],
        invested=snapshot["invested"],
        cash=snapshot["cash"],
        cash_ratio=snapshot["cash_ratio"],
        unrealized_pnl=snapshot["unrealized_pnl"],
        realized_pnl=snapshot["realized_pnl"],
        positions=positions,
    )
