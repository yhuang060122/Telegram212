from fastapi import APIRouter

from app.api.dependencies import RepositoryDep
from app.api.schemas import PositionsResponse

router = APIRouter(tags=["Positions"])


@router.get(
    "/api/positions",
    response_model=PositionsResponse,
    summary="Get current positions",
)
def get_positions(repository: RepositoryDep) -> PositionsResponse:
    positions = repository.latest_positions()

    return PositionsResponse(
        count=len(positions),
        items=positions,
    )
