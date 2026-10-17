from dataclasses import dataclass
from datetime import date
from decimal import Decimal

THIRTY_360, ACT_360 = "30/360", "ACT/360"


@dataclass(frozen=True)
class Bond:
    bond_id: str
    coupon: Decimal
    frequency: int
    maturity: date
    day_count: str


@dataclass(frozen=True)
class Trade:
    trade_id: str
    bond_id: str
    side: str
    face: Decimal
    clean_price: Decimal
    trade_date: date
    settle_date: date
    accrued: Decimal
    settlement_amount: Decimal
