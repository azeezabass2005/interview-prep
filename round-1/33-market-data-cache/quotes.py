from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal

TTL = timedelta(seconds=5)
STALE_LIMIT = timedelta(seconds=60)


class VendorError(Exception):
    pass


@dataclass(frozen=True)
class Quote:
    symbol: str
    price: Decimal
    timestamp: datetime
    stale: bool = False


@dataclass
class Entry:
    quote: Quote
    fetched_at: datetime


class QuoteCache:
    def __init__(self, vendor, clock, capacity=1000):
        self.vendor = vendor
        self.clock = clock
        self.capacity = capacity
        self.entries = OrderedDict()
        self.hits = 0
        self.misses = 0

    @staticmethod
    def _key(symbol):
        return symbol.strip()

    def get(self, symbol):
        key = self._key(symbol)
        now = self.clock.now()
        entry = self.entries.get(key)
        if entry and now - entry.fetched_at <= TTL:
            self.hits += 1
            return entry.quote
        self.misses += 1
        try:
            quote = self.vendor.fetch(key)
        except VendorError:
            if entry:
                return Quote(entry.quote.symbol, entry.quote.price, entry.quote.timestamp, stale=True)
            raise
        self.entries[key] = Entry(quote, quote.timestamp)
        self.entries.move_to_end(key)
        while len(self.entries) > self.capacity:
            self.entries.popitem(last=False)
        return quote

    def get_many(self, symbols):
        results, errors = {}, {}
        for symbol in dict.fromkeys(self._key(s) for s in symbols):
            try:
                results[symbol] = self.get(symbol)
            except VendorError as exc:
                errors[symbol] = str(exc)
        return results, errors

    def invalidate(self, symbol):
        return self.entries.pop(self._key(symbol), None) is not None

    def purge(self):
        now = self.clock.now()
        old = [k for k, e in self.entries.items() if now - e.fetched_at >= STALE_LIMIT]
        for k in old:
            del self.entries[k]
        return len(old)

    def stats(self):
        total = self.hits + self.misses
        ratio = round(self.hits / total, 4) if total else 0.0
        return {"hits": self.hits, "misses": self.misses, "hit_ratio": ratio, "size": len(self.entries)}
