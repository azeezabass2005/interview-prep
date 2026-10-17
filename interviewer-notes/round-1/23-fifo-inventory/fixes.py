FIXES = [
    ("inventory.py", "            lot = lots[-1]\n", "            lot = lots[0]\n"),
    ("inventory.py", "        taken, remaining = [], quantity\n",
     "        if sum(l.quantity for l in lots) < quantity:\n            raise InventoryError(\"insufficient stock\")\n        taken, remaining = [], quantity\n"),
    ("inventory.py", "            lots.append(Lot(t.quantity, t.cost, on))", "            lots.append(Lot(t.quantity, t.cost, t.received))\n        lots.sort(key=lambda l: l.received)"),
    ("inventory.py", "        cost = lots[-1].cost if lots else s.cogs / s.quantity", "        cost = s.cogs / s.quantity"),
    ("inventory.py", "self.on_hand(warehouse, sku) < point:", "self.on_hand(warehouse, sku) <= point:"),
]
