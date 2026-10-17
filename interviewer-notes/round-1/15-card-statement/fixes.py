FIXES = [
    ("statement.py", "        amount = self._record(on, \"cash\", amount)\n        return money(min(amount * CASH_FEE_PCT, CASH_FEE_MIN))",
     "        amount = self._record(on, \"cash\", amount)\n        return money(max(amount * CASH_FEE_PCT, CASH_FEE_MIN))"),
    ("statement.py", "            self.balances[\"cash\"] += amount + money(min(amount * CASH_FEE_PCT, CASH_FEE_MIN))",
     "            self.balances[\"cash\"] += amount + money(max(amount * CASH_FEE_PCT, CASH_FEE_MIN))"),
    ("statement.py", "PAYMENT_ORDER = (\"purchase\", \"cash\")", "PAYMENT_ORDER = (\"cash\", \"purchase\")"),
    ("statement.py", "paid_by_due > previous[\"balance\"]", "paid_by_due >= previous[\"balance\"]"),
    ("statement.py", "        for offset in range((end - start).days):", "        for offset in range((end - start).days + 1):"),
    ("statement.py", "        elif balance < MIN_PAYMENT:\n            minimum = MIN_PAYMENT", "        elif balance < MIN_PAYMENT:\n            minimum = balance"),
]
