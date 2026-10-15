from ..cache import TtlCache
from ..config import PROVIDER_TIMEOUT_S
from ..metrics import Metrics
from ..models import Quote
from ..providers import ProviderError
from ..repositories.history import CloseRepository


class SymbolNotFound(Exception):
    pass


class QuoteService:
    def __init__(self, provider, cache: TtlCache, closes: CloseRepository, metrics: Metrics = None):
        self._provider = provider
        self._cache = cache
        self._closes = closes
        self.metrics = metrics or Metrics()

    def get_quote(self, symbol: str) -> Quote:
        cached = self._cache.get(symbol)
        if cached is not None:
            self.metrics.incr("cache_hits")
            return cached
        self.metrics.incr("cache_misses")
        return self._fetch(symbol)

    def _fetch(self, symbol: str) -> Quote:
        try:
            self.metrics.incr("vendor_calls")
            quote = self._provider.fetch(symbol.upper(), timeout=PROVIDER_TIMEOUT_S)
        except ProviderError:
            self.metrics.incr("vendor_errors")
            return self._fallback(symbol)
        self._cache.put(symbol, quote)
        return quote

    def _fallback(self, symbol: str) -> Quote:
        close = self._closes.last_close(symbol.upper())
        if close is None:
            raise SymbolNotFound(symbol)
        price, recorded_at = close
        return Quote(symbol.upper(), price, price, price, recorded_at, stale=True)
