from datetime import timedelta


class TTLCache:
    """In-process cache with a per-entry time to live (seconds)."""

    def __init__(self, clock, ttl_seconds: float, max_entries: int = 10_000):
        self._clock = clock
        self._ttl = ttl_seconds
        self._max = max_entries
        self._entries: dict = {}
        self.hits = 0
        self.misses = 0

    def get(self, key):
        entry = self._entries.get(key)
        if entry is None or entry[1] <= self._clock.now():
            self._entries.pop(key, None)
            self.misses += 1
            return None
        self.hits += 1
        return entry[0]

    def set(self, key, value, ttl_seconds: float | None = None) -> None:
        if len(self._entries) >= self._max:
            self._entries.pop(next(iter(self._entries)))
        ttl = self._ttl if ttl_seconds is None else ttl_seconds
        self._entries[key] = (value, self._clock.now() + timedelta(seconds=ttl))

    def delete(self, key) -> None:
        self._entries.pop(key, None)

    def delete_prefix(self, prefix: str) -> None:
        for key in [k for k in self._entries if isinstance(k, str) and k.startswith(prefix)]:
            del self._entries[key]

    def clear(self) -> None:
        self._entries.clear()
