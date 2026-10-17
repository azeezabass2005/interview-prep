FIXES = [
    ("tab.py", "            each = (amount / len(participants)).quantize(CENT, rounding=ROUND_DOWN)\n            return {p: each for p in participants}",
     "            return self._with_leftover(amount, {p: amount / len(participants) for p in participants}, participants)"),
    ("tab.py", "        if mode == \"EXACT\":\n            return dict(zip(participants, values))",
     "        if mode == \"EXACT\":\n            if sum(values) != amount:\n                raise TabError(\"amounts must add up to the expense\")\n            return dict(zip(participants, values))"),
    ("tab.py", "            total = len(participants)", "            total = sum(values)"),
    ("tab.py", "            balance[p.sender] -= p.amount\n            balance[p.receiver] += p.amount",
     "            balance[p.sender] += p.amount\n            balance[p.receiver] -= p.amount"),
    ("tab.py", "        for e in self.expenses.values():\n", "        for e in self.expenses.values():\n            if e.deleted:\n                continue\n"),
]
