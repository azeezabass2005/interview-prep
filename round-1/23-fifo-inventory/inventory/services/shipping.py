from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from ..errors import InsufficientStock, InventoryError, NotFound
from ..models import Shipment
from ..store import InMemoryStore
from .fifo import cost_of, take


class ShippingService:
    def __init__(self, store: InMemoryStore):
        self._store = store

    def ship(self, shipment_id: str, sku: str, warehouse: str, qty: int) -> Shipment:
        if qty <= 0:
            raise InventoryError("quantity must be positive")
        if shipment_id in self._store.shipments:
            raise InventoryError("duplicate shipment id")
        taken = take(self._store, sku, warehouse, qty)
        shipped = sum(n for _, n in taken)
        if shipped < qty:
            raise InsufficientStock(f"{sku}@{warehouse}: short by {qty - shipped}")
        shipment = Shipment(shipment_id, sku, warehouse, qty, cost_of(taken))
        self._store.shipments[shipment_id] = shipment
        return shipment

    def return_units(self, shipment_id: str, qty: int, on: date):
        shipment = self._store.shipments.get(shipment_id)
        if shipment is None:
            raise NotFound(shipment_id)
        if qty <= 0 or shipment.returned + qty > shipment.qty:
            raise InventoryError("cannot return more than was shipped")
        layers = self._store.layers[(shipment.sku, shipment.warehouse)]
        cost = layers[-1].unit_cost if layers else Decimal("0")
        shipment.returned += qty
        return self._store.add_layer(shipment.sku, shipment.warehouse, qty, cost, on)
