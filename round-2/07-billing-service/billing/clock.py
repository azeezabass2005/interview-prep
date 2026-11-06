import time
from datetime import datetime, timedelta, timezone


class Clock:
    def now(self) -> datetime:
        raise NotImplementedError

    def monotonic(self) -> float:
        raise NotImplementedError


class SystemClock(Clock):
    def now(self) -> datetime:
        return datetime.now(timezone.utc).replace(tzinfo=None, microsecond=0)

    def monotonic(self) -> float:
        return time.monotonic()


class FixedClock(Clock):
    """A clock for tests and replays: time only moves when you advance it."""

    def __init__(self, now: datetime):
        self._now = now
        self._mono = 1000.0

    def now(self) -> datetime:
        return self._now

    def monotonic(self) -> float:
        return self._mono

    def advance(self, **delta) -> None:
        step = timedelta(**delta)
        self._now += step
        self._mono += step.total_seconds()


def iso(dt: datetime) -> str:
    return dt.isoformat(timespec="seconds")


def parse_iso(text: str) -> datetime:
    return datetime.fromisoformat(text)
