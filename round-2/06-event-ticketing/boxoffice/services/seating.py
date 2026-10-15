from datetime import timedelta
from typing import List

from ..config import HOLD_MINUTES, MAX_SEATS_PER_ORDER
from ..db import Database
from ..errors import BoxOfficeError, NotFound, SeatUnavailable
from ..models import AVAILABLE, HELD, Seat
from ..repositories.seats import SeatRepository


class SeatService:
    def __init__(self, db: Database, clock):
        self._seats = SeatRepository(db)
        self._clock = clock

    def is_available(self, seat: Seat) -> bool:
        if seat.status == AVAILABLE:
            return True
        return seat.status == HELD and seat.hold_expires_at < str(self._clock.now())

    def hold(self, event_id: str, seat_ids: List[str], customer: str) -> None:
        if not seat_ids or len(seat_ids) > MAX_SEATS_PER_ORDER:
            raise BoxOfficeError(f"choose 1-{MAX_SEATS_PER_ORDER} seats")
        seats = []
        for seat_id in seat_ids:
            seat = self._seats.get(event_id, seat_id)
            if seat is None:
                raise NotFound(f"seat {seat_id}")
            seats.append(seat)
        for seat in seats:
            if not self.is_available(seat):
                raise SeatUnavailable(f"seat {seat.seat_id} is unavailable")
        expires = self._clock.now() + timedelta(minutes=HOLD_MINUTES)
        for seat in seats:
            self._seats.set_hold(event_id, seat.seat_id, customer, expires)

    def available(self, event_id: str) -> List[str]:
        return [s.seat_id for s in self._seats.for_event(event_id) if self.is_available(s)]
