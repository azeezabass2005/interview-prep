FIXES = [
    ("margin/calc.py", "from decimal import ROUND_HALF_UP, Decimal", "from decimal import ROUND_CEILING, Decimal"),
    ("margin/calc.py", "    base_value = sum((p.market_value for p in account.positions), ZERO)",
     "    base_value = sum((p.market_value for p in account.positions if p.is_long), ZERO)"),
    ("margin/calc.py", "p.market_value / base_value >= CONCENTRATION_LIMIT", "p.market_value / base_value > CONCENTRATION_LIMIT"),
    ("margin/calc.py", "    return sum((p.market_value * (1 - cuts[p.symbol]) for p in account.positions if p.is_long), ZERO)",
     "    longs = sum((p.market_value * (1 - cuts[p.symbol]) for p in account.positions if p.is_long), ZERO)\n"
     "    return longs + max(account.cash, ZERO)"),
    ("margin/calc.py", "abs(p.market_value) * SHORT_REQUIREMENT for p", "abs(p.market_value) * (1 + SHORT_REQUIREMENT) for p"),
    ("margin/calc.py", "quantize(Decimal(\"1\"), rounding=ROUND_HALF_UP)", "quantize(Decimal(\"1\"), rounding=ROUND_CEILING)"),
    ("margin/liquidation.py", "longs.sort(key=lambda p: (cuts[p.symbol], p.market_value))",
     "longs.sort(key=lambda p: (-cuts[p.symbol], -p.market_value))"),
]
