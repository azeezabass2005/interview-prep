from datetime import date

from ..errors import InsufficientStock, InventoryError
from ..store import InMemoryStore
from .fifo import take


class TransferService:
    def __init__(self, store: InMemoryStore):
        self._store = store

    def transfer(self, sku: str, source: str, destination: str, qty: int, on: date) -> None:
        if source == destination or qty <= 0:
            raise InventoryError("transfer needs two warehouses and a positive quantity")
        if self._store.on_hand(sku, source) < qty:
            raise InsufficientStock(f"{sku}@{source}")
        for layer, n in take(self._store, sku, source, qty):
            self._store.add_layer(sku, destination, n, layer.unit_cost, on)
