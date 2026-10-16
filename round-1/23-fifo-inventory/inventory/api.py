from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from .errors import InventoryError
from .services.receiving import ReceivingService
from .services.shipping import ShippingService
from .services.transfers import TransferService
from .services.valuation import valuation
from .store import InMemoryStore


class InventoryApi:
    def __init__(self, store: InMemoryStore):
        self._store = store
        self._receiving = ReceivingService(store)
        self._shipping = ShippingService(store)
        self._transfers = TransferService(store)

    def _call(self, fn, ok=200):
        try:
            return ok, fn()
        except InventoryError as exc:
            return exc.status, {"error": str(exc)}

    def receive(self, sku, warehouse, qty, cost, on):
        return self._call(lambda: {"layer": self._receiving.receive(sku, warehouse, qty, cost, date.fromisoformat(on)).seq}, 201)

    def ship(self, shipment_id, sku, warehouse, qty):
        return self._call(lambda: {"cogs": str(self._shipping.ship(shipment_id, sku, warehouse, qty).cogs.quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP))}, 201)

    def return_units(self, shipment_id, qty, on):
        return self._call(lambda: {"unit_cost": str(self._shipping.return_units(shipment_id, qty, date.fromisoformat(on)).unit_cost)}, 201)

    def transfer(self, sku, source, destination, qty, on):
        return self._call(lambda: self._transfers.transfer(sku, source, destination, qty, date.fromisoformat(on)) or {"ok": True})

    def value(self, sku, warehouse):
        return 200, {"on_hand": self._store.on_hand(sku, warehouse), "value": str(valuation(self._store, sku, warehouse))}
