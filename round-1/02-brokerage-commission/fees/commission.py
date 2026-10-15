from decimal import ROUND_HALF_UP, Decimal

from .schedule import CENT, MIN_COMMISSION, REG_FEE_RATE, TIERS, ZERO


def tiered_commission(notional: Decimal) -> Decimal:
    """Raw commission (unrounded) for a notional, using the tier table."""
    for upper, rate in TIERS:
        if upper is None or notional <= upper:
            return notional * rate
    raise AssertionError("unreachable: last tier is unbounded")


def commission_for(notional: Decimal) -> Decimal:
    if notional <= 0:
        raise ValueError("notional must be positive")
    fee = tiered_commission(notional).quantize(CENT, rounding=ROUND_HALF_UP)
    return max(fee, MIN_COMMISSION)


def regulatory_fee(side: str, notional: Decimal) -> Decimal:
    if side != "SELL":
        return ZERO
    return (notional * REG_FEE_RATE).quantize(CENT, rounding=ROUND_HALF_UP)
