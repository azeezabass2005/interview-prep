FIXES = [
    ("margin.py", "            equity += value\n", "            equity += quantity * price\n"),
    ("margin.py", "        gross = sum(abs(q) * self._price(s)[0] for s, q in account.positions.items())",
     "        gross = sum(q * self._price(s)[0] for s, q in account.positions.items() if q > 0)"),
    ("margin.py", "            if now - as_of >= STALE_AFTER:", "            if now - as_of > STALE_AFTER:"),
    ("margin.py", "from decimal import ROUND_HALF_UP, Decimal", "from decimal import ROUND_CEILING, Decimal"),
    ("margin.py", "rounding=ROUND_HALF_UP)", "rounding=ROUND_CEILING)"),
    ("margin.py", "        paid = sum(amount for _, amount in account.deposits)",
     "        paid = sum(amount for at, amount in account.deposits if at >= account.call[\"issued_at\"])"),
]
