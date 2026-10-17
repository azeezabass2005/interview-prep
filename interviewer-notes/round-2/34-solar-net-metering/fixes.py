FIXES = [
    ("utility/services/meters.py", "    return current - previous", "    return (current - previous) % REGISTER_MAX"),
    ("utility/services/tariff.py", "    return [None if size is None else size for size, _ in TIERS_PER_30_DAYS]",
     "    return [None if size is None else size * days // 30 for size, _ in TIERS_PER_30_DAYS]"),
    ("utility/services/billing.py", "            used = min(account.bank_kwh, net)\n",
     "            used = min(account.bank_kwh, net)\n            account.bank_kwh -= used\n"),
    ("utility/services/billing.py", "tax = cents((energy + service) * TAX_RATE)", "tax = cents(energy * TAX_RATE)"),
    ("utility/services/billing.py", "if previous.read_on.month == TRUE_UP_MONTH:", "if reading.read_on.month == TRUE_UP_MONTH:"),
]
