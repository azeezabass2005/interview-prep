from dataclasses import dataclass
from decimal import ROUND_DOWN, Decimal

MIN_FLOAT = Decimal("0.15")
MIN_PRICE = Decimal("1.00")
MIN_CAP = Decimal("500000000")
PLACES = Decimal("0.0001")
HUNDRED = Decimal(100)


class IndexError_(Exception):
    pass


@dataclass(frozen=True)
class Stock:
    ticker: str
    shares: int
    free_float: Decimal
    price: Decimal


def eligible(stocks):
    return [s for s in stocks
            if s.free_float >= MIN_FLOAT and s.price >= MIN_PRICE and s.shares * s.price >= MIN_CAP]


def raw_weights(stocks):
    caps = {s.ticker: s.shares * s.price for s in stocks}
    total = sum(caps.values())
    return {t: c / total for t, c in caps.items()}


def apply_cap(weights, cap):
    w = dict(weights)
    over = [t for t, v in w.items() if v > cap]
    excess = sum((w[t] - cap for t in over), Decimal(0))
    for t in over:
        w[t] = cap
    rest = {t: v for t, v in w.items() if t not in over}
    base = sum(rest.values())
    for t, v in rest.items():
        w[t] = v + excess * v / base
    return w


def publish(weights, cap):
    published = {t: (v * HUNDRED).quantize(PLACES, rounding=ROUND_DOWN) for t, v in weights.items()}
    residue = HUNDRED - sum(published.values())
    if residue:
        target = sorted(published, key=lambda t: (-published[t], t))[0]
        published[target] += residue
    return published


def turnover(old, new):
    return sum((abs(new[t] - old.get(t, Decimal(0))) for t in new), Decimal(0)) / 2


class IndexCalculator:
    def __init__(self, cap):
        self.cap = Decimal(str(cap))
        self.history = []

    def rebalance(self, universe):
        members = eligible(universe)
        if not members or len(members) * self.cap < 1:
            raise IndexError_("not enough eligible stocks for the cap")
        weights = publish(apply_cap(raw_weights(members), self.cap), self.cap)
        previous = self.history[-1] if self.history else None
        self.history.append(weights)
        return {"weights": weights, "turnover": turnover(previous, weights) if previous else Decimal(0)}

    def constituents(self):
        return sorted(self.history[-1]) if self.history else []

    def changes(self):
        if len(self.history) < 2:
            return {"added": self.constituents(), "removed": []}
        old, new = self.history[-2], self.history[-1]
        return {"added": sorted(set(new) - set(old)), "removed": sorted(set(old) - set(new))}

    def capped(self):
        if not self.history:
            return []
        limit = self.cap * HUNDRED
        return sorted(t for t, w in self.history[-1].items() if w >= limit)
