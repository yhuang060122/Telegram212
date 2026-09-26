from __future__ import annotations

import math
from collections import defaultdict
from datetime import datetime, timezone
from typing import Literal

from pyxirr import xirr

from app.domain.analytics import (
    Allocation,
    PerformanceMetrics,
    PortfolioAnalytics,
    RiskMetrics, ConcentrationMetrics,
)
from app.domain.cashflow import CashFlow
from app.domain.portfolio import Portfolio


class AnalyticsService:
    """Compute derived analytics from Portfolio + historical snapshots."""

    def calculate(self,
                  portfolio: Portfolio,
                  history: list[dict],
                  cashflows: list[CashFlow],
                  ) -> PortfolioAnalytics:
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
            history: list[dict],
            cashflows: list[CashFlow],
    ) -> PerformanceMetrics:

        return PerformanceMetrics(

            daily_return=self._period_return(history, 1),
            weekly_return=self._period_return(history, 5),
            monthly_return=self._period_return(history, 21),

            total_return=portfolio.return_pct,

            twr=self._twr(history, cashflows),

            xirr=self._xirr(portfolio, cashflows),
        )

    # ---------- Risk ----------

    def _risk(self, portfolio: Portfolio, history: list[dict]) -> RiskMetrics:

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
    def _sector_allocation(portfolio):

        totals = {}

        for p in portfolio.positions:
            totals.setdefault(
                p.sector,
                0,
            )
            totals[p.sector] += p.market_value

        return sorted(
            [
                Allocation(
                    name=sector,
                    value=value,
                    weight=round(
                        value / portfolio.total_value * 100,
                        2,
                    ),
                )
                for sector, value in totals.items()
            ],
            key=lambda x: x.weight,
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

    # ---------- Helpers ----------

    @staticmethod
    def _herfindahl(portfolio):

        weights = [
            p.weight / 100
            for p in portfolio.positions
        ]

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
    def _daily_returns(history: list[dict]) -> list[float]:

        if len(history) < 2:
            return []

        returns = []

        for prev, curr in zip(history[:-1], history[1:]):
            prev_value = prev["total_value"]
            if prev_value == 0:
                continue

            r = (curr["total_value"] - prev_value) / prev_value

            returns.append(r)

        return returns

    def _volatility(self, history: list[dict]) -> float | None:
        returns = self._daily_returns(history)
        if len(returns) < 2:
            return None
        mean_daily = sum(returns) / len(returns)
        variance = sum((r - mean_daily) ** 2 for r in returns) / (len(returns) - 1)
        daily_vol = math.sqrt(variance)
        annual_vol = daily_vol * math.sqrt(252)

        return round(annual_vol * 100, 2)

    def _sharpe(
            self,
            history: list[dict],
            risk_free_rate: float = 0.02,
    ) -> float | None:

        returns = self._daily_returns(history)

        if len(returns) < 2:
            return None

        mean_daily = sum(returns) / len(returns)
        variance = sum(
            (r - mean_daily) ** 2
            for r in returns
        ) / (len(returns) - 1)

        daily_vol = math.sqrt(variance)

        if daily_vol == 0:
            return None

        annual_return = mean_daily * 252

        annual_vol = daily_vol * math.sqrt(252)

        sharpe = (annual_return - risk_free_rate) / annual_vol

        return round(sharpe, 2)

    @staticmethod
    def _drawdown_metrics(history: list[dict]) -> tuple[float | None, float | None]:
        if not history:
            return None, None

        peak = history[0]["total_value"]

        current_dd = 0.0
        max_dd = 0.0

        for row in history:
            value = row["total_value"]
            peak = max(peak, value)
            dd = (value - peak) / peak * 100
            current_dd = dd
            max_dd = min(max_dd, dd)

        return round(current_dd, 2), round(max_dd, 2)

    @staticmethod
    def _period_return(history: list[dict], periods: int) -> float | None:
        if len(history) <= periods:
            return None

        if len(history) <= periods:
            return None

        start = history[-(periods + 1)]["total_value"]
        end = history[-1]["total_value"]

        if start == 0:
            return None

        return round((end - start) / start * 100, 2)

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
            rate = xirr(dates, amounts)
            return round(rate * 100, 2)

        except Exception:
            return None

    @staticmethod
    def _twr(
            history: list[dict],
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

        for prev, curr in zip(history[:-1], history[1:]):

            start = prev["total_value"]
            end = curr["total_value"]

            flow = flows.get(curr["snapshot_date"], 0.0)

            adjusted_end = end - flow

            if start == 0:
                continue

            period_return = (adjusted_end - start) / start

            cumulative *= (1 + period_return)

        return round((cumulative - 1) * 100, 2)
