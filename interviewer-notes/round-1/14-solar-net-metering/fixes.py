FIXES = [
    ("netmeter.py", "    return current - previous", "    return (current - previous) % ROLLOVER"),
    ("netmeter.py", "        threshold = TIER_KWH\n", "        threshold = round(Decimal(TIER_KWH * days) / TIER_DAYS)\n"),
    ("netmeter.py", "            charged = net - banked_used", "            account.bank -= banked_used\n            charged = net - banked_used"),
    ("netmeter.py", "        return (account.bank * TRUE_UP_RATE).quantize(CENT, rounding=ROUND_HALF_UP)",
     "        payout = (account.bank * TRUE_UP_RATE).quantize(CENT, rounding=ROUND_HALF_UP)\n        account.bank = 0\n        return payout"),
    ("netmeter.py", "            account.bank += exported", "            account.bank += -net"),
]
