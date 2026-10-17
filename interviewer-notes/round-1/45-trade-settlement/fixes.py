FIXES = [
    ("settlement.py", "        while d.weekday() >= 5:", "        while d.weekday() >= 5 or d in self.holidays:"),
    ("settlement.py", "            if t.settles_on != day:", "            if t.settles_on != day or t.cancelled:"),
    ("settlement.py", "            netted[key] = (qty + t.quantity, cash", "            netted[key] = (qty + (t.quantity if t.side == \"BUY\" else -t.quantity), cash"),
    ("settlement.py", "        instructions = self.net(day)\n        self.failed = []",
     "        instructions = self.failed + self.net(day)\n        self.failed = []"),
    ("settlement.py", "                ins.status = \"FAILED\"", "                ins.status = \"FAILED\"\n                self.failed.append(ins)"),
    ("settlement.py", "        for symbol, quantity in ours.items():\n            theirs = custodian.get(symbol, 0)",
     "        for symbol in set(ours) | set(custodian):\n            quantity, theirs = ours.get(symbol, 0), custodian.get(symbol, 0)"),
]
