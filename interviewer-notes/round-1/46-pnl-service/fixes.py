FIXES = [
    ("pnl.py", "            lot = lots[-1]", "            lot = lots[0]"),
    ("pnl.py", "        pnl = money(quantity * price - cost)", "        pnl = money(quantity * price - commission - cost)"),
    ("pnl.py", "            lot.quantity *= ratio", "            lot.quantity *= ratio\n            lot.cost_per_share /= ratio"),
    ("pnl.py", "            cost += lot.quantity * lot.cost_per_share", "            cost += take * lot.cost_per_share"),
    ("pnl.py", "        remaining, cost = quantity, Decimal(\"0\")", "        if quantity > self.held(symbol):\n            raise PnlError(\"cannot sell more than held\")\n        remaining, cost = quantity, Decimal(\"0\")"),
]
