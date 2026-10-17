from datetime import date, datetime, timedelta
from decimal import Decimal

from ..config import SERVICES
from ..models import Shift


def window(day: date, service: str):
    start_t, end_t = SERVICES[service]
    start = datetime.combine(day, start_t)
    end = datetime.combine(day, end_t) if end_t else datetime.combine(day + timedelta(days=1), datetime.min.time())
    return start, end


def hours_in_service(shift: Shift, day: date, service: str) -> Decimal:
    start, end = window(day, service)
    if not (start <= shift.start < end):
        return Decimal(0)
    minutes = int((shift.end - shift.start).total_seconds() // 60)
    return Decimal(minutes) / 60
