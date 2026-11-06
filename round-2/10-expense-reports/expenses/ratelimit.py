from dataclasses import dataclass


@dataclass
class Decision:
    allowed: bool
    remaining: int
    retry_after: int


class FixedWindowLimiter:
    """At most `limit` requests per key in each fixed window of `window_seconds`."""

    def __init__(self, clock, limit: int, window_seconds: int):
        self._clock = clock
        self.limit = limit
        self.window = window_seconds
        self._windows: dict[str, tuple[int, int]] = {}

    def check(self, key: str) -> Decision:
        now = self._clock.now().timestamp()
        window_start = int(now // self.window) * self.window
        start, count = self._windows.get(key, (window_start, 0))
        if start != window_start:
            start, count = window_start, 0
        if count >= self.limit:
            return Decision(False, 0, max(1, int(start + self.window - now)))
        count += 1
        self._windows[key] = (start, count)
        return Decision(True, self.limit - count, 0)
