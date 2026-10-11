from fastapi import APIRouter, HTTPException

from app.api.dependencies import RepositoryDep
from app.api.schemas import LatestReportResponse

router = APIRouter(tags=["Reports"])


@router.get(
    "/api/reports/latest",
    response_model=LatestReportResponse,
    summary="Get latest AI report",
)
def get_latest_report(
    repository: RepositoryDep,
) -> LatestReportResponse:
    report = repository.latest_report()

    if report is None:
        raise HTTPException(
            status_code=404,
            detail="No AI report is available.",
        )

    return LatestReportResponse(report=report)
