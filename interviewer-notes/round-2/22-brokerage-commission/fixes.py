FIXES = [
    ("fees/services/commission.py",
     """    for upper, rate in EQUITY_TIERS:
        if upper is None or amount <= upper:
            return amount * rate
    raise AssertionError("tier table must end with an unbounded band")""",
     """    total, lower = Decimal("0"), Decimal("0")
    for upper, rate in EQUITY_TIERS:
        top = amount if upper is None else min(amount, upper)
        if top > lower:
            total += (top - lower) * rate
        if upper is None or amount <= upper:
            return total
        lower = upper
    raise AssertionError("tier table must end with an unbounded band")"""),
    ("fees/services/commission.py", "    return clamp(half_up(OPTION_PER_CONTRACT * contracts), OPTION_MIN, EQUITY_MAX)",
     "    return clamp(half_up(OPTION_PER_CONTRACT * contracts), OPTION_MIN)"),
    ("fees/services/regulatory.py", "from ..money import ZERO, half_up", "from ..money import ZERO, always_up"),
    ("fees/services/regulatory.py", "    return half_up(notional(trade) * REG_FEE_RATE)", "    return always_up(notional(trade) * REG_FEE_RATE)"),
    ("fees/services/statements.py", "if start <= t.executed_at.date() <= end]", "if start <= t.executed_at.date() < end]"),
    ("fees/services/statements.py",
     "        for number, trade in enumerate(self.trades_in_month(account_id, year, month), start=1):\n            if trade.status != ACTIVE:\n                continue\n",
     "        active = [t for t in self.trades_in_month(account_id, year, month) if t.status == ACTIVE]\n"
     "        for number, trade in enumerate(active, start=1):\n"),
]
