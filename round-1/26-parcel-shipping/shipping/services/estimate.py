from datetime import date, datetime, timedelta

from ..config import CARRIERS, CUTOFF_HOUR


def next_business_day(d: date) -> date:
    d += timedelta(days=1)
    while d.weekday() >= 5:
        d += timedelta(days=1)
    return d


def ship_date(ordered_at: datetime) -> date:
    d = ordered_at.date()
    if d.weekday() >= 5 or ordered_at.hour > CUTOFF_HOUR:
        return next_business_day(d)
    return d


def delivery_date(ordered_at: datetime, carrier: str) -> date:
    d = ship_date(ordered_at)
    for _ in range(CARRIERS[carrier]["transit_days"]):
        d = next_business_day(d)
    return d
