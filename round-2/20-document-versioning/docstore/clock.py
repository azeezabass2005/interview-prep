from datetime import datetime, timedelta


class FakeClock:
    def __init__(self, now: datetime):
        self.current = now

    def now(self) -> datetime:
        self.current += timedelta(seconds=1)
        return self.current
