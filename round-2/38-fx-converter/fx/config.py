from datetime import timedelta
from decimal import Decimal

MINOR_UNITS = {"USD": 2, "EUR": 2, "GBP": 2, "CHF": 2, "JPY": 0, "KWD": 3}
SPREAD_TIERS = [(Decimal("10000"), Decimal("0.0100")), (Decimal("100000"), Decimal("0.0050")), (None, Decimal("0.0025"))]
RATE_MAX_AGE = timedelta(seconds=60)
QUOTE_TTL = timedelta(seconds=30)
DAILY_LIMIT_USD = Decimal("50000")
CANCEL_WINDOW = timedelta(minutes=30)
