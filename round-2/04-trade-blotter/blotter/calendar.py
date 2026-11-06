from datetime import date, datetime, timedelta

from .config import BUSINESS_UTC_OFFSET_HOURS


def business_date(utc_now: datetime) -> date:
    """The New York business date for a UTC timestamp."""
    return (utc_now + timedelta(hours=BUSINESS_UTC_OFFSET_HOURS)).date()
