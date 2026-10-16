from decimal import Decimal

from ..config import RATE_MAX_AGE
from ..errors import FxError, Rejected
from ..store import InMemoryStore


class RateBook:
    def __init__(self, store: InMemoryStore, clock):
        self._store = store
        self._clock = clock

    def publish(self, pair: str, rate) -> None:
        if len(pair) != 6 or "USD" not in (pair[:3], pair[3:]):
            raise FxError("pairs must be quoted against USD")
        self._store.rates[pair] = (Decimal(str(rate)), self._clock.now())

    def usd_per_unit(self, currency: str) -> Decimal:
        if currency == "USD":
            return Decimal(1)
        for pair, (rate, at) in self._store.rates.items():
            base, quote = pair[:3], pair[3:]
            if currency not in (base, quote):
                continue
            if self._clock.now() - at > RATE_MAX_AGE:
                raise Rejected(f"{pair} rate is stale")
            return rate
        raise FxError(f"no rate for {currency}")
