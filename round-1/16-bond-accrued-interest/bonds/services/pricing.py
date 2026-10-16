from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from ..daycount import year_fraction
from ..models import Bond
from ..schedule import surrounding_coupons

CENT = Decimal("0.01")


def accrued_interest(bond: Bond, face: Decimal, settle: date) -> Decimal:
    last_coupon, _ = surrounding_coupons(bond, settle)
    fraction = year_fraction(bond.day_count, last_coupon, settle)
    return (face * bond.coupon * fraction).quantize(CENT, rounding=ROUND_HALF_UP)


def settlement_amount(bond: Bond, face: Decimal, clean_price: Decimal, settle: date) -> Decimal:
    principal = (clean_price * face / 100).quantize(CENT, rounding=ROUND_HALF_UP)
    return principal + accrued_interest(bond, face, settle)
