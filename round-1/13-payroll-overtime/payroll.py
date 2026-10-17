from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal

BREAK_AFTER = Decimal("6")
BREAK_HOURS = Decimal("0.5")
DAILY_REGULAR = Decimal("8")
DAILY_DOUBLE = Decimal("12")
WEEKLY_REGULAR = Decimal("40")
OVERTIME = Decimal("1.5")
DOUBLE = Decimal("2")
CENT = Decimal("0.01")


class PayrollError(Exception):
    pass


@dataclass
class Shift:
    employee: str
    start: datetime
    end: datetime


class Payroll:
    def __init__(self):
        self.rates = {}
        self.shifts = []

    def set_rate(self, employee, effective, rate):
        self.rates.setdefault(employee, []).append((effective, Decimal(str(rate))))

    def rate_on(self, employee, day):
        history = self.rates.get(employee)
        if not history:
            raise PayrollError(f"no rate for {employee}")
        return history[-1][1]

    def add_shift(self, employee, start, end):
        if end <= start:
            raise PayrollError("shift must end after it starts")
        for s in self.shifts:
            if s.employee == employee and start < s.end and s.start < end:
                raise PayrollError("overlapping shift")
        self.shifts.append(Shift(employee, start, end))

    @staticmethod
    def _hours(shift):
        hours = Decimal(int((shift.end - shift.start).total_seconds() // 60)) / 60
        if hours >= BREAK_AFTER:
            hours -= BREAK_HOURS
        return hours

    def week(self, employee, monday):
        if monday.weekday() != 0:
            raise PayrollError("weeks start on Monday")
        days = defaultdict(Decimal)
        for s in self.shifts:
            day = s.end.date()
            if s.employee == employee and monday <= day < monday + timedelta(days=7):
                days[day] += self._hours(s)
        totals = {"regular": Decimal(0), "overtime": Decimal(0), "double": Decimal(0), "gross": Decimal(0)}
        weekly_hours = Decimal(0)
        for day in sorted(days):
            hours = days[day]
            regular = min(hours, DAILY_REGULAR)
            overtime = max(hours - DAILY_REGULAR, Decimal(0))
            double = Decimal(0)
            weekly_hours += hours
            excess = max(Decimal(0), min(regular, weekly_hours - WEEKLY_REGULAR))
            regular -= excess
            overtime += excess
            rate = self.rate_on(employee, day)
            totals["regular"] += regular
            totals["overtime"] += overtime
            totals["double"] += double
            totals["gross"] += rate * (regular + overtime * OVERTIME + double * DOUBLE)
        totals["gross"] = totals["gross"].quantize(CENT, rounding=ROUND_HALF_UP)
        return totals
