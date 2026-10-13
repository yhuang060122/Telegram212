from __future__ import annotations

import math
from collections import defaultdict
from datetime import date, datetime, timezone
from typing import Literal

from app.domain.analytics import (
    Allocation,
    ConcentrationMetrics,
    PerformanceMetrics,
    PortfolioAnalytics,
    RiskMetrics,
)
from app.domain.cashflow import CashFlow
from app.domain.portfolio import Portfolio, PortfolioSnapshot


def _calculate_xirr(
    dates: list[date],
    amounts: list[float],
) -> float | None:
    """Calculate XIRR using pure Python and bisection."""

    if len(dates) != len(amounts) or len(dates) < 2:
        return None

    if not (
        any(amount < 0 for amount in amounts) and any(amount > 0 for amount in amounts)
    ):
        return None

    start_date = min(dates)
    years = [(d - start_date).days / 365.0 for d in dates]

    def npv(rate: float) -> float:
        return sum(
            amount / (1.0 + rate) ** year
            for amount, year in zip(amounts, years, strict=True)
        )

    # Search for a sign-changing interval above -100%.
    lower = -0.9999
    upper = 1.0

    try:
        f_lower = npv(lower)
        f_upper = npv(upper)

        for _ in range(60):
            if f_lower * f_upper <= 0:
                break
            upper = upper * 2 + 1
            f_upper = npv(upper)
        else:
            return None

        for _ in range(200):
            mid = (lower + upper) / 2
            f_mid = npv(mid)

            if abs(f_mid) < 1e-8:
                return mid

            if f_lower * f_mid <= 0:
                upper = mid
                f_upper = f_mid
            else:
                lower = mid
                f_lower = f_mid

        return (lower + upper) / 2

    except (OverflowError, ZeroDivisionError):
        return None


