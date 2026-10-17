import itertools
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Tuple

HOLD_FOR = timedelta(minutes=10)
FEE = Decimal("4.50")
MAX_PER_CUSTOMER = 8
REFUND_CUTOFF = timedelta(hours=48)
PRICES = [("C", Decimal("120.00")), ("J", Decimal("80.00"))]
OTHER_PRICE = Decimal("50.00")


class BoxOfficeError(Exception):
    pass


@dataclass
class Hold:
    hold_id: int
    customer: str
    seats: Tuple[str, ...]
    expires_at: datetime


@dataclass
class Order:
    order_id: int
    customer: str
    seats: Tuple[str, ...]
    total: Decimal
    refunded: bool = False


def parse(seat):
    match = re.fullmatch(r"([A-Z])(\d+)", seat)
    if not match:
        raise BoxOfficeError(f"bad seat {seat}")
    return match.group(1), int(match.group(2))


def price(seat):
    row, _ = parse(seat)
    for last_row, amount in PRICES:
        if row < last_row:
            return amount
    return OTHER_PRICE


class BoxOffice:
    def __init__(self, show_at, seats_per_row=10):
        self.show_at = show_at
        self.seats_per_row = seats_per_row
        self.holds = {}
        self.orders = {}
        self._ids = itertools.count(1)

    def _sold(self):
        return {s for o in self.orders.values() if not o.refunded for s in o.seats}

    def _held(self, now):
        return {s for h in self.holds.values() for s in h.seats}

    def _gap(self, taken, seats):
        for seat in seats:
            row, n = parse(seat)
            if f"{row}{n - 1}" not in taken and f"{row}{n - 2}" in taken and n - 1 >= 1:
                return True
        return False

    def hold(self, customer, seats, now):
        seats = tuple(seats)
        for s in seats:
            if parse(s)[1] > self.seats_per_row:
                raise BoxOfficeError(f"no such seat {s}")
        taken = self._sold() | self._held(now)
        if taken & set(seats):
            raise BoxOfficeError("seat not available")
        if self._gap(taken | set(seats), seats):
            raise BoxOfficeError("would leave a single empty seat")
        if len(seats) > MAX_PER_CUSTOMER:
            raise BoxOfficeError("too many tickets")
        hold = Hold(next(self._ids), customer, seats, now + HOLD_FOR)
        self.holds[hold.hold_id] = hold
        return hold

    def buy(self, hold_id, customer, now):
        hold = self.holds.get(hold_id)
        if hold is None or hold.customer != customer or now >= hold.expires_at:
            raise BoxOfficeError("no valid hold")
        del self.holds[hold_id]
        total = sum((price(s) + FEE for s in hold.seats), Decimal("0"))
        order = Order(next(self._ids), customer, hold.seats, total)
        self.orders[order.order_id] = order
        return order

    def refund(self, order_id, now):
        order = self.orders.get(order_id)
        if order is None or order.refunded or self.show_at - now < REFUND_CUTOFF:
            raise BoxOfficeError("not refundable")
        order.refunded = True
        return order.total
