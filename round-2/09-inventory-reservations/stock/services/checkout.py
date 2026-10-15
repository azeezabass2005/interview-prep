from ..db import Database
from ..errors import StockError
from ..models import SOLD
from ..repositories.reservations import ReservationRepository
from ..repositories.skus import SkuRepository


class CheckoutService:
    def __init__(self, db: Database, clock):
        self._skus = SkuRepository(db)
        self._reservations = ReservationRepository(db)
        self._clock = clock

    def confirm(self, cart_id: str) -> int:
        lines = self._reservations.active_for_cart(cart_id)
        if not lines:
            raise StockError("cart has no active reservations")
        for r in lines:
            self._skus.record_sale(r.sku, r.qty)
            self._reservations.set_status(r.reservation_id, SOLD)
        return len(lines)
