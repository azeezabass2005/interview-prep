import threading
from collections import defaultdict

from .repositories.counters import CounterRepository


class LocalCounterStore:

    def __init__(self):
        self._counts = defaultdict(int)
        self._lock = threading.Lock()

    def increment(self, bucket: str, window_start: int) -> int:
        with self._lock:
            self._counts[(bucket, window_start)] += 1
            return self._counts[(bucket, window_start)]


class DbCounterStore:

    def __init__(self, repo: CounterRepository):
        self._repo = repo

    def increment(self, bucket: str, window_start: int) -> int:
        return self._repo.increment(bucket, window_start)
