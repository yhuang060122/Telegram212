from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, HTTPException, Request

from app.repository import Repository


def get_repository(request: Request) -> Generator[Repository, None, None]:
    """
    Return a lazily initialized, process-local repository.

    The Repository is created only when an endpoint requests it.
    The instance is reused through app.state.
    """
    repository = getattr(request.app.state, "repository", None)

    if repository is None:
        try:
            repository = Repository()
        except (ValueError, RuntimeError) as exc:
            raise HTTPException(
                status_code=503, detail="Data service is not configured or unavailable"
            ) from exc
        request.app.state.repository = repository

    yield repository


RepositoryDep = Annotated[Repository, Depends(get_repository)]
