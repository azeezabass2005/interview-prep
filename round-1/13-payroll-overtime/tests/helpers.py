from datetime import datetime, timedelta

from payroll.models import Shift

MONDAY = datetime(2026, 3, 2)


def shift(day, start_hour, hours, start_minute=0):
    start = MONDAY + timedelta(days=day, hours=start_hour, minutes=start_minute)
    return Shift(start, start + timedelta(hours=hours))
