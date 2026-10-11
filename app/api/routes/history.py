from fastapi import APIRouter, Query

from app.api.dependencies import RepositoryDep
from app.api.schemas import HistoryResponse

router = APIRouter(tags=["History"])


@router.get(
    "/api/history",
    response_model=HistoryResponse,
    summary="Get portfolio history",
)
def get_history(
    repository: RepositoryDep,
    days: int = Query(default=30, ge=1, le=365),
) -> HistoryResponse:
    items = repository.history(days=days)

    return HistoryResponse(
        days=days,
        count=len(items),
        items=items,
    )
