from decimal import Decimal

from ..errors import NotFound
from ..store import InMemoryStore


class PriceService:
    def __init__(self, store: InMemoryStore):
        self._store = store

    def set(self, symbol: str, price) -> None:
        self._store.prices[symbol] = Decimal(str(price))

    def get(self, symbol: str) -> Decimal:
        if symbol not in self._store.prices:
            raise NotFound(f"no price for {symbol}")
        return self._store.prices[symbol]
