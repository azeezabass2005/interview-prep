from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal

WEIGHTS = {"SERVER": Decimal("1.0"), "BARTENDER": Decimal("1.0"), "BUSSER": Decimal("0.5"), "HOST": Decimal("0.5")}
SERVICES = ("LUNCH", "DINNER")
CARD_FEE = Decimal("0.025")
MIN_HOURS = Decimal("1")
CENT = Decimal("0.01")


class TipError(Exception):
    pass


@dataclass
class Work:
    employee: str
    role: str
    day: date
    service: str
    hours: Decimal


class TipPool:
    def __init__(self):
        self.work = []
        self.tips = defaultdict(lambda: {"cash": Decimal("0"), "card": Decimal("0")})
        self.paid = {}

    def add_work(self, employee, role, day, service, hours):
        if service not in SERVICES:
            raise TipError("unknown service")
        self.work.append(Work(employee, role, day, service, Decimal(str(hours))))

    def add_tips(self, day, service, cash=0, card=0):
        if service not in SERVICES:
            raise TipError("unknown service")
        self.tips[(day, service)]["cash"] += Decimal(str(cash))
        self.tips[(day, service)]["card"] += Decimal(str(card))

    def pool(self, day, service):
        t = self.tips[(day, service)]
        return ((t["cash"] + t["card"]) * (1 - CARD_FEE)).quantize(CENT, rounding=ROUND_HALF_UP)

    def _points(self, day, service):
        points = defaultdict(Decimal)
        for w in self.work:
            if w.day == day and w.hours > MIN_HOURS:
                points[w.employee] += w.hours * WEIGHTS.get(w.role, Decimal("1.0"))
        return points

    def distribute(self, day, service):
        if (day, service) in self.paid:
            raise TipError("already distributed")
        pool = self.pool(day, service)
        points = self._points(day, service)
        total = sum(points.values())
        if not total:
            return {}
        shares = {e: (pool * p / total).quantize(CENT, rounding=ROUND_DOWN) for e, p in points.items()}
        leftover = int((pool - sum(shares.values())) / CENT)
        for employee in sorted(points)[:leftover]:
            shares[employee] += CENT
        self.paid[(day, service)] = shares
        return shares

    def statement(self, employee, monday):
        week = {monday + timedelta(days=i) for i in range(7)}
        return sum((s.get(employee, Decimal("0")) for (day, _), s in self.paid.items() if day in week), Decimal("0.00"))

    def remove_work(self, employee, day, service):
        if (day, service) in self.paid:
            raise TipError("pool already distributed")
        before = len(self.work)
        self.work = [w for w in self.work if not (w.employee == employee and w.day == day and w.service == service)]
        return before - len(self.work)

    def undistributed(self, until):
        pending = [(d, s) for (d, s) in self.tips if d <= until and (d, s) not in self.paid]
        return sorted(pending)

    def day_report(self, day):
        report = {}
        for service in SERVICES:
            if (day, service) in self.tips:
                shares = self.paid.get((day, service))
                report[service] = {"pool": self.pool(day, service), "distributed": shares is not None,
                                   "shares": dict(sorted(shares.items())) if shares else {}}
        return report
