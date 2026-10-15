import calendar
from datetime import date, timedelta


def last_day_of_month(year: int, month: int) -> int:
    return calendar.monthrange(year, month)[1]


def is_month_end(d: date) -> bool:
    return d.day == last_day_of_month(d.year, d.month)


def add_months(d: date, months: int) -> date:
    """Shift by whole months, clamping the day to the target month's length."""
    index = d.year * 12 + (d.month - 1) + months
    year, month = divmod(index, 12)
    month += 1
    return date(year, month, min(d.day, last_day_of_month(year, month)))


def add_business_days(d: date, days: int) -> date:
    return d + timedelta(days=days)
