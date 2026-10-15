import uuid
from typing import List

from ..db import Database
from ..errors import NotFound, SeatUnavailable
from ..models import HELD, Order
from ..notifications import Notifier
from ..repositories.events import EventRepository
from ..repositories.orders import OrderRepository
from ..repositories.seats import SeatRepository
from .pricing import order_amounts


class CheckoutService:
    def __init__(self, db: Database, clock):
        self._events = EventRepository(db)
        self._seats = SeatRepository(db)
        self._orders = OrderRepository(db)
        self._notifier = Notifier(db, clock)
        self._clock = clock

    def purchase(self, customer: str, event_id: str, seat_ids: List[str]) -> Order:
        event = self._events.get(event_id)
        if event is None:
            raise NotFound(event_id)
        now = self._clock.now().isoformat()
        for seat_id in seat_ids:
            seat = self._seats.get(event_id, seat_id)
            if seat is None or seat.status != HELD or seat.held_by != customer or seat.hold_expires_at <= now:
                raise SeatUnavailable(f"seat {seat_id} is not held by you")
        face, fees, total = order_amounts(event.face_value_cents, len(seat_ids))
        order = Order(f"ord_{uuid.uuid4().hex[:10]}", event_id, customer, tuple(seat_ids), face, fees, total, "PAID")
        self._orders.insert(order, self._clock.now())
        self._seats.mark_sold(event_id, seat_ids, order.order_id)
        self._notifier.receipt(customer, order)
        return order