class AnalyticsService:
    """Compute derived analytics from Portfolio + historical snapshots."""

    def __init__(self):
        self.risk_free_rate = 0.02

    def calculate(
        self,
        portfolio: Portfolio,
        history: list[PortfolioSnapshot],
        cashflows: list[CashFlow],
        risk_free_rate: float = 0.02,
    ) -> PortfolioAnalytics:
        self.risk_free_rate = risk_free_rate
        return PortfolioAnalytics(
            performance=self._performance(
                portfolio,
                history,
                cashflows,
            ),
            risk=self._risk(portfolio, history),
            sector_allocation=self._sector_allocation(portfolio),
            position_allocation=self._position_allocation(portfolio),
        )

    # ---------- Performance ----------

    def _performance(
        self,
        portfolio: Portfolio,
        history: list[PortfolioSnapshot],
        cashflows: list[CashFlow],
    ) -> PerformanceMetrics:

        return PerformanceMetrics(
            daily_return=self._period_return(history, 1),
            weekly_return=self._period_return(history, 5),
            monthly_return=self._period_return(history, 21),
            total_return=self._total_return(history),
            twr=self._twr(history, cashflows),
            xirr=self._xirr(portfolio, cashflows),
        )

    # ---------- Risk ----------

    def _risk(
        self, portfolio: Portfolio, history: list[PortfolioSnapshot]
    ) -> RiskMetrics:

        drawdown, max_drawdown = self._drawdown_metrics(history)
        hhi = self._herfindahl(portfolio)

        return RiskMetrics(
            concentration=ConcentrationMetrics(
                top1=self._top_weight(portfolio, 1),
                top3=self._top_weight(portfolio, 3),
                top5=self._top_weight(portfolio, 5),
                herfindahl=hhi,
                risk_level=self._risk_level(hhi),
            ),
            drawdown=drawdown,
            max_drawdown=max_drawdown,
            volatility=self._volatility(history),
            sharpe=self._sharpe(history),
        )

    # ---------- Allocation ----------
    @staticmethod
    def _sector_allocation(portfolio: Portfolio) -> list[Allocation]:
        totals: dict[str, float] = {}

        for position in portfolio.positions:
            totals[position.sector] = (
                totals.get(position.sector, 0.0) + position.market_value
            )

        invested_value = sum(totals.values())

        if invested_value <= 0:
            return []

        return sorted(
            [
                Allocation(
                    name=sector,
                    value=value,
                    weight=round(value / invested_value * 100, 2),
                )
                for sector, value in totals.items()
            ],
            key=lambda item: item.weight,
            reverse=True,
        )

    @staticmethod
    def _position_allocation(
        portfolio: Portfolio,
    ) -> list[Allocation]:
        return sorted(
            [
                Allocation(
                    name=p.ticker,
                    weight=p.weight,
                    value=p.market_value,
                )
                for p in portfolio.positions
            ],
            key=lambda x: x.weight,
            reverse=True,
        )

    @staticmethod
    def _total_return(history: list[PortfolioSnapshot]) -> float:
        if len(history) < 2:
            return 0.0

        start_value = history[0].total_value
        end_value = history[-1].total_value

        if start_value <= 0:
            return 0.0

        return round((end_value - start_value) / start_value * 100, 2)

    # ---------- Helpers ----------

    @staticmethod
    def _herfindahl(portfolio):

        weights = [p.weight / 100 for p in portfolio.positions]

        return round(
            sum(w * w for w in weights),
            4,
        )

    @staticmethod
    def _top_weight(portfolio, n):

        weights = sorted(
            [p.weight for p in portfolio.positions],
            reverse=True,
        )

        return round(sum(weights[:n]), 2)

    @staticmethod
    def _risk_level(hhi) -> Literal["High", "Medium", "Low"]:

        if hhi >= 0.18:
            return "High"

        if hhi >= 0.10:
            return "Medium"

        return "Low"

    @staticmethod
    def _daily_returns(history: list[PortfolioSnapshot]) -> list[float]:

        if len(history) < 2:
            return []

        returns = []

        for prev, curr in zip(history[:-1], history[1:], strict=True):
            prev_value = prev.total_value
            if prev_value == 0:
                continue

            r = (curr.total_value - prev_value) / prev_value

            returns.append(r)

        return returns

    def _volatility(self, history: list[PortfolioSnapshot]) -> float | None:
        returns = self._daily_returns(history)
        if len(returns) < 2:
            return None
        mean_daily = sum(returns) / len(returns)
        variance = sum((r - mean_daily) ** 2 for r in returns) / (len(returns) - 1)
        daily_vol = math.sqrt(variance)
        annual_vol = daily_vol * math.sqrt(252)

        return round(annual_vol * 100, 2)

    def _sharpe(self, history: list[PortfolioSnapshot]) -> float | None:

        returns = self._daily_returns(history)

        if len(returns) < 2:
            return None

        mean_daily = sum(returns) / len(returns)
        variance = sum((r - mean_daily) ** 2 for r in returns) / (len(returns) - 1)

        daily_vol = math.sqrt(variance)

        if daily_vol == 0:
            return None

        annual_return = mean_daily * 252

        annual_vol = daily_vol * math.sqrt(252)

        sharpe = (annual_return - self.risk_free_rate) / annual_vol

        return round(sharpe, 2)

    @staticmethod
    def _drawdown_metrics(
        history: list[PortfolioSnapshot],
    ) -> tuple[float | None, float | None]:
        if not history:
            return None, None

        peak = history[0].total_value

        current_dd = 0.0
        max_dd = 0.0

        for row in history:
            value = row.total_value
            peak = max(peak, value)
            dd = (value - peak) / peak * 100
            current_dd = dd
            max_dd = min(max_dd, dd)

        return round(current_dd, 2), round(max_dd, 2)

    @staticmethod
    def _period_return(history: list[PortfolioSnapshot], periods: int) -> float | None:
        if len(history) <= periods:
            return None

        if len(history) <= periods:
            return None

        start = history[-(periods + 1)].total_value
        end = history[-1].total_value

        if start == 0:
            return None

        return round((end - start) / start * 100, 2)

    def calculate_xirr(self, portfolio, cashflows):
        return self._xirr(portfolio, cashflows)

    @staticmethod
    def _xirr(
        portfolio: Portfolio,
        cashflows: list[CashFlow],
    ) -> float | None:

        if not cashflows:
            return None

        dates = []
        amounts = []

        for cf in cashflows:
            dates.append(cf.datetime.date())
            amounts.append(float(cf.amount))

        # Current portfolio value = final inflow
        dates.append(datetime.now(timezone.utc).date())
        amounts.append(portfolio.total_value)

        try:
            rate = _calculate_xirr(
                dates=[cf.datetime.date() for cf in cashflows]
                + [datetime.now(timezone.utc).date()],
                amounts=[float(cf.amount) for cf in cashflows]
                + [float(portfolio.total_value)],
            )

            return round(rate * 100, 2) if rate is not None else None

        except Exception:
            return None

    @staticmethod
    def _twr(
        history: list[PortfolioSnapshot],
        cashflows: list[CashFlow],
    ) -> float | None:

        if len(history) < 2:
            return None

        # Group cashflow by day
        flows = defaultdict(float)

        for cf in cashflows:
            if cf.is_external:
                flows[cf.datetime.date()] += float(cf.amount)

        cumulative = 1.0

        for prev, curr in zip(history[:-1], history[1:], strict=True):
            start = prev.total_value
            end = curr.total_value

            flow = flows.get(curr.snapshot_date, 0.0)

            adjusted_end = end + flow

            if start == 0:
                continue

            period_return = (adjusted_end - start) / start

            cumulative *= 1 + period_return

        return round((cumulative - 1) * 100, 2)
