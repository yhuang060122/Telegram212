from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_analytics_service, get_repository
from app.domain.portfolio import Portfolio
from app.repository import Repository
from app.services.analytics_service import AnalyticsService

router = APIRouter(tags=["analytics"])


@router.get("/analytics")
def portfolio_analytics(
    repository: Repository = Depends(get_repository),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
) -> dict:
    """Calculate analytics using the existing domain and analytics service."""
    try:
        snapshot_rows = repository.latest_snapshot()
        if not snapshot_rows:
            raise HTTPException(
                status_code=404,
                detail="No portfolio snapshot is available yet",
            )

        snapshot = snapshot_rows[0]
        positions = repository.latest_positions()
        history = repository.history(365)
        cashflows = repository.cashflows(365)

        portfolio = Portfolio(
            currency=snapshot["currency"],
            total_value=float(snapshot["total_value"]),
            current_value=float(snapshot["current_value"]),
            invested=float(snapshot["invested"]),
            cash_available=float(snapshot["cash"]),
            cash_reserved=0.0,
            unrealized_pnl=float(snapshot["unrealized_pnl"]),
            realized_pnl=float(snapshot["realized_pnl"]),
            positions=positions,
        )

        result = analytics_service.calculate(
            portfolio=portfolio,
            history=history,
            cashflows=cashflows,
        )
        return result.model_dump(mode="json")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Could not calculate portfolio analytics",
        ) from exc
