FIXES = [
    ("mdcache/cache.py", "self._entries[key] = (value, self._clock.time() + self._ttl_ms)",
     "self._entries[key] = (value, self._clock.time() + self._ttl_ms / 1000)"),
    ("mdcache/services/consolidation.py", "fresh = [q for q in quotes if q.timestamp - now <= VENUE_MAX_AGE_S]",
     "fresh = [q for q in quotes if now - q.timestamp <= VENUE_MAX_AGE_S]"),
    ("mdcache/api/handlers.py", "from datetime import datetime", "from datetime import datetime, timezone"),
    ("mdcache/api/handlers.py", "datetime.fromtimestamp(epoch_seconds).strftime", "datetime.fromtimestamp(epoch_seconds, tz=timezone.utc).strftime"),
    ("mdcache/services/quotes.py", "from ..cache import TtlCache", "import threading\n\nfrom ..cache import TtlCache"),
    ("mdcache/services/quotes.py", "        self.metrics = metrics or Metrics()\n",
     "        self.metrics = metrics or Metrics()\n        self._locks = {}\n        self._locks_guard = threading.Lock()\n\n"
     "    def _lock_for(self, symbol: str) -> threading.Lock:\n        with self._locks_guard:\n"
     "            return self._locks.setdefault(symbol, threading.Lock())\n"),
    ("mdcache/services/quotes.py",
     "        self.metrics.incr(\"cache_misses\")\n        return self._fetch(symbol)",
     "        self.metrics.incr(\"cache_misses\")\n        with self._lock_for(symbol):\n"
     "            cached = self._cache.get(symbol)\n            if cached is not None:\n                return cached\n"
     "            return self._fetch(symbol)"),
]
