import uuid
from decimal import Decimal, InvalidOperation

from ..config import BOOKING_FEE, CANCEL_FEE, CANCEL_FREE_SECONDS, DRIVER_LATE_GRACE_SECONDS, DRIVER_SHARE, PROMOS
from ..errors import InvalidState, NotFound, RideError
from ..models import ARRIVED, ASSIGNED, CANCELLED, COMPLETED, IN_PROGRESS, REQUESTED, Trip
from ..store import InMemoryStore
from .fare import cents, compute_fare, started_minutes
from .surge import SurgeFeed


class TripService:
    def __init__(self, store: InMemoryStore, surge: SurgeFeed, clock):
        self._store = store
        self._surge = surge
        self._clock = clock

    def _get(self, trip_id: str, *expected) -> Trip:
        trip = self._store.get(trip_id)
        if trip is None:
            raise NotFound(f"trip {trip_id}")
        if expected and trip.status not in expected:
            raise InvalidState(f"trip is {trip.status}")
        return trip

    def request(self, rider: str, zone: str, promo: str = None) -> Trip:
        if promo is not None and promo not in PROMOS:
            raise RideError(f"unknown promo {promo}")
        trip = Trip(f"trip-{uuid.uuid4().hex[:8]}", rider, zone, self._surge.current(zone), self._clock.now(), promo=promo)
        self._store.save(trip)
        return trip

    def assign(self, trip_id: str, driver: str, eta_seconds: int) -> Trip:
        trip = self._get(trip_id, REQUESTED)
        trip.driver, trip.eta_seconds, trip.assigned_at, trip.status = driver, eta_seconds, self._clock.now(), ASSIGNED
        return trip

    def arrive(self, trip_id: str) -> Trip:
        trip = self._get(trip_id, ASSIGNED)
        trip.arrived_at, trip.status = self._clock.now(), ARRIVED
        return trip

    def pick_up(self, trip_id: str) -> Trip:
        trip = self._get(trip_id, ARRIVED)
        trip.picked_up_at, trip.status = self._clock.now(), IN_PROGRESS
        return trip

    def complete(self, trip_id: str, miles, tolls="0") -> Trip:
        trip = self._get(trip_id, IN_PROGRESS)
        try:
            trip.miles, trip.tolls = Decimal(str(miles)), Decimal(str(tolls))
        except InvalidOperation:
            raise RideError("miles and tolls must be numbers")
        trip.dropped_off_at = self._clock.now()
        ride = started_minutes(trip.picked_up_at, trip.dropped_off_at)
        wait = started_minutes(trip.arrived_at, trip.picked_up_at)
        breakdown = compute_fare(trip.miles, ride, wait, self._surge.current(trip.zone), trip.tolls, trip.promo)
        trip.fare = breakdown.total
        trip.driver_payout = cents((trip.fare - trip.tolls) * DRIVER_SHARE) + trip.tolls
        trip.status = COMPLETED
        return trip

    def cancel(self, trip_id: str) -> Trip:
        trip = self._get(trip_id, REQUESTED, ASSIGNED, ARRIVED)
        now = self._clock.now()
        fee = Decimal("0.00")
        if trip.assigned_at is not None:
            waited = (now - trip.assigned_at).total_seconds()
            driver_late = trip.arrived_at is None and waited > trip.eta_seconds + DRIVER_LATE_GRACE_SECONDS
            if waited > CANCEL_FREE_SECONDS and not driver_late:
                fee = CANCEL_FEE
        trip.cancel_fee, trip.status = fee, CANCELLED
        return trip
