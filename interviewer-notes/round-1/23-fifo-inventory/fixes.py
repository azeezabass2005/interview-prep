FIXES = [
    ("inventory/services/fifo.py", "key=lambda l: (l.received_on, l.seq), reverse=True):", "key=lambda l: (l.received_on, l.seq)):"),
    ("inventory/services/fifo.py", "        layer.qty = layer.qty - n if n == layer.qty else n", "        layer.qty -= n"),
    ("inventory/services/shipping.py", "        taken = take(self._store, sku, warehouse, qty)\n        shipped = sum(n for _, n in taken)\n        if shipped < qty:\n            raise InsufficientStock(f\"{sku}@{warehouse}: short by {qty - shipped}\")\n",
     "        if self._store.on_hand(sku, warehouse) < qty:\n            raise InsufficientStock(f\"{sku}@{warehouse}\")\n        taken = take(self._store, sku, warehouse, qty)\n"),
    ("inventory/services/shipping.py",
     "        layers = self._store.layers[(shipment.sku, shipment.warehouse)]\n        cost = layers[-1].unit_cost if layers else Decimal(\"0\")\n",
     "        cost = (shipment.cogs / shipment.qty).quantize(Decimal(\"0.0001\"), rounding=ROUND_HALF_UP)\n"),
    ("inventory/services/transfers.py", "self._store.add_layer(sku, destination, n, layer.unit_cost, on)",
     "self._store.add_layer(sku, destination, n, layer.unit_cost, layer.received_on)"),
]
