import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from typing import Optional

BASE = Decimal("2.50")
PER_KM = Decimal("1.20")
PER_MIN = Decimal("0.30")
MIN_FARE = Decimal("7.00")
FREE_WAIT_MIN = 2
WAIT_PER_MIN = Decimal("0.40")
BOOKING_FEE = Decimal("1.50")
MAX_DISCOUNT = Decimal("10.00")
DRIVER_SHARE = Decimal("0.75")
CANCEL_FEE = Decimal("5.00")
FREE_CANCEL = timedelta(minutes=5)
CENT = Decimal("0.01")


def money(x):
    return Decimal(x).quantize(CENT, rounding=ROUND_HALF_UP)


class RideError(Exception):
    pass


@dataclass
class Trip:
    trip_id: str
    rider: str
    requested_at: datetime
    surge: Decimal
    promo_pct: Decimal
    status: str = "REQUESTED"
    driver: Optional[str] = None
    accepted_at: Optional[datetime] = None
    arrived_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    receipt: Optional[dict] = None


class RideService:
    def __init__(self):
        self.trips = {}
        self.current_surge = Decimal("1.0")

    def set_surge(self, multiplier):
        self.current_surge = Decimal(str(multiplier))

    def request(self, trip_id, rider, at, promo_pct=0):
        trip = Trip(trip_id, rider, at, self.current_surge, Decimal(str(promo_pct)) / 100)
        self.trips[trip_id] = trip
        return trip

    def _move(self, trip_id, expected, new):
        trip = self.trips.get(trip_id)
        if trip is None or trip.status != expected:
            raise RideError(f"trip must be {expected}")
        trip.status = new
        return trip

    def accept(self, trip_id, driver, at):
        trip = self._move(trip_id, "REQUESTED", "ACCEPTED")
        trip.driver, trip.accepted_at = driver, at

    def arrive(self, trip_id, at):
        self._move(trip_id, "ACCEPTED", "ARRIVED").arrived_at = at

    def start(self, trip_id, at):
        self._move(trip_id, "ARRIVED", "STARTED").started_at = at

    def cancel(self, trip_id, at):
        trip = self.trips.get(trip_id)
        if trip is None or trip.status not in ("REQUESTED", "ACCEPTED", "ARRIVED"):
            raise RideError("cannot cancel")
        fee = Decimal("0.00")
        if trip.accepted_at is not None and at - trip.accepted_at > FREE_CANCEL:
            fee = CANCEL_FEE
        trip.status = "CANCELLED"
        return fee

    def _waiting(self, trip):
        minutes = math.ceil((trip.started_at - trip.arrived_at).total_seconds() / 60)
        return money(minutes * WAIT_PER_MIN) if minutes > FREE_WAIT_MIN else Decimal("0.00")

    def complete(self, trip_id, km, minutes):
        trip = self._move(trip_id, "STARTED", "COMPLETED")
        raw = BASE + PER_KM * Decimal(str(km)) + PER_MIN * Decimal(str(minutes))
        fare = money(max(raw, MIN_FARE) * self.current_surge)
        waiting = self._waiting(trip)
        discount = money((fare + waiting) * trip.promo_pct)
        payout = money((fare + waiting - discount) * DRIVER_SHARE)
        trip.receipt = {
            "fare": fare, "waiting": waiting, "booking_fee": BOOKING_FEE, "discount": discount,
            "total": fare + waiting + BOOKING_FEE - discount, "driver_payout": payout,
        }
        return trip.receipt
