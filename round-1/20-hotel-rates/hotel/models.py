from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional, Tuple

FLEXIBLE, NON_REFUNDABLE = "FLEXIBLE", "NON_REFUNDABLE"
CONFIRMED, CANCELLED = "CONFIRMED", "CANCELLED"


@dataclass(frozen=True)
class Quote:
    nightly: Tuple[Decimal, ...]
    subtotal: Decimal
    los_discount: Decimal
    plan_discount: Decimal
    promo: Decimal
    room_total: Decimal
    tax: Decimal
    city_fee: Decimal
    total: Decimal


@dataclass
class Reservation:
    reservation_id: str
    guest: str
    room_type: str
    check_in: date
    check_out: date
    plan: str
    promo_code: Optional[str]
    quote: Quote
    status: str = CONFIRMED
    refund: Optional[Decimal] = None
