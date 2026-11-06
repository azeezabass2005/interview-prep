import calendar
from datetime import date, datetime


def bounds(period: str) -> tuple[datetime, datetime]:
    """'2026-06' -> (2026-06-01T00:00, 2026-07-01T00:00): start inclusive, end exclusive."""
    year, month = (int(p) for p in period.split("-"))
    start = datetime(year, month, 1)
    end = datetime(year + month // 12, month % 12 + 1, 1)
    return start, end


def days_in_month(d: date) -> int:
    return calendar.monthrange(d.year, d.month)[1]


def period_of(d: date) -> str:
    return f"{d.year:04d}-{d.month:02d}"
