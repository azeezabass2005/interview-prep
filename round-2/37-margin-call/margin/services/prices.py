from datetime import date
from decimal import Decimal

from ..errors import MarginError
from ..models import Price
from ..store import InMemoryStore


class PriceService:
    def __init__(self, store: InMemoryStore):
        self._store = store

    def publish(self, symbol: str, on: date, price) -> Price:
        p = Price(symbol, on, Decimal(str(price)))
        self._store.prices[symbol].append(p)
        return p

    def latest(self, symbol: str, as_of: date) -> Price:
        candidates = [p for p in self._store.prices.get(symbol, []) if p.on <= as_of]
        if not candidates:
            raise MarginError(f"no price for {symbol}")
        return max(candidates, key=lambda p: p.on)
