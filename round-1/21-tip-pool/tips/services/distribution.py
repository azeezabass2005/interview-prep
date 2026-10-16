from decimal import ROUND_DOWN, Decimal
from typing import Dict

CENT = Decimal("0.01")


def shares(pool: Decimal, weights: Dict[str, Decimal]) -> Dict[str, Decimal]:
    total = sum(weights.values(), Decimal(0))
    if total == 0:
        return {}
    exact = {n: pool * w / total for n, w in weights.items()}
    result = {n: v.quantize(CENT, rounding=ROUND_DOWN) for n, v in exact.items()}
    leftover = int((pool - sum(result.values())) / CENT)
    for name in sorted(result, key=lambda n: (-(exact[n] - result[n]), n))[:leftover]:
        result[name] += CENT
    return result
