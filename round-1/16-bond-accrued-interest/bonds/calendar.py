import calendar
from datetime import date, timedelta
from typing import Iterable


def last_day(year: int, month: int) -> int:
    return calendar.monthrange(year, month)[1]


def is_month_end(d: date) -> bool:
    return d.day == last_day(d.year, d.month)


def shift_months(d: date, months: int) -> date:
    index = d.year * 12 + d.month - 1 + months
    year, month = divmod(index, 12)
    month += 1
    return date(year, month, min(d.day, last_day(year, month)))


class BusinessCalendar:
    def __init__(self, holidays: Iterable[date] = ()):
        self.holidays = set(holidays)

    def add_holiday(self, d: date) -> None:
        self.holidays.add(d)

    def is_business_day(self, d: date) -> bool:
        return d.weekday() < 5

    def add_business_days(self, d: date, n: int) -> date:
        while n > 0:
            d += timedelta(days=1)
            if self.is_business_day(d):
                n -= 1
        return d
