from typing import Dict, Optional

from .config import FLAG_CACHE_TTL_SECONDS
from .models import Flag
from .repositories.flags import FlagRepository


class FlagCache:
    """Per-process snapshot of all flags, refreshed at most every TTL seconds."""

    def __init__(self, repo: FlagRepository, clock, ttl_seconds: float = FLAG_CACHE_TTL_SECONDS):
        self._repo = repo
        self._clock = clock
        self._ttl = ttl_seconds
        self._flags: Dict[str, Flag] = {}
        self._loaded_at: Optional[float] = None

    def get(self, key: str) -> Optional[Flag]:
        now = self._clock.time()
        if self._loaded_at is None or now - self._loaded_at >= self._ttl:
            self._flags = self._repo.load_all()
            self._loaded_at = now
        return self._flags.get(key)

    def invalidate(self) -> None:
        self._loaded_at = None
