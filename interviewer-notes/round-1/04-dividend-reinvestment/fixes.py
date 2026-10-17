FIXES = [
    ("drip.py", "self.shares_on(account, symbol, pay_date)", "self.shares_on(account, symbol, record_date)"),
    ("drip.py", "WITHHOLDING.get(self.countries[account], Decimal(\"0\"))", "WITHHOLDING.get(self.countries[account], DEFAULT_WITHHOLDING)"),
    ("drip.py", "(net / price).quantize(SHARE_UNIT, rounding=ROUND_HALF_UP)", "(net / price).quantize(SHARE_UNIT, rounding=ROUND_DOWN)"),
    ("drip.py", "                cash = Decimal(\"0.00\")\n", "                cash = (net - bought * price).quantize(CENT, rounding=ROUND_DOWN)\n"),
    ("drip.py", "        return history[-1][1] if history else False",
     "        state = False\n        for when, enrolled in sorted(history, key=lambda h: h[0]):\n            if when <= on:\n                state = enrolled\n        return state"),
]
