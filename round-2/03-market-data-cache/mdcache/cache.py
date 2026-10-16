import threading
from typing import Any, Dict, Optional, Tuple


class TtlCache:

    def __init__(self, clock, ttl_ms: int):
        self._clock = clock
        self._ttl_ms = ttl_ms
        self._entries: Dict[str, Tuple[Any, float]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._entries.get(key)
            if entry is None:
                return None
            value, expires_at = entry
            if self._clock.time() >= expires_at:
                del self._entries[key]
                return None
            return value

    def put(self, key: str, value: Any) -> None:
        with self._lock:
            self._entries[key] = (value, self._clock.time() + self._ttl_ms)

    def invalidate(self, key: str) -> None:
        with self._lock:
            self._entries.pop(key, None)

    def __len__(self) -> int:
        with self._lock:
            return len(self._entries)
