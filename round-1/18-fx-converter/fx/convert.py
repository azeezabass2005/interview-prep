from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from .currencies import minor_units
from .rates import RateBook

SPREAD_TIERS = [  # (USD equivalent upper bound, spread)
    (Decimal("10000"), Decimal("0.0100")),
    (Decimal("100000"), Decimal("0.0050")),
    (None, Decimal("0.0025")),
]


@dataclass(frozen=True)
class Quote:
    source_currency: str
    source_amount: Decimal
    target_currency: str
    target_amount: Decimal
    mid_rate: Decimal
    spread: Decimal


def spread_for(usd_equivalent: Decimal) -> Decimal:
    for upper, spread in SPREAD_TIERS:
        if upper is None or usd_equivalent < upper:
            return spread
    raise AssertionError("unreachable")


class Converter:
    def __init__(self, rates: RateBook):
        self._rates = rates

    def quote(self, amount: Decimal, source: str, target: str) -> Quote:
        if amount <= 0:
            raise ValueError("amount must be positive")
        source_usd = self._rates.usd_per_unit(source)
        target_usd = self._rates.usd_per_unit(target)
        mid = source_usd / target_usd
        spread = spread_for(amount)
        raw = amount * mid * (1 - spread)
        exponent = Decimal(1).scaleb(-minor_units(target))
        return Quote(source, amount, target, raw.quantize(exponent, rounding=ROUND_HALF_UP), mid, spread)
