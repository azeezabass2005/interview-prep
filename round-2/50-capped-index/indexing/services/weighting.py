from decimal import ROUND_HALF_UP, Decimal
from typing import Dict, Iterable

from ..config import PLACES
from ..models import Security

HUNDRED = Decimal(100)


def float_cap(s: Security) -> Decimal:
    return s.shares * s.price


def raw_weights(securities: Iterable[Security]) -> Dict[str, Decimal]:
    caps = {s.ticker: float_cap(s) for s in securities}
    total = sum(caps.values(), Decimal(0))
    return {t: c / total for t, c in caps.items()} if total else {}


def apply_cap(weights: Dict[str, Decimal], cap: Decimal) -> Dict[str, Decimal]:
    w = dict(weights)
    over = [t for t, v in w.items() if v > cap]
    excess = sum((w[t] - cap for t in over), Decimal(0))
    for t in over:
        w[t] = cap
    under = [t for t in w if t not in over]
    for t in under:
        w[t] += excess / len(under)
    return w


def publish(weights: Dict[str, Decimal], cap: Decimal) -> Dict[str, Decimal]:
    published = {t: (v * HUNDRED).quantize(PLACES, rounding=ROUND_HALF_UP) for t, v in weights.items()}
    if published:
        residue = HUNDRED - sum(published.values())
        uncapped = [t for t, v in weights.items() if v < cap] or list(published)
        target = sorted(uncapped, key=lambda t: (-published[t], t))[0]
        published[target] += residue
    return published
