from typing import Literal

from pydantic import BaseModel, ConfigDict

from app.domain.portfolio import PortfolioSnapshot


class CollectorStatus(BaseModel):
    """Status of each external data collector."""

    model_config = ConfigDict(frozen=True)

    status: Literal[
        "ok",
        "empty",
        "partial",
        "failed",
    ]

    count: int = 0

    error: str | None = None


class DataQualityIssue(BaseModel):
    severity: Literal["warning", "error"]
    code: str
    message: str


class DataQualityReport(BaseModel):
    valid: bool
    cleaned: list[PortfolioSnapshot]
    issues: list[DataQualityIssue]
