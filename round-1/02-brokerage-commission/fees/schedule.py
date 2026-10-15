"""Published fee schedule. All amounts are Decimal dollars."""
from decimal import Decimal

# (upper bound of the band, rate). None = no upper bound.
TIERS = [
    (Decimal("10000"), Decimal("0.0010")),
    (Decimal("50000"), Decimal("0.0005")),
    (None, Decimal("0.0002")),
]

MIN_COMMISSION = Decimal("1.00")
MAX_COMMISSION = Decimal("50.00")

VOLUME_DISCOUNT_FROM_TRADE = 51  # 1-based trade number within the month
VOLUME_DISCOUNT_RATE = Decimal("0.20")

REG_FEE_RATE = Decimal("0.0000278")

CENT = Decimal("0.01")
ZERO = Decimal("0.00")
