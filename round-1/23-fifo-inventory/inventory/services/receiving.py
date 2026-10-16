from datetime import date
from decimal import Decimal, InvalidOperation

from ..errors import InventoryError
from ..store import InMemoryStore


class ReceivingService:
    def __init__(self, store: InMemoryStore):
        self._store = store

    def receive(self, sku: str, warehouse: str, qty: int, unit_cost, on: date):
        try:
            unit_cost = Decimal(str(unit_cost))
        except InvalidOperation:
            raise InventoryError("unit cost must be a number")
        if qty <= 0 or unit_cost < 0:
            raise InventoryError("quantity must be positive and cost non-negative")
        return self._store.add_layer(sku, warehouse, qty, unit_cost, on)
