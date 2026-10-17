FIXES = [
    ("tab/splitting.py", "    base = amount // len(names)\n    return {name: base for name in names}",
     "    base, leftover = divmod(amount, len(names))\n    return {name: base + (1 if i < leftover else 0) for i, name in enumerate(names)}"),
    ("tab/splitting.py", "    for name in sorted(shares)[:leftover]:",
     "    for name in sorted(shares, key=lambda n: (-(exact[n] - shares[n]), n))[:leftover]:"),
    ("tab/services/balances.py", "        for expense in self._store.group_expenses(group_id):\n",
     "        for expense in self._store.group_expenses(group_id):\n            if expense.deleted:\n                continue\n"),
    ("tab/services/balances.py",
     "            balance[payment.sender] -= payment.amount_cents\n            balance[payment.receiver] += payment.amount_cents",
     "            balance[payment.sender] += payment.amount_cents\n            balance[payment.receiver] -= payment.amount_cents"),
    ("tab/services/settle.py", "key=lambda m: (creditors[m], m))[0]", "key=lambda m: (-creditors[m], m))[0]"),
]
