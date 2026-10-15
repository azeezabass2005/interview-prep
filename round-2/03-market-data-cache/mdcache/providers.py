from decimal import Decimal
from typing import Protocol

from .models import Quote


class ProviderError(Exception):
    pass


class QuoteProvider(Protocol):
    def fetch(self, symbol: str, timeout: float) -> Quote: ...


class VendorFeedProvider:
    """Real vendor client (HTTP). Not available in this exercise."""

    def __init__(self, base_url: str, api_key: str):
        self._base_url = base_url
        self._api_key = api_key

    def fetch(self, symbol: str, timeout: float) -> Quote:  # pragma: no cover
        raise ProviderError("vendor feed not reachable from the interview sandbox")


class ScriptedProvider:
    """Test double: returns prices from a dict and counts calls."""

    def __init__(self, clock, prices=None, fail=False):
        self._clock = clock
        self.prices = dict(prices or {})
        self.fail = fail
        self.calls = []

    def fetch(self, symbol: str, timeout: float) -> Quote:
        self.calls.append(symbol)
        if self.fail:
            raise ProviderError("vendor timeout")
        last = Decimal(self.prices[symbol])
        return Quote(symbol, last - Decimal("0.01"), last + Decimal("0.01"), last, self._clock.time())
