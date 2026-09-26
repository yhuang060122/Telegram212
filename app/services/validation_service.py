from __future__ import annotations

from datetime import date
from typing import Iterable

from app.domain.portfolio import PortfolioSnapshot
from app.domain.validation import (
    DataQualityIssue,
    DataQualityReport,
)


class ValidationService:
    """Validate & clean historical portfolio snapshots."""

    def __init__(self, jump_threshold: float = 0.5):
        """
        Parameters
        ----------
        jump_threshold
            Percentage expressed as decimal.
            0.5 = 50%
        """
        self.jump_threshold = jump_threshold

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def validate_history(
            self,
            history: Iterable[PortfolioSnapshot],
    ) -> DataQualityReport:
        """Validate historical snapshots and return cleaned history."""

        cleaned = self.clean_history(history)

        issues: list[DataQualityIssue] = []

        if not cleaned:
            issues.append(
                DataQualityIssue(
                    severity="error",
                    code="EMPTY_HISTORY",
                    message="Portfolio history is empty.",
                )
            )

            return DataQualityReport(
                valid=False,
                cleaned=[],
                issues=issues,
            )

        issues.extend(self._check_positive_nav(cleaned))
        issues.extend(self._check_date_gap(cleaned))
        issues.extend(self._check_large_jump(cleaned))

        valid = not any(i.severity == "error" for i in issues)

        return DataQualityReport(
            valid=valid,
            cleaned=cleaned,
            issues=issues,
        )

    def clean_history(
            self,
            history: Iterable[PortfolioSnapshot],
    ) -> list[PortfolioSnapshot]:
        """
        Sort snapshots and remove duplicated dates.

        If multiple snapshots exist on the same day,
        keep the latest one in the iterable.
        """

        latest_per_day: dict[date, PortfolioSnapshot] = {}

        for snapshot in history:
            latest_per_day[snapshot.snapshot_date] = snapshot

        return sorted(
            latest_per_day.values(),
            key=lambda s: s.snapshot_date,
        )

    # ---------------------------------------------------------
    # Internal checks
    # ---------------------------------------------------------

    def _check_positive_nav(
            self,
            history: list[PortfolioSnapshot],
    ) -> list[DataQualityIssue]:
        issues = []

        for s in history:
            if s.total_value <= 0:
                issues.append(
                    DataQualityIssue(
                        severity="error",
                        code="INVALID_NAV",
                        message=(
                            f"NAV must be positive "
                            f"({s.snapshot_date})"
                        ),
                    )
                )

        return issues

    def _check_date_gap(
            self,
            history: list[PortfolioSnapshot],
    ) -> list[DataQualityIssue]:
        issues = []

        for prev, curr in zip(history, history[1:]):
            gap = (
                    curr.snapshot_date - prev.snapshot_date
            ).days

            if gap > 5:
                issues.append(
                    DataQualityIssue(
                        severity="warning",
                        code="DATE_GAP",
                        message=(
                            f"Gap of {gap} days between "
                            f"{prev.snapshot_date} and "
                            f"{curr.snapshot_date}"
                        ),
                    )
                )

        return issues

    def _check_large_jump(
            self,
            history: list[PortfolioSnapshot],
    ) -> list[DataQualityIssue]:
        issues = []

        for prev, curr in zip(history, history[1:]):

            if prev.total_value == 0:
                continue

            pct = (
                          curr.total_value - prev.total_value
                  ) / prev.total_value

            if abs(pct) >= self.jump_threshold:
                issues.append(
                    DataQualityIssue(
                        severity="warning",
                        code="LARGE_NAV_JUMP",
                        message=(
                            f"{pct:.1%} NAV change on "
                            f"{curr.snapshot_date}"
                        ),
                    )
                )

        return issues
