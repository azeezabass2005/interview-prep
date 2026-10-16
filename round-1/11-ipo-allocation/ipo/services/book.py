from decimal import Decimal, InvalidOperation

from ..config import LOT_SIZE
from ..errors import InvalidState, IpoError, NotFound
from ..models import ACTIVE, CANCELLED, OPEN, Offering, Order
from ..store import InMemoryStore


class BookService:
    def __init__(self, store: InMemoryStore):
        self._store = store

    def create(self, offering_id: str, shares: int) -> Offering:
        if shares <= 0 or shares % LOT_SIZE:
            raise IpoError("offering must be whole lots")
        offering = Offering(offering_id, shares)
        self._store.save(offering)
        return offering

    def get(self, offering_id: str) -> Offering:
        offering = self._store.get(offering_id)
        if offering is None:
            raise NotFound(offering_id)
        return offering

    def _open(self, offering_id: str) -> Offering:
        offering = self.get(offering_id)
        if offering.status != OPEN:
            raise InvalidState("book is closed")
        return offering

    def _validate(self, shares, limit):
        try:
            shares, limit = int(shares), Decimal(str(limit))
        except (ValueError, InvalidOperation):
            raise IpoError("shares and limit must be numbers")
        if shares <= 0 or shares % LOT_SIZE or limit <= 0:
            raise IpoError("shares must be whole lots and the limit positive")
        return shares, limit

    def submit(self, offering_id: str, investor: str, shares, limit) -> Order:
        offering = self._open(offering_id)
        existing = offering.orders.get(investor)
        if existing and existing.status == ACTIVE:
            raise IpoError(f"{investor} already has an order")
        shares, limit = self._validate(shares, limit)
        order = Order(investor, shares, limit, self._store.next_seq())
        offering.orders[investor] = order
        return order

    def amend(self, offering_id: str, investor: str, shares=None, limit=None) -> Order:
        offering = self._open(offering_id)
        order = offering.orders.get(investor)
        if order is None or order.status != ACTIVE:
            raise NotFound(f"no active order for {investor}")
        new_shares, new_limit = self._validate(shares if shares is not None else order.shares,
                                               limit if limit is not None else order.limit)
        order.shares, order.limit = new_shares, new_limit
        return order

    def cancel(self, offering_id: str, investor: str) -> Order:
        offering = self._open(offering_id)
        order = offering.orders.get(investor)
        if order is None or order.status != ACTIVE:
            raise NotFound(f"no active order for {investor}")
        order.status = CANCELLED
        return order
