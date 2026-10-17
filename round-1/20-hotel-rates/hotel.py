from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from decimal import ROUND_HALF_UP, Decimal

WEEKDAY_RATE = Decimal("150.00")
WEEKEND_RATE = Decimal("190.00")
WEEKEND_NIGHTS = (5, 6)
ADVANCE_DISCOUNT = Decimal("0.15")
ADVANCE_DAYS = 14
LONG_STAY_NIGHTS = 7
LONG_STAY_DISCOUNT = Decimal("0.10")
TAX = Decimal("0.12")
CHECK_IN_TIME = time(15, 0)
FREE_CANCEL = timedelta(hours=48)
CENT = Decimal("0.01")
PLANS = ("BAR", "ADVANCE")


def money(x):
    return x.quantize(CENT, rounding=ROUND_HALF_UP)


class HotelError(Exception):
    pass


@dataclass
class Reservation:
    res_id: str
    guest: str
    room_type: str
    check_in: date
    check_out: date
    plan: str
    nights: list
    total: Decimal
    status: str = "BOOKED"


class Hotel:
    def __init__(self, inventory):
        self.inventory = dict(inventory)
        self.reservations = {}

    @staticmethod
    def _nights(check_in, check_out):
        return [check_in + timedelta(days=i) for i in range((check_out - check_in).days + 1)]

    def _booked(self, room_type, night):
        return sum(1 for r in self.reservations.values()
                   if r.status == "BOOKED" and r.room_type == room_type and night in r.nights)

    def nightly_rate(self, night, plan):
        rate = WEEKEND_RATE if night.weekday() in WEEKEND_NIGHTS else WEEKDAY_RATE
        if plan == "ADVANCE":
            rate = money(rate * (1 - ADVANCE_DISCOUNT))
        return rate

    def price(self, nights, plan):
        room = sum((self.nightly_rate(n, plan) for n in nights), Decimal("0"))
        if len(nights) >= LONG_STAY_NIGHTS:
            room = money(room * (1 - LONG_STAY_DISCOUNT))
        return money(room * (1 + TAX))

    def book(self, res_id, guest, room_type, check_in, check_out, plan, booked_at):
        if res_id in self.reservations or plan not in PLANS or room_type not in self.inventory:
            raise HotelError("bad reservation")
        if check_out <= check_in:
            raise HotelError("check-out must be after check-in")
        if plan == "ADVANCE" and (check_in - booked_at.date()).days > ADVANCE_DAYS:
            pass
        elif plan == "ADVANCE":
            raise HotelError("advance rate needs 14 days' notice")
        nights = self._nights(check_in, check_out)
        if self._booked(room_type, nights[0]) >= self.inventory[room_type]:
            raise HotelError("no availability")
        reservation = Reservation(res_id, guest, room_type, check_in, check_out, plan, nights, self.price(nights, plan))
        self.reservations[res_id] = reservation
        return reservation

    def cancel(self, res_id, at):
        r = self.reservations.get(res_id)
        if r is None or r.status != "BOOKED":
            raise HotelError("nothing to cancel")
        r.status = "CANCELLED"
        if r.plan == "ADVANCE":
            return r.total
        deadline = datetime.combine(r.check_in, time(0, 0)) - FREE_CANCEL
        if at <= deadline:
            return Decimal("0.00")
        return money(self.nightly_rate(r.nights[0], r.plan) * (1 + TAX))
