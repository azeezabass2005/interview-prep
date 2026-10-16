from ..config import REFUND_CUTOFF_HOURS
from ..db import Database
from ..errors import NotFound, RefundNotAllowed
from ..repositories.events import EventRepository
from ..repositories.orders import OrderRepository
from ..repositories.seats import SeatRepository


class RefundService:
    def __init__(self, db: Database, clock):
        self._events = EventRepository(db)
        self._orders = OrderRepository(db)
        self._seats = SeatRepository(db)
        self._clock = clock

    def hours_until_event(self, event) -> float:
        return (event.starts_at_local - self._clock.now()).total_seconds() / 3600

    def refund(self, order_id: str) -> int:
        order = self._orders.get(order_id)
        if order is None or order.status != "PAID":
            raise NotFound(order_id)
        event = self._events.get(order.event_id)
        if self.hours_until_event(event) < REFUND_CUTOFF_HOURS:
            raise RefundNotAllowed("refund window has closed")
        self._orders.set_status(order_id, "REFUNDED")
        self._seats.release(order.event_id, order.seat_ids)
        return order.face_total_cents
