from decimal import Decimal

# (upper kWh bound of the band, $/kWh). None = unbounded.
TIERS = [
    (500, Decimal("0.12")),
    (1000, Decimal("0.15")),
    (None, Decimal("0.20")),
]
FIXED_CHARGE = Decimal("12.00")
TAX_RATE = Decimal("0.05")
TRUE_UP_RATE = Decimal("0.04")
TRUE_UP_MONTH = 12
