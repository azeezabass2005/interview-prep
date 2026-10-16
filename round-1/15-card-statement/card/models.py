from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Dict, List, Optional

PURCHASE, REFUND, CASH, PAYMENT, FEE = "PURCHASE", "REFUND", "CASH", "PAYMENT", "FEE"


@dataclass(frozen=True)
class Txn:
    posted_on: date
    kind: str
    amount: Decimal


@dataclass(frozen=True)
class Statement:
    cycle_start: date
    cycle_end: date
    days: int
    interest: Dict[str, Decimal]
    fees: Decimal
    balances: Dict[str, Decimal]
    new_balance: Decimal
    minimum_due: Decimal
    due_date: date


@dataclass
class Account:
    account_id: str
    credit_limit: Decimal
    opened_on: date
    txns: List[Txn] = field(default_factory=list)
    statements: List[Statement] = field(default_factory=list)

    @property
    def last_statement(self) -> Optional[Statement]:
        return self.statements[-1] if self.statements else None
