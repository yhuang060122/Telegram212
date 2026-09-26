from datetime import datetime
from decimal import Decimal

from app.domain.cashflow import CashFlow, CashFlowType


def flow(flow_type):
    return CashFlow(
        reference="ABC123",
        datetime=datetime(2026, 1, 1, 10, 0),
        amount=Decimal("100"),
        currency="EUR",
        type=flow_type,
    )


class TestCashFlow:

    def test_deposit_external(self):
        assert flow(CashFlowType.DEPOSIT).is_external is True

    def test_withdrawal_external(self):
        assert flow(CashFlowType.WITHDRAWAL).is_external is True

    def test_fee_not_external(self):
        assert flow(CashFlowType.FEE).is_external is False

    def test_interest_not_external(self):
        assert flow(CashFlowType.INTEREST).is_external is False

    def test_transfer_not_external(self):
        assert flow(CashFlowType.TRANSFER).is_external is False

    def test_amount_decimal(self):
        f = flow(CashFlowType.DEPOSIT)

        assert isinstance(f.amount, Decimal)

    def test_reference(self):
        f = flow(CashFlowType.DEPOSIT)

        assert f.reference == "ABC123"
