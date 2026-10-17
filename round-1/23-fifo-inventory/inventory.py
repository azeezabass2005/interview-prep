from dataclasses import dataclass
from datetime import date
from decimal import Decimal


class InventoryError(Exception):
    pass


@dataclass
class Lot:
    quantity: int
    cost: Decimal
    received: date


@dataclass
class Shipment:
    warehouse: str
    sku: str
    quantity: int
    cogs: Decimal
    returned: int = 0


class Inventory:
    def __init__(self):
        self.stock = {}
        self.shipments = {}
        self.reorder_points = {}
        self.reorders = []

    def lots(self, warehouse, sku):
        return self.stock.setdefault((warehouse, sku), [])

    def on_hand(self, warehouse, sku):
        return sum(l.quantity for l in self.lots(warehouse, sku))

    def value(self, warehouse, sku):
        return sum((l.quantity * l.cost for l in self.lots(warehouse, sku)), Decimal("0"))

    def receive(self, warehouse, sku, quantity, cost, on):
        if quantity <= 0:
            raise InventoryError("quantity must be positive")
        lots = self.lots(warehouse, sku)
        lots.append(Lot(quantity, Decimal(str(cost)), on))
        lots.sort(key=lambda l: l.received)

    def _take(self, lots, quantity):
        taken, remaining = [], quantity
        while remaining:
            if not lots:
                raise InventoryError("insufficient stock")
            lot = lots[-1]
            used = min(remaining, lot.quantity)
            taken.append(Lot(used, lot.cost, lot.received))
            lot.quantity -= used
            remaining -= used
            if lot.quantity == 0:
                lots.remove(lot)
        return taken

    def set_reorder_point(self, warehouse, sku, point):
        self.reorder_points[(warehouse, sku)] = point

    def ship(self, shipment_id, warehouse, sku, quantity):
        if shipment_id in self.shipments or quantity <= 0:
            raise InventoryError("bad shipment")
        taken = self._take(self.lots(warehouse, sku), quantity)
        cogs = sum((t.quantity * t.cost for t in taken), Decimal("0"))
        self.shipments[shipment_id] = Shipment(warehouse, sku, quantity, cogs)
        point = self.reorder_points.get((warehouse, sku))
        if point is not None and self.on_hand(warehouse, sku) < point:
            self.reorders.append((warehouse, sku))
        return cogs

    def transfer(self, source, destination, sku, quantity, on):
        taken = self._take(self.lots(source, sku), quantity)
        lots = self.lots(destination, sku)
        for t in taken:
            lots.append(Lot(t.quantity, t.cost, on))

    def return_goods(self, shipment_id, quantity, on):
        s = self.shipments.get(shipment_id)
        if s is None or quantity <= 0 or s.returned + quantity > s.quantity:
            raise InventoryError("bad return")
        lots = self.lots(s.warehouse, s.sku)
        cost = lots[-1].cost if lots else s.cogs / s.quantity
        s.returned += quantity
        self.receive(s.warehouse, s.sku, quantity, cost, on)
