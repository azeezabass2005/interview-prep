FIXES = [
    ("fx/services/rates.py", "                raise Rejected(f\"{pair} rate is stale\")\n            return rate",
     "                raise Rejected(f\"{pair} rate is stale\")\n            return rate if base == currency else 1 / rate"),
    ("fx/services/quotes.py", "        spread = spread_for(amount)", "        spread = spread_for(usd_equivalent)"),
    ("fx/services/quotes.py", "from decimal import ROUND_HALF_UP, Decimal, InvalidOperation", "from decimal import ROUND_DOWN, Decimal, InvalidOperation"),
    ("fx/services/quotes.py", ".quantize(unit, rounding=ROUND_HALF_UP)", ".quantize(unit, rounding=ROUND_DOWN)"),
    ("fx/services/payments.py", "        if quote.booked:\n", "        if self._clock.now() - quote.created_at > QUOTE_TTL:\n            raise Rejected(\"quote expired\")\n        if quote.booked:\n"),
    ("fx/services/payments.py", "            if payment.booked_at.date() == today:", "            if payment.status == BOOKED and payment.booked_at.date() == today:"),
]
