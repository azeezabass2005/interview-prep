FIXES = [
    ("fx/currencies.py", '    "CHF": 2,\n', '    "CHF": 2,\n    "JPY": 0,\n'),
    ("fx/rates.py",
     "            if base == currency and quote == \"USD\":\n                return rate\n"
     "            if base == \"USD\" and quote == currency:\n                return rate\n",
     "            if currency not in (base, quote) or \"USD\" not in (base, quote):\n                continue\n"
     "            if self._clock.now() - at > MAX_AGE:\n                raise StaleRate(f\"{pair} is stale\")\n"
     "            return rate if base == currency else 1 / rate\n"),
    ("fx/convert.py", "from decimal import ROUND_HALF_UP, Decimal", "from decimal import ROUND_DOWN, Decimal"),
    ("fx/convert.py", "spread = spread_for(amount)", "spread = spread_for(amount * source_usd)"),
    ("fx/convert.py", "raw.quantize(exponent, rounding=ROUND_HALF_UP)", "raw.quantize(exponent, rounding=ROUND_DOWN)"),
]
