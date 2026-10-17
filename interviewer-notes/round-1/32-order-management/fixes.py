FIXES = [
    ("oms.py", "        if not 1 <= quantity < MAX_QTY:", "        if not 1 <= quantity <= MAX_QTY:"),
    ("oms.py", "        order = self.orders.get(order_id)\n        if order is None or order.status in",
     "        if exec_id in self.exec_ids:\n            return self.orders[order_id]\n        order = self.orders.get(order_id)\n        if order is None or order.status in"),
    ("oms.py", "        if order.filled == order.quantity:\n            order.status = \"FILLED\"",
     "        order.status = \"FILLED\" if order.filled == order.quantity else \"PARTIALLY_FILLED\""),
    ("oms.py", "        return (sum(self.fill_prices) / len(self.fill_prices)).quantize(",
     "        return (self.notional_filled / self.filled).quantize("),
    ("oms.py", "        self.positions[key] = self.positions.get(key, 0) + quantity",
     "        self.positions[key] = self.positions.get(key, 0) + (quantity if order.side == \"BUY\" else -quantity)"),
]
