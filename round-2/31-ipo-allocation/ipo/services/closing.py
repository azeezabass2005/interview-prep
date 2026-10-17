from decimal import Decimal, InvalidOperation

from ..config import LOT_SIZE, RETAIL_TRANCHE
from ..errors import InvalidState, IpoError
from ..models import ACTIVE, CLOSED, INSTITUTIONAL, OPEN, RETAIL, Offering
from .allocation import allocate_tranche
from .book import BookService


class ClosingService:
    def __init__(self, book: BookService):
        self._book = book

    def close(self, offering_id: str, final_price) -> Offering:
        offering = self._book.get(offering_id)
        if offering.status != OPEN:
            raise InvalidState("already closed")
        try:
            price = Decimal(str(final_price))
        except InvalidOperation:
            raise IpoError("price must be a number")
        offering.final_price = price
        offering.status = CLOSED
        live = [o for o in offering.orders.values() if o.status == ACTIVE]
        retail = [o for o in live if o.category == RETAIL]
        institutional = [o for o in live if o.category == INSTITUTIONAL]
        retail_tranche = int(offering.shares * RETAIL_TRANCHE) // LOT_SIZE * LOT_SIZE
        institutional_tranche = offering.shares - retail_tranche
        allocations = allocate_tranche(retail, retail_tranche, guarantee_lot=True)
        allocations.update(allocate_tranche(institutional, institutional_tranche, guarantee_lot=False))
        offering.allocations = allocations
        return offering
