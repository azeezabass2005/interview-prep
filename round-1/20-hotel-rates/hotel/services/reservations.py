import uuid
from datetime import date, datetime

from ..config import CHECK_IN_HOUR, FULL_REFUND_HOURS, PARTIAL_REFUND_HOURS, TAX_RATE
from ..errors import HotelError, NotFound, Unavailable
from ..models import CANCELLED, CONFIRMED, FLEXIBLE, NON_REFUNDABLE, Reservation
from ..store import InMemoryStore
from .availability import Availability
from .pricing import cents, price


class ReservationService:
    def __init__(self, store: InMemoryStore, clock):
        self._store = store
        self._availability = Availability(store)
        self._clock = clock

    def book(self, guest: str, room_type: str, check_in: date, check_out: date, plan: str = FLEXIBLE,
             promo: str = None) -> Reservation:
        if plan not in (FLEXIBLE, NON_REFUNDABLE):
            raise HotelError("unknown rate plan")
        quote = price(room_type, check_in, check_out, plan, promo)
        if not self._availability.available(room_type, check_in, check_out):
            raise Unavailable(f"no {room_type} rooms for those dates")
        r = Reservation(f"R{uuid.uuid4().hex[:6].upper()}", guest, room_type, check_in, check_out, plan, promo, quote)
        self._store.reservations[r.reservation_id] = r
        return r

    def cancel(self, reservation_id: str) -> Reservation:
        r = self._store.reservations.get(reservation_id)
        if r is None or r.status != CONFIRMED:
            raise NotFound(reservation_id)
        r.status = CANCELLED
        r.refund = self.refund_for(r)
        return r

    def refund_for(self, r: Reservation):
        if r.plan == NON_REFUNDABLE:
            return cents(0 * TAX_RATE)
        check_in = datetime(r.check_in.year, r.check_in.month, r.check_in.day)
        hours = (check_in - self._clock.now()).total_seconds() / 3600
        if hours >= FULL_REFUND_HOURS:
            return r.quote.total
        if hours >= PARTIAL_REFUND_HOURS:
            first = r.quote.nightly[0]
            return r.quote.total - first - cents(first * TAX_RATE)
        return cents(0 * TAX_RATE)
