from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import Dict, List

from .models import InsufficientStock, Layer, Shipment

UNIT_COST_PLACES = Decimal("0.0001")


class Inventory:
    def __init__(self):
        self._layers: List[Layer] = []
        self._shipments: Dict[str, Shipment] = {}

    def receive(self, sku: str, qty: int, unit_cost, on: date) -> Layer:
        if qty <= 0:
            raise ValueError("quantity must be positive")
        layer = Layer(sku, qty, Decimal(unit_cost), on)
        self._layers.append(layer)
        return layer

    def layers(self, sku: str) -> List[Layer]:
        return [l for l in self._layers if l.sku == sku]

    def on_hand(self, sku: str) -> int:
        return sum(l.qty for l in self.layers(sku))

    def valuation(self, sku: str) -> Decimal:
        total = sum((l.qty * l.unit_cost for l in self.layers(sku)), Decimal(0))
        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def ship(self, shipment_id: str, sku: str, qty: int) -> Shipment:
        if qty <= 0:
            raise ValueError("quantity must be positive")
        remaining = qty
        cogs = Decimal(0)
        layers = self._layers
        while remaining > 0:
            if not layers:
                raise InsufficientStock(f"{sku}: short by {remaining}")
            layer = layers[-1]
            take = min(layer.qty, remaining)
            cogs += take * layer.unit_cost
            remaining -= take
            if take == layer.qty:
                layers.pop()
            else:
                layer.qty = take
        shipment = Shipment(shipment_id, sku, qty, cogs)
        self._shipments[shipment_id] = shipment
        return shipment

    def _latest_cost(self, sku: str) -> Decimal:
        layers = self.layers(sku)
        return layers[-1].unit_cost if layers else Decimal(0)

    def return_units(self, shipment_id: str, qty: int, on: date) -> Layer:
        shipment = self._shipments[shipment_id]
        if qty <= 0 or shipment.returned + qty > shipment.qty:
            raise ValueError("cannot return more than was shipped")
        shipment.returned += qty
        return self.receive(shipment.sku, qty, self._latest_cost(shipment.sku), on)
