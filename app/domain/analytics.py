from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Allocation(BaseModel):
    """Allocation breakdown."""

    model_config = ConfigDict(frozen=True)

    name: str
    weight: float
    value: float


class ConcentrationMetrics(BaseModel):
    """Concentration metrics."""

    model_config = ConfigDict(frozen=True)

    top1: float | None = None
    top3: float | None = None
    top5: float | None = None

    # Herfindahl–Hirschman Index (HHI)
    herfindahl: float
    risk_level: Literal["High", "Medium", "Low"]


class RiskMetrics(BaseModel):
    """Portfolio  risk metrics."""

    model_config = ConfigDict(frozen=True)

    concentration: ConcentrationMetrics

    # 年化波动率
    volatility: float | None = None
    # 夏普比率
    sharpe: float | None = None

    drawdown: float | None = None
    max_drawdown: float | None = None


class PerformanceMetrics(BaseModel):
    """Portfolio performance metrics."""
    model_config = ConfigDict(frozen=True)

    daily_return: float | None = None
    weekly_return: float | None = None
    monthly_return: float | None = None

    twr: float | None = None
    xirr: float | None = None

    total_return: float | None = None


class PortfolioAnalytics(BaseModel):
    """
    Computed analytics for a portfolio.

    This model contains only derived values.
    It never stores raw portfolio positions.
    """

    model_config = ConfigDict(frozen=True)

    performance: PerformanceMetrics = Field(default_factory=PerformanceMetrics)
    risk: RiskMetrics = Field(default_factory=RiskMetrics)
    sector_allocation: list[Allocation] = Field(default_factory=list)
    position_allocation: list[Allocation] = Field(default_factory=list)
