from datetime import datetime, timedelta
from typing import Iterable, Iterator, Optional, Tuple

from ..config import SLOT_MINUTES, WORKDAY_END_HOUR, WORKDAY_START_HOUR

Interval = Tuple[datetime, datetime]


def overlaps(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> bool:
    return a_start <= b_end and b_start <= a_end


def workday_bounds(day: datetime) -> Interval:
    start = day.replace(hour=WORKDAY_START_HOUR, minute=0, second=0, microsecond=0)
    end = day.replace(hour=WORKDAY_END_HOUR, minute=0, second=0, microsecond=0)
    return start, end


def _align_up(t: datetime) -> datetime:
    t = t.replace(second=0, microsecond=0)
    remainder = t.minute % SLOT_MINUTES
    return t if remainder == 0 else t + timedelta(minutes=SLOT_MINUTES - remainder)


def candidate_starts(day: datetime, earliest: datetime, latest: datetime, duration: timedelta) -> Iterator[datetime]:
    day_start, day_end = workday_bounds(day)
    start = _align_up(max(day_start, earliest))
    last_end = min(day_end, latest)
    while start + duration <= last_end:
        yield start
        start += timedelta(minutes=SLOT_MINUTES)


def first_free_slot(day: datetime, earliest: datetime, latest: datetime, duration: timedelta,
                    busy: Iterable[Interval]) -> Optional[Interval]:
    busy = list(busy)
    for start in candidate_starts(day, earliest, latest, duration):
        end = start + duration
        if not any(overlaps(start, end, b_start, b_end) for b_start, b_end in busy):
            return start, end
    return None
