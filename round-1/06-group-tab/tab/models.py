from dataclasses import dataclass, field
from typing import Dict, List

EQUAL, EXACT, PERCENT, SHARES = "EQUAL", "EXACT", "PERCENT", "SHARES"


@dataclass
class Group:
    group_id: str
    name: str
    members: List[str] = field(default_factory=list)


@dataclass
class Expense:
    expense_id: int
    group_id: str
    payer: str
    amount_cents: int
    description: str
    split_type: str
    shares: Dict[str, int]
    deleted: bool = False


@dataclass(frozen=True)
class Payment:
    payment_id: int
    group_id: str
    sender: str
    receiver: str
    amount_cents: int


@dataclass(frozen=True)
class Transfer:
    sender: str
    receiver: str
    amount_cents: int
