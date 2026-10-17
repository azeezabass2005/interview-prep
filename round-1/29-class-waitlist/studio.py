from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List

MAX_WAITLIST = 5
LATE_WINDOW = timedelta(hours=12)
NO_PROMOTION = timedelta(hours=1)
LATE_FEE = Decimal("10.00")
PLANS = ("UNLIMITED", "PACK")


class StudioError(Exception):
    pass


@dataclass
class Member:
    name: str
    plan: str
    credits: int = 0
    fees: Decimal = Decimal("0.00")


@dataclass
class FitnessClass:
    starts_at: datetime
    capacity: int
    booked: List[str] = field(default_factory=list)
    waitlist: List[str] = field(default_factory=list)


class Studio:
    def __init__(self, clock):
        self.clock = clock
        self.members = {}
        self.classes = {}

    def join(self, name, plan, credits=0):
        if plan not in PLANS:
            raise StudioError("unknown plan")
        self.members[name] = Member(name, plan, credits if plan == "PACK" else 0)

    def add_class(self, class_id, starts_at, capacity):
        self.classes[class_id] = FitnessClass(starts_at, capacity)

    def book(self, class_id, name):
        c, m = self.classes[class_id], self.members[name]
        if name in c.booked:
            raise StudioError("already booked")
        if m.plan == "PACK" and m.credits < 1:
            raise StudioError("no credits")
        if len(c.booked) < c.capacity:
            c.booked.append(name)
            if m.plan == "PACK":
                m.credits -= 1
            return "BOOKED"
        if len(c.waitlist) >= MAX_WAITLIST:
            raise StudioError("waitlist full")
        c.waitlist.append(name)
        return "WAITLISTED"

    def cancel(self, class_id, name):
        c, m = self.classes[class_id], self.members[name]
        if name in c.waitlist:
            c.waitlist.remove(name)
            return Decimal("0.00")
        if name not in c.booked:
            raise StudioError("no place to cancel")
        c.booked.remove(name)
        late = c.starts_at - self.clock.now() <= LATE_WINDOW
        fee = Decimal("0.00")
        if late and m.plan == "UNLIMITED":
            fee = LATE_FEE
            m.fees += fee
        self._promote(c)
        return fee

    def _promote(self, c):
        if not c.waitlist or len(c.booked) >= c.capacity:
            return
        name = c.waitlist.pop()
        m = self.members[name]
        if m.plan == "PACK":
            m.credits -= 1
        c.booked.append(name)
