from fastapi import APIRouter, Depends, HTTPException

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
