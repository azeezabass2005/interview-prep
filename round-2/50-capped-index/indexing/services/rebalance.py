from datetime import date
from decimal import Decimal
from typing import Dict

from ..errors import IndexError_
from ..models import IndexDefinition, Security
from ..store import InMemoryStore
from .eligibility import is_eligible
from .weighting import apply_cap, publish, raw_weights


def turnover(old: Dict[str, Decimal], new: Dict[str, Decimal]) -> Decimal:
    names = set(old) | set(new)
    return sum((abs(new.get(n, Decimal(0)) - old.get(n, Decimal(0))) for n in names), Decimal(0)) / 2


class RebalanceService:
    def __init__(self, store: InMemoryStore):
        self._store = store

    def add_security(self, s: Security) -> None:
        self._store.universe[s.ticker] = s

    def define(self, name: str, cap) -> IndexDefinition:
        cap = Decimal(str(cap))
        if not Decimal(0) < cap <= 1:
            raise IndexError_("cap must be in (0, 1]")
        d = IndexDefinition(name, cap)
        self._store.indices[name] = d
        return d

    def rebalance(self, name: str, on: date) -> dict:
        d = self._store.indices.get(name)
        if d is None:
            raise IndexError_(f"unknown index {name}")
        eligible = [s for s in self._store.universe.values() if is_eligible(s, on)]
        if not eligible:
            raise IndexError_("no eligible securities")
        if len(eligible) * d.cap < 1:
            raise IndexError_("too few constituents for the cap")
        weights = publish(apply_cap(raw_weights(eligible), d.cap), d.cap)
        previous = d.history[-1] if d.history else {}
        d.history.append(weights)
        return {"weights": weights, "turnover": turnover(previous, weights)}
