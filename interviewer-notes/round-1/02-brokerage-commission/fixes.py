FIXES = [
    ("commission.py", "        return max(min(raw, cap), MIN_COMMISSION).quantize(CENT, ROUND_HALF_UP)",
     "        return min(max(raw, MIN_COMMISSION), cap).quantize(CENT, ROUND_HALF_UP)"),
    ("commission.py", "        rate = low_rate if done < threshold else BANDS[1][1]\n        raw = trade.quantity * rate",
     "        first = max(0, min(trade.quantity, threshold - done))\n        raw = first * low_rate + (trade.quantity - first) * BANDS[1][1]"),
    ("commission.py", "from decimal import ROUND_HALF_UP, Decimal", "from decimal import ROUND_HALF_UP, ROUND_UP, Decimal"),
    ("commission.py", "rounding=ROUND_HALF_UP)", "rounding=ROUND_UP)"),
    ("commission.py", "if t.kind == \"EQUITY\" and t.month == month)",
     "if t.kind == \"EQUITY\" and t.month == month and t.account == account and not t.busted)"),
]
