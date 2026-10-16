from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import List


@dataclass(frozen=True)
class RateChange:
    effective: date
    hourly: Decimal


@dataclass
class Worker:
    worker_id: str
    name: str
    rates: List[RateChange] = field(default_factory=list)


@dataclass(frozen=True)
class Shift:
    worker_id: str
    start: datetime
    end: datetime
    break_taken: bool = False


@dataclass(frozen=True)
class DayHours:
    day: date
    hours: Decimal
    rate: Decimal


@dataclass(frozen=True)
class Buckets:
    regular: Decimal
    overtime: Decimal
    double: Decimal
