from decimal import Decimal

EQUITY_TIERS = [
    (Decimal("10000"), Decimal("0.0010")),
    (Decimal("50000"), Decimal("0.0005")),
    (None, Decimal("0.0002")),
]
EQUITY_MIN = Decimal("1.00")
EQUITY_MAX = Decimal("50.00")

OPTION_PER_CONTRACT = Decimal("0.65")
OPTION_MIN = Decimal("1.00")
OPTION_MULTIPLIER = 100

REG_FEE_RATE = Decimal("0.0000278")

VOLUME_DISCOUNT_FROM = 51
VOLUME_DISCOUNT_RATE = Decimal("0.20")
