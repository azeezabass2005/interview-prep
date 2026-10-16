FIXES = [
    ("margin/services/valuation.py", "        base = sum((qty * p.price for _, qty, p in raw), ZERO)",
     "        base = sum((qty * p.price for _, qty, p in raw if qty > 0), ZERO)"),
    ("margin/services/valuation.py",
     """                if p.on < run_date - timedelta(days=1):
                    haircut += STALE_SURCHARGE
                if base > 0 and mv / base > CONCENTRATION_LIMIT:
                    haircut = max(haircut, CONCENTRATED_HAIRCUT)""",
     """                if base > 0 and mv / base > CONCENTRATION_LIMIT:
                    haircut = max(haircut, CONCENTRATED_HAIRCUT)
                if p.on < run_date - timedelta(days=1):
                    haircut += STALE_SURCHARGE"""),
    ("margin/services/valuation.py", "abs(l.market_value) * SHORT_ADD_ON for l", "abs(l.market_value) * (1 + SHORT_ADD_ON) for l"),
    ("margin/services/calls.py", "from decimal import ROUND_HALF_UP, Decimal", "from decimal import ROUND_CEILING, Decimal"),
    ("margin/services/calls.py", "rounding=ROUND_HALF_UP) * CALL_ROUNDING", "rounding=ROUND_CEILING) * CALL_ROUNDING"),
    ("margin/services/calls.py", "        deposited = sum((d.amount for d in self._store.deposits[account_id]), Decimal(\"0\"))",
     "        deposited = sum((d.amount for d in self._store.deposits[account_id] if d.on >= call.issued_on), Decimal(\"0\"))"),
]
