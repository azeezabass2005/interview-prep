from decimal import ROUND_HALF_UP, Decimal
from typing import Dict, Iterable, List

from .models import Security

MIN_FREE_FLOAT = Decimal("0.15")
MIN_PRICE = Decimal("1.00")
MIN_MARKET_CAP = Decimal("500000000")
PRODUCTION_CAP = Decimal("0.10")
PLACES = Decimal("0.0001")
HUNDRED = Decimal(100)


def is_eligible(s: Security) -> bool:
    return (s.free_float > MIN_FREE_FLOAT
            and s.price > MIN_PRICE
            and s.shares * s.price >= MIN_MARKET_CAP)


def float_adjusted_cap(s: Security) -> Decimal:
    return s.shares * s.price


def raw_weights(securities: Iterable[Security]) -> Dict[str, Decimal]:
    caps = {s.ticker: float_adjusted_cap(s) for s in securities if is_eligible(s)}
    total = sum(caps.values(), Decimal(0))
    if total == 0:
        return {}
    return {t: c / total for t, c in caps.items()}


def apply_cap(weights: Dict[str, Decimal], cap: Decimal) -> Dict[str, Decimal]:
    w = dict(weights)
    over: List[str] = [t for t, v in w.items() if v > cap]
    excess = sum((w[t] - cap for t in over), Decimal(0))
    for t in over:
        w[t] = cap
    under = [t for t in w if t not in over]
    for t in under:
        w[t] += excess / len(under)
    return w


def publish(securities: Iterable[Security], cap: Decimal = PRODUCTION_CAP) -> Dict[str, Decimal]:
    capped = apply_cap(raw_weights(securities), cap)
    return {t: (v * HUNDRED).quantize(PLACES, rounding=ROUND_HALF_UP) for t, v in capped.items()}
