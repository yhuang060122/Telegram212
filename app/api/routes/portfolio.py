from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import get_repository
from app.repository import Repository

router = APIRouter(tags=["portfolio"])


@router.get("/portfolio")
def latest_portfolio(
    repository: Repository = Depends(get_repository),
) -> dict:
    """Return the latest snapshot and the positions belonging to it."""
    try:
        rows = repository.latest_snapshot()
        snapshot = rows[0] if rows else None
        positions = repository.latest_positions() if snapshot else []
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Could not load portfolio data",
        ) from exc

    return {
        "snapshot": snapshot,
        "positions": [
            position.model_dump(mode="json") for position in positions
        ],
    }


@router.get("/positions")
def latest_positions(
    repository: Repository = Depends(get_repository),
) -> list[dict]:
    try:
        positions = repository.latest_positions()
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Could not load positions",
        ) from exc

    return [position.model_dump(mode="json") for position in positions]


@router.get("/history")
def portfolio_history(
    days: int = Query(default=365, ge=1, le=3650),
    repository: Repository = Depends(get_repository),
) -> list[dict]:
    try:
        rows = repository.history(days)
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Could not load portfolio history",
        ) from exc

    return [row.model_dump(mode="json") for row in rows]


@router.get("/monthly-returns")
def monthly_returns(
    repository: Repository = Depends(get_repository),
) -> list[dict]:
    try:
        return repository.monthly_returns()
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Could not load monthly returns",
        ) from exc


@router.get("/positions/{ticker}/history")
def position_history(
    ticker: str,
    repository: Repository = Depends(get_repository),
) -> list[dict]:
    try:
        return repository.position_history(ticker.upper())
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Could not load position history",
        ) from exc
