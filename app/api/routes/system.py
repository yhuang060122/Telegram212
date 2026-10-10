from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_repository
from app.repository import Repository

router = APIRouter(tags=["system"])


@router.get("/health")
def health(repository: Repository = Depends(get_repository)) -> dict[str, str]:
    try:
        healthy = repository.health_check()
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Database health check failed",
        ) from exc

    if not healthy:
        raise HTTPException(status_code=503, detail="Database is unavailable")

    return {"status": "ok", "database": "ok"}
