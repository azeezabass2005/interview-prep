from decimal import ROUND_HALF_UP, ROUND_UP, Decimal

CENT = Decimal("0.01")
ZERO = Decimal("0.00")


def half_up(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def always_up(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_UP)


def clamp(value: Decimal, low: Decimal, high=None) -> Decimal:
    value = max(value, low)
    if high is not None:
        value = min(value, high)
    return value
