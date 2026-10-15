from datetime import datetime, timedelta


class FakeClock:
    """Naive UTC."""

    def __init__(self, now: datetime):
        self.current = now

    def now(self) -> datetime:
        return self.current

    def advance(self, seconds: float) -> None:
        self.current += timedelta(seconds=seconds)
