FIXES = [
    ("card/services/posting.py", "PAYMENT_ORDER = sorted(APR, key=APR.get)", "PAYMENT_ORDER = sorted(APR, key=APR.get, reverse=True)"),
    ("card/services/posting.py", "    return min(amount * CASH_FEE_RATE, CASH_FEE_MIN)", "    return max(amount * CASH_FEE_RATE, CASH_FEE_MIN)"),
    ("card/services/cycle.py", "start <= t.posted_on < end)", "start <= t.posted_on <= end)"),
    ("card/services/cycle.py", "            if grace:\n", "            if grace and bucket == \"purchase\":\n"),
    ("card/services/cycle.py", "cents(daily_sum[bucket] / 30 * apr", "cents(daily_sum[bucket] / days * apr"),
]
