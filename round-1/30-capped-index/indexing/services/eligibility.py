from datetime import date

from ..config import MIN_FREE_FLOAT, MIN_LISTED_DAYS, MIN_MARKET_CAP, MIN_PRICE
from ..models import Security


def is_eligible(s: Security, on: date) -> bool:
    return (s.free_float > MIN_FREE_FLOAT
            and s.price > MIN_PRICE
            and s.shares * s.price >= MIN_MARKET_CAP
            and (on - s.listed_on).days > MIN_LISTED_DAYS)
