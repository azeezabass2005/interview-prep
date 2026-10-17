FIXES = [
    ("fx.py", "        return self.rates[source] / self.rates[target]", "        return self.rates[target] / self.rates[source]"),
    ("fx.py", "* (1 + SPREAD)", "* (1 - SPREAD)"),
    ("fx.py", "        receive = (amount * rate).quantize(Decimal(\"0.01\"), rounding=ROUND_DOWN)",
     "        receive = (amount * rate).quantize(Decimal(1).scaleb(-MINOR_UNITS[target]), rounding=ROUND_DOWN)"),
    ("fx.py", "        if now >= quote[\"expires_at\"]:", "        if now > quote[\"expires_at\"]:"),
    ("fx.py", "        usd = quote[\"amount\"]\n", "        usd = quote[\"amount\"] * quote[\"usd_mid\"]\n"),
]
