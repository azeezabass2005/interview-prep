from dataclasses import dataclass
from datetime import datetime

OPEN = "OPEN"
CLOSED = "CLOSED"


@dataclass(frozen=True)
class Account:
    account_id: str
    owner: str
    balance_cents: int
    status: str


@dataclass(frozen=True)
class Entry:
    entry_id: int
    account_id: str
    amount_cents: int
    kind: str
    reference: str
    created_at: datetime
