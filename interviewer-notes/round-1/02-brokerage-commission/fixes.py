FIXES = [
    ("fees/commission.py",
     '''    for upper, rate in TIERS:
        if upper is None or notional <= upper:
            return notional * rate
    raise AssertionError("unreachable: last tier is unbounded")''',
     '''    total = Decimal("0")
    lower = Decimal("0")
    for upper, rate in TIERS:
        top = notional if upper is None else min(notional, upper)
        if top > lower:
            total += (top - lower) * rate
        if upper is None or notional <= upper:
            return total
        lower = upper
    raise AssertionError("unreachable: last tier is unbounded")'''),
    ("fees/commission.py", "return max(fee, MIN_COMMISSION)", "return min(max(fee, MIN_COMMISSION), MAX_COMMISSION)"),
    ("fees/commission.py", "from .schedule import CENT, MIN_COMMISSION,", "from .schedule import CENT, MAX_COMMISSION, MIN_COMMISSION,"),
    ("fees/commission.py", "from decimal import ROUND_HALF_UP, Decimal", "from decimal import ROUND_HALF_UP, ROUND_UP, Decimal"),
    ("fees/commission.py", "(notional * REG_FEE_RATE).quantize(CENT, rounding=ROUND_HALF_UP)", "(notional * REG_FEE_RATE).quantize(CENT, rounding=ROUND_UP)"),
    ("fees/statement.py", "if i > VOLUME_DISCOUNT_FROM_TRADE - 1:", "if i >= VOLUME_DISCOUNT_FROM_TRADE - 1:"),
    ("fees/statement.py", "account_trades = [t for t in trades if t.account == account]",
     "account_trades = sorted((t for t in trades if t.account == account), key=lambda t: t.executed_at)"),
]
