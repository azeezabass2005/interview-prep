from collections import deque

from .ratelimit import Decision


class SlidingWindowLimiter:
    """At most `limit` requests per key in any `window`-second period (a sliding log of request times)."""

    def __init__(self, clock, limit: int, window: float):
        self._clock = clock
        self.limit = limit
        self.window = window
        self._logs: dict[str, deque] = {}

    def check(self, key: str) -> Decision:
        now = self._clock.monotonic()
        log = self._logs.setdefault(key, deque())
        while log and log[0] <= now - self.window:
            log.popleft()
        log.append(now)
        if len(log) > self.limit:
            return Decision(False, 0, max(1, int(log[0] + self.window - now)))
        return Decision(True, self.limit - len(log), 0)
