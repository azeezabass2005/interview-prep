from datetime import date, timedelta
from typing import Iterable


class LibraryCalendar:
    def __init__(self, holidays: Iterable[date] = ()):
        self.holidays = set(holidays)

    def is_open(self, d: date) -> bool:
        return d not in self.holidays

    def next_open(self, d: date) -> date:
        while not self.is_open(d):
            d += timedelta(days=1)
        return d

    def open_days_after(self, start: date, end: date) -> int:
        """Open days in (start, end]."""
        count, d = 0, start + timedelta(days=1)
        while d <= end:
            if self.is_open(d):
                count += 1
            d += timedelta(days=1)
        return count
