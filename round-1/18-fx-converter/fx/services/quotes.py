import uuid
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from ..config import MINOR_UNITS, SPREAD_TIERS
from ..errors import FxError
from ..models import Quote
from ..store import InMemoryStore
from .rates import RateBook


def spread_for(usd_equivalent: Decimal) -> Decimal:
    for upper, spread in SPREAD_TIERS:
        if upper is None or usd_equivalent < upper:
            return spread
    raise AssertionError("unreachable")


class QuoteService:
    def __init__(self, store: InMemoryStore, rates: RateBook, clock):
        self._store = store
        self._rates = rates
        self._clock = clock

    def quote(self, customer: str, source: str, amount, target: str) -> Quote:
        if source not in MINOR_UNITS or target not in MINOR_UNITS or source == target:
            raise FxError("unsupported currency pair")
        try:
            amount = Decimal(str(amount))
        except InvalidOperation:
            raise FxError("amount must be a number")
        if amount <= 0:
            raise FxError("amount must be positive")
        source_usd = self._rates.usd_per_unit(source)
        mid = source_usd / self._rates.usd_per_unit(target)
        usd_equivalent = amount * source_usd
        spread = spread_for(amount)
        unit = Decimal(1).scaleb(-MINOR_UNITS[target])
        target_amount = (amount * mid * (1 - spread)).quantize(unit, rounding=ROUND_HALF_UP)
        q = Quote(f"q-{uuid.uuid4().hex[:8]}", customer, source, amount, target, target_amount, mid, spread,
                  usd_equivalent, self._clock.now())
        self._store.quotes[q.quote_id] = q
        return q
