from datetime import date, timedelta
from typing import Iterable

US_HOLIDAYS_2026 = [
    date(2026, 1, 1), date(2026, 1, 19), date(2026, 2, 16), date(2026, 4, 3), date(2026, 5, 25),
    date(2026, 6, 19), date(2026, 7, 3), date(2026, 9, 7), date(2026, 11, 26), date(2026, 12, 25),
]


class BusinessCalendar:
    def __init__(self, holidays: Iterable[date] = US_HOLIDAYS_2026):
        self.holidays = set(holidays)

    def is_business_day(self, d: date) -> bool:
        return d.weekday() < 5 and d not in self.holidays

    def roll_forward(self, d: date) -> date:
        while not self.is_business_day(d):
            d += timedelta(days=1)
        return d

    def add_business_days(self, d: date, n: int) -> date:
        while n > 0:
            d += timedelta(days=1)
            if self.is_business_day(d):
                n -= 1
        return d
