from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import get_repository
from app.repository import Repository

router = APIRouter(tags=["research"])


@router.get("/report/latest")
def latest_report(
    repository: Repository = Depends(get_repository),
) -> dict | None:
    try:
        report = repository.latest_report()
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Could not load the latest AI report",
        ) from exc

    return report.model_dump(mode="json") if report else None


@router.get("/news")
def latest_news(
    repository: Repository = Depends(get_repository),
) -> list[dict]:
    try:
        news = repository.today_news()
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Could not load news",
        ) from exc

    return [item.model_dump(mode="json") for item in news]


@router.get("/earnings")
def upcoming_earnings(
    days: int = Query(default=30, ge=1, le=365),
    repository: Repository = Depends(get_repository),
) -> list[dict]:
    try:
        events = repository.upcoming_earnings(days)
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Could not load upcoming earnings",
        ) from exc
    return [event.model_dump(mode="json") for event in events]


@router.get("/macro/latest")
def latest_macro(
    repository: Repository = Depends(get_repository),
) -> dict | None:
    try:
        macro = repository.latest_macro()
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Could not load macro data",
        ) from exc
    return macro.model_dump(mode="json") if macro else None
