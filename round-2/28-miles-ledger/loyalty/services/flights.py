from datetime import date
from decimal import Decimal, InvalidOperation

from ..errors import LoyaltyError, NotFound
from ..models import FLIGHT, Flight
from ..store import InMemoryStore
from .earning import miles_for
from .status import StatusService


class FlightService:
    def __init__(self, store: InMemoryStore, status: StatusService):
        self._store = store
        self._status = status

    def record(self, flight_id: str, member_id: str, flown_on: date, base_fare) -> Flight:
        if self._store.member(member_id) is None:
            raise NotFound(f"member {member_id}")
        if self._store.flight(flight_id):
            raise LoyaltyError(f"flight {flight_id} already credited")
        try:
            fare = Decimal(str(base_fare))
        except InvalidOperation:
            raise LoyaltyError("base fare must be a number")
        if fare < 0:
            raise LoyaltyError("negative fare")
        tier = self._status.tier(member_id, flown_on)
        base, bonus = miles_for(fare, tier)
        flight = Flight(flight_id, member_id, flown_on, fare, base, bonus)
        self._store.add_flight(flight)
        self._store.add_lot(member_id, flown_on, base + bonus, FLIGHT, flight_id)
        self._store.add_qualifying(member_id, flown_on.year, base + bonus)
        return flight

    def cancel(self, flight_id: str) -> Flight:
        flight = self._store.flight(flight_id)
        if flight is None or flight.cancelled:
            raise NotFound(f"flight {flight_id}")
        flight.cancelled = True
        for lot in self._store.lots_for(flight.member_id):
            if lot.flight_id == flight_id:
                lot.remaining = 0
        self._store.add_qualifying(flight.member_id, flight.flown_on.year, -(flight.base_miles + flight.bonus_miles))
        return flight
