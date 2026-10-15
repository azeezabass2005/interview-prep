from datetime import timedelta
from typing import Dict

from ..config import MAX_QTY_PER_LINE, RESERVATION_MINUTES
from ..db import Database
from ..errors import InsufficientStock, NotFound, StockError
from ..repositories.reservations import ReservationRepository
from ..repositories.skus import SkuRepository


class ReservationService:
    def __init__(self, db: Database, clock):
        self._skus = SkuRepository(db)
        self._reservations = ReservationRepository(db)
        self._clock = clock

    def _units_for(self, sku: str, qty: int) -> Dict[str, int]:
        item = self._skus.get(sku)
        if item is None:
            raise NotFound(sku)
        if not item.is_bundle:
            return {sku: qty}
        return {component: per * qty for component, per in self._skus.components(sku).items()}

    def reserve(self, cart_id: str, sku: str, qty: int) -> None:
        if not 1 <= qty <= MAX_QTY_PER_LINE:
            raise StockError(f"quantity must be 1..{MAX_QTY_PER_LINE}")
        units = self._units_for(sku, qty)
        for component, needed in units.items():
            item = self._skus.get(component)
            if item.available < needed:
                raise InsufficientStock(f"{component}: {item.available} available, {needed} requested")
        expires = self._clock.now() + timedelta(minutes=RESERVATION_MINUTES)
        for component, needed in units.items():
            item = self._skus.get(component)
            self._skus.set_reserved(component, item.reserved + needed)
            self._reservations.create(cart_id, component, needed, expires)

    def sweep_expired(self) -> int:
        """Release reservations past their expiry. Runs every minute."""
        released = 0
        for r in self._reservations.expired(self._clock.now()):
            self._skus.adjust_reserved(r.sku, -r.qty)
            released += 1
        return released
