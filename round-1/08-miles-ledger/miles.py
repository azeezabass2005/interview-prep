import calendar
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

CLASS_MULTIPLIER = {"Y": Decimal("1.0"), "J": Decimal("1.5"), "F": Decimal("2.0")}
BONUS = {"BASIC": Decimal("0"), "SILVER": Decimal("0.25"), "GOLD": Decimal("0.50")}
TIERS = [(50_000, "GOLD"), (25_000, "SILVER")]
RANK = ["BASIC", "SILVER", "GOLD"]
ACTIVITY = ("FLIGHT",)
EXPIRY_MONTHS = 18
TRANSFER_LIMIT = 50_000


class MilesError(Exception):
    pass


@dataclass
class Event:
    member: str
    when: date
    kind: str
    miles: int
    base: int = 0


def add_months(d, months):
    month = d.month - 1 + months
    year, month = d.year + month // 12, month % 12 + 1
    return date(year, month, min(d.day, calendar.monthrange(year, month)[1]))


class MilesLedger:
    def __init__(self):
        self.members = set()
        self.events = []

    def join(self, member):
        self.members.add(member)

    def _events(self, member):
        if member not in self.members:
            raise MilesError(f"unknown member {member}")
        return sorted((e for e in self.events if e.member == member), key=lambda e: e.when)

    def _qualifying(self, member, year):
        return sum(e.miles for e in self._events(member) if e.kind == "FLIGHT" and e.when.year == year)

    @staticmethod
    def _level(qualifying):
        for threshold, name in TIERS:
            if qualifying >= threshold:
                return name
        return "BASIC"

    def status_on(self, member, on):
        return self._level(self._qualifying(member, on.year))

    def fly(self, member, on, distance, fare_class):
        status = self.status_on(member, on)
        base = int(distance * CLASS_MULTIPLIER[fare_class])
        bonus = int(distance * BONUS[status])
        self.events.append(Event(member, on, "FLIGHT", base + bonus, base))
        return base + bonus

    def balance(self, member, on):
        balance, last_activity = 0, None
        for e in self._events(member):
            if e.when > on:
                break
            if last_activity and e.when > add_months(last_activity, EXPIRY_MONTHS):
                balance = 0
            balance += e.miles
            if e.kind in ACTIVITY:
                last_activity = e.when
        if last_activity and on > add_months(last_activity, EXPIRY_MONTHS):
            balance = 0
        return balance

    def redeem(self, member, on, miles):
        if miles <= 0 or miles > self.balance(member, on):
            raise MilesError("not enough miles")
        self.events.append(Event(member, on, "REDEEM", -miles))

    def transfer(self, sender, receiver, on, miles):
        if receiver not in self.members or sender == receiver:
            raise MilesError("bad receiver")
        if miles <= 0 or miles > self.balance(sender, on):
            raise MilesError("not enough miles")
        if miles > TRANSFER_LIMIT:
            raise MilesError("annual transfer limit reached")
        self.events.append(Event(sender, on, "TRANSFER_OUT", -miles))
        self.events.append(Event(receiver, on, "TRANSFER_IN", miles))
