from datetime import datetime
from decimal import Decimal

from app.domain.cashflow import CashFlow, CashFlowType


def create_cashflows():
    return [
        CashFlow(
            reference="TXN001",
            datetime=datetime(2026, 1, 1, 9, 0),
            amount=Decimal("-10000"),
            currency="EUR",
            type=CashFlowType.DEPOSIT,
        ),
        CashFlow(
            reference="TXN002",
            datetime=datetime(2026, 1, 3, 9, 0),
            amount=Decimal("-5000"),
            currency="EUR",
            type=CashFlowType.DEPOSIT,
        ),
        CashFlow(
            reference="TXN003",
            datetime=datetime(2026, 1, 5, 17, 0),
            amount=Decimal("17000"),
            currency="EUR",
            type=CashFlowType.WITHDRAWAL,
        ),
    ]
