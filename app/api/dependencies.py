from functools import lru_cache

from app.repository import Repository
from app.services.analytics_service import AnalyticsService


@lru_cache(maxsize=1)
def get_repository() -> Repository:
    """Create the repository lazily so importing the API does not require secrets."""
    return Repository()


@lru_cache(maxsize=1)
def get_analytics_service() -> AnalyticsService:
    return AnalyticsService()
