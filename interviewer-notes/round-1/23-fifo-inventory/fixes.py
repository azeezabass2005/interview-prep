FIXES = [
    ("inventory/ledger.py",
     """        remaining = qty
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
""",
     """        if self.on_hand(sku) < qty:
            raise InsufficientStock(f"{sku}: short by {qty - self.on_hand(sku)}")
        remaining = qty
        cogs = Decimal(0)
        for layer in self.layers(sku):
            if remaining == 0:
                break
            take = min(layer.qty, remaining)
            cogs += take * layer.unit_cost
            remaining -= take
            layer.qty -= take
        self._layers = [l for l in self._layers if l.qty > 0]
"""),
    ("inventory/ledger.py",
     "        return self.receive(shipment.sku, qty, self._latest_cost(shipment.sku), on)",
     "        average = (shipment.cogs / shipment.qty).quantize(UNIT_COST_PLACES, rounding=ROUND_HALF_UP)\n"
     "        return self.receive(shipment.sku, qty, average, on)"),
]
