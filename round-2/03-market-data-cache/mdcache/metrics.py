import threading
from collections import Counter


class Metrics:

    def __init__(self):
        self._lock = threading.Lock()
        self._counts = Counter()

    def incr(self, name: str, by: int = 1) -> None:
        with self._lock:
            self._counts[name] += by

    def get(self, name: str) -> int:
        with self._lock:
            return self._counts[name]

    def snapshot(self) -> dict:
        with self._lock:
            return dict(self._counts)
