from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict


class CashFlowType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    INTEREST = "interest"
    FEE = "fee"
    TRANSFER = "transfer"


class CashFlow(BaseModel):
    model_config = ConfigDict(frozen=True)

    reference: str

    datetime: datetime

    amount: Decimal
    currency: str

    type: CashFlowType

    @property
    def is_external(self) -> bool:
        return self.type in {
            CashFlowType.DEPOSIT,
            CashFlowType.WITHDRAWAL,
        }
