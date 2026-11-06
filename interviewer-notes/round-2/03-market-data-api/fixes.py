FIXES = [
    ("quotes/wiring.py",
     '''        middleware.rate_limit(PlanLimiter(clock), limit_key),
        middleware.authenticate(auth, public_paths={"/health"}),''',
     '''        middleware.authenticate(auth, public_paths={"/health"}),
        middleware.rate_limit(PlanLimiter(clock), limit_key),'''),
    ("quotes/services/quotes.py", "self._quotes = TTLCache(clock, QUOTE_TTL_MS)", "self._quotes = TTLCache(clock, QUOTE_TTL_MS / 1000)"),
    ("quotes/services/quotes.py",
     '''        quote.price = round(quote.price * rate, 4)
        quote.currency = currency
        return quote''',
     '''        return replace(quote, price=round(quote.price * rate, 4), currency=currency)'''),
    ("quotes/services/quotes.py", "from datetime import date\n", "from dataclasses import replace\nfrom datetime import date\n"),
    ("quotes/repositories/instruments.py",
     '''            f"SELECT * FROM instruments WHERE name LIKE '%{text}%' OR symbol LIKE '{text.upper()}%' "
            f"ORDER BY symbol LIMIT {int(limit)}"
        )''',
     '''            "SELECT * FROM instruments WHERE name LIKE ? OR symbol LIKE ? ORDER BY symbol LIMIT ?",
            (f"%{text}%", f"{text.upper()}%", int(limit)),
        )'''),
    ("quotes/wiring.py",
     '''        middleware.errors(logger),
        middleware.access_log(logger, metrics, clock),''',
     '''        middleware.access_log(logger, metrics, clock),
        middleware.errors(logger),'''),
]
GROUPS = [[0], [1], [2, 3], [4], [5]]
