from fastapi import APIRouter, HTTPException

from app.api.dependencies import RepositoryDep
from app.domain.portfolio import Portfolio
from app.services.analytics_service import AnalyticsService

router = APIRouter(tags=["Analytics"])


@router.get(
    "/api/analytics",
    summary="Get portfolio analytics",
)
def get_analytics(repository: RepositoryDep):
    snapshot_rows = repository.latest_snapshot()

    if not snapshot_rows:
        raise HTTPException(
            status_code=404,
            detail="No portfolio snapshot is available.",
        )

    snapshot = snapshot_rows[0]
    positions = repository.latest_positions()
    history = repository.history(days=365)
    cashflows = repository.cashflows(days=365)

    portfolio = Portfolio(
        currency=snapshot["currency"],
        total_value=snapshot["total_value"],
        current_value=snapshot["current_value"],
        invested=snapshot["invested"],
        cash_available=snapshot["cash"],
        cash_reserved=0.0,
        unrealized_pnl=snapshot["unrealized_pnl"],
        realized_pnl=snapshot["realized_pnl"],
        positions=positions,
    )

    service = AnalyticsService()
    return service.calculate(
        portfolio=portfolio,
        history=history,
        cashflows=cashflows,
    )
