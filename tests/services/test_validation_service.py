from datetime import date

import pytest

from app.domain.portfolio import PortfolioSnapshot
from app.services.validation_service import ValidationService


@pytest.fixture
def service():
    return ValidationService()


def make_snapshot(
    day: int,
    total_value: float = 10_000,
) -> PortfolioSnapshot:
    snapshot_date = date(2026, 1, day)
    return PortfolioSnapshot(
        snapshot_date=snapshot_date,
        total_value=total_value,
        cash=0,
        cash_ratio=0,
        invested=total_value,
        current_value=total_value,
        unrealized_pnl=0,
        realized_pnl=0,
        currency="EUR",
    )


class TestCleanHistory:
    def test_empty_history(self, service):
        assert service.clean_history([]) == []

    def test_sorts_snapshots_by_date(self, service):
        history = [
            make_snapshot(3),
            make_snapshot(1),
            make_snapshot(2),
        ]

        cleaned = service.clean_history(history)

        assert [s.snapshot_date.day for s in cleaned] == [1, 2, 3]

    def test_keeps_last_snapshot_for_duplicate_date(self, service):
        first = make_snapshot(1, 10_000)
        second = make_snapshot(1, 12_000)
        other = make_snapshot(2, 13_000)

        cleaned = service.clean_history([first, other, second])

        assert len(cleaned) == 2
        assert cleaned[0].total_value == 12_000
        assert cleaned[1].total_value == 13_000


class TestValidateHistory:
    def test_empty_history_is_invalid(self, service):
        report = service.validate_history([])

        assert report.valid is False
        assert report.cleaned == []
        assert any(
            issue.code == "EMPTY_HISTORY" and issue.severity == "error"
            for issue in report.issues
        )

    def test_valid_history_has_no_issues(self, service):
        history = [
            make_snapshot(1, 10_000),
            make_snapshot(2, 10_100),
            make_snapshot(3, 10_200),
        ]

        report = service.validate_history(history)

        assert report.valid is True
        assert len(report.cleaned) == 3
        assert report.issues == []

    @pytest.mark.parametrize("nav", [0, -100])
    def test_non_positive_nav_is_invalid(self, service, nav):
        history = [
            make_snapshot(1, 10_000),
            make_snapshot(2, nav),
        ]

        report = service.validate_history(history)

        assert report.valid is False
        assert any(
            issue.code == "INVALID_NAV" and issue.severity == "error"
            for issue in report.issues
        )

    def test_duplicate_dates_are_cleaned_before_validation(self, service):
        history = [
            make_snapshot(1, 10_000),
            make_snapshot(1, 10_100),
            make_snapshot(2, 10_200),
        ]

        report = service.validate_history(history)

        assert report.valid is True
        assert len(report.cleaned) == 2


class TestDateGap:
    def test_gap_of_five_days_is_not_reported(self, service):
        history = [
            make_snapshot(1),
            make_snapshot(6),
        ]

        issues = service._check_date_gap(history)

        assert issues == []

    def test_gap_over_five_days_generates_warning(self, service):
        history = [
            make_snapshot(1),
            make_snapshot(7),
        ]

        issues = service._check_date_gap(history)

        assert len(issues) == 1
        assert issues[0].code == "DATE_GAP"
        assert issues[0].severity == "warning"

    def test_date_gap_warning_does_not_invalidate_report(self, service):
        history = [
            make_snapshot(1, 10_000),
            make_snapshot(7, 10_100),
        ]

        report = service.validate_history(history)

        assert report.valid is True
        assert any(issue.code == "DATE_GAP" for issue in report.issues)


class TestLargeNavJump:
    def test_jump_below_threshold_is_not_reported(self, service):
        history = [
            make_snapshot(1, 10_000),
            make_snapshot(2, 14_900),
        ]

        issues = service._check_large_jump(history)

        assert issues == []

    @pytest.mark.parametrize(
        ("previous", "current"),
        [
            (10_000, 15_000),  # +50%
            (10_000, 5_000),  # -50%
        ],
    )
    def test_jump_at_threshold_generates_warning(self, service, previous, current):
        history = [
            make_snapshot(1, previous),
            make_snapshot(2, current),
        ]

        issues = service._check_large_jump(history)

        assert len(issues) == 1
        assert issues[0].code == "LARGE_NAV_JUMP"
        assert issues[0].severity == "warning"

    def test_custom_jump_threshold(self):
        service = ValidationService(jump_threshold=0.2)
        history = [
            make_snapshot(1, 10_000),
            make_snapshot(2, 12_000),
        ]

        issues = service._check_large_jump(history)

        assert len(issues) == 1
        assert issues[0].code == "LARGE_NAV_JUMP"

    def test_zero_previous_nav_does_not_divide_by_zero(self, service):
        history = [
            make_snapshot(1, 0),
            make_snapshot(2, 10_000),
        ]

        issues = service._check_large_jump(history)

        assert issues == []

    def test_large_jump_warning_does_not_invalidate_report(self, service):
        history = [
            make_snapshot(1, 10_000),
            make_snapshot(2, 16_000),
        ]

        report = service.validate_history(history)

        assert report.valid is True
        assert any(issue.code == "LARGE_NAV_JUMP" for issue in report.issues)
