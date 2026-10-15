from datetime import date
from decimal import Decimal

from .calendar import add_business_days
from .daycount import days_30_360
from .models import Bond
from .schedule import previous_and_next

SETTLEMENT_LAG_DAYS = 1


def settlement_date(trade_date: date) -> date:
    return add_business_days(trade_date, SETTLEMENT_LAG_DAYS)


def accrued_interest(bond: Bond, settle: date) -> Decimal:
    last_coupon, _ = previous_and_next(bond, settle)
    days = days_30_360(last_coupon, settle)
    raw = bond.face * bond.coupon_rate * days / 360
    return Decimal(int(raw * 100)) / 100


def settlement_amount(bond: Bond, clean_price: Decimal, settle: date) -> Decimal:
    return clean_price * bond.face / 100 + accrued_interest(bond, settle)
