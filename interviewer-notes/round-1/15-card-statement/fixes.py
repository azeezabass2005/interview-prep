FIXES = [
    ("card/statement.py", 'PAYMENT_ORDER = ["purchase", "cash"]', 'PAYMENT_ORDER = sorted(APR, key=APR.get, reverse=True)'),
    ("card/statement.py", "return cents(min(amount * CASH_FEE_RATE, CASH_FEE_MIN))", "return cents(max(amount * CASH_FEE_RATE, CASH_FEE_MIN))"),
    ("card/statement.py", "average = daily_sum[bucket] / STANDARD_CYCLE_DAYS", "average = daily_sum[bucket] / cycle.days"),
    ("card/statement.py", "if cycle.paid_in_full_last_cycle:", "if bucket == \"purchase\" and cycle.paid_in_full_last_cycle:"),
    ("card/statement.py",
     "    minimum = max(MIN_PAYMENT_FLOOR, cents(new_balance * MIN_PAYMENT_PERCENT) + total_interest)\n",
     "    minimum = max(MIN_PAYMENT_FLOOR, cents(new_balance * MIN_PAYMENT_PERCENT) + total_interest)\n"
     "    minimum = max(min(minimum, new_balance), Decimal(\"0.00\"))\n"),
]
