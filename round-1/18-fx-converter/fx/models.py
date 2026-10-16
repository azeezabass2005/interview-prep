from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

BOOKED, CANCELLED = "BOOKED", "CANCELLED"


@dataclass
class Quote:
    quote_id: str
    customer: str
    source: str
    source_amount: Decimal
    target: str
    target_amount: Decimal
    mid: Decimal
    spread: Decimal
    usd_equivalent: Decimal
    created_at: datetime
    booked: bool = False


@dataclass
class Payment:
    payment_id: str
    quote_id: str
    customer: str
    booked_at: datetime
    status: str = BOOKED
