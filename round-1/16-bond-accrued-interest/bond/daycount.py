from datetime import date


def days_30_360(start: date, end: date) -> int:
    d1, d2 = start.day, end.day
    if d1 == 31:
        d1 = 30
    if d2 == 31:
        d2 = 30
    return 360 * (end.year - start.year) + 30 * (end.month - start.month) + (d2 - d1)
