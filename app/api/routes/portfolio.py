from fastapi import APIRouter

from app.api.dependencies import RepositoryDep
from app.api.mappers import map_portfolio
from app.api.schemas import PortfolioResponse

router = APIRouter(tags=["portfolio"])


@router.get(
    "/api/portfolio",
    response_model=PortfolioResponse,
    summary="Get the latest portfolio",
)
def get_portfolio(repository: RepositoryDep) -> PortfolioResponse:
    snapshot_rows = repository.latest_snapshot()
    positions = repository.latest_positions()
    return map_portfolio(snapshot_rows, positions)
