from decimal import Decimal

REGISTER_MAX = 100_000
TIERS_PER_30_DAYS = [(500, Decimal("0.12")), (500, Decimal("0.15")), (None, Decimal("0.20"))]
DAILY_SERVICE = Decimal("0.40")
TAX_RATE = Decimal("0.05")
TRUE_UP_RATE = Decimal("0.04")
TRUE_UP_MONTH = 12
