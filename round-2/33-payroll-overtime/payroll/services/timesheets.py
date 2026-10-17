from collections import defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List

from ..errors import NotFound, PayrollError
from ..models import DayHours, Shift
from ..store import InMemoryStore
from .rates import rate_on

MEAL_BREAK_AFTER = Decimal(6)
MEAL_BREAK = Decimal("0.5")


def shift_hours(shift: Shift) -> Decimal:
    minutes = int((shift.end - shift.start).total_seconds() // 60)
    hours = Decimal(minutes) / 60
    if not shift.break_taken and hours >= MEAL_BREAK_AFTER:
        hours -= MEAL_BREAK
    return hours


class TimesheetService:
    def __init__(self, store: InMemoryStore):
        self._store = store

    def record(self, worker_id: str, start: datetime, end: datetime, break_taken: bool = False) -> Shift:
        if self._store.worker(worker_id) is None:
            raise NotFound(f"worker {worker_id}")
        if end <= start or end - start > timedelta(hours=24):
            raise PayrollError("shift must be between 1 minute and 24 hours")
        for other in self._store.shifts[worker_id]:
            if start < other.end and other.start < end:
                raise PayrollError("shift overlaps an existing shift")
        shift = Shift(worker_id, start, end, break_taken)
        self._store.shifts[worker_id].append(shift)
        return shift

    def week(self, worker_id: str, monday: date) -> List[DayHours]:
        worker = self._store.worker(worker_id)
        if worker is None:
            raise NotFound(f"worker {worker_id}")
        end = monday + timedelta(days=7)
        hours = defaultdict(Decimal)
        for shift in self._store.shifts[worker_id]:
            if monday <= shift.start.date() < end:
                hours[shift.end.date()] += shift_hours(shift)
        return [DayHours(day, h, rate_on(worker, day)) for day, h in sorted(hours.items())]
