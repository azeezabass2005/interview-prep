from decimal import Decimal

INCREMENTS = [
    (Decimal("100"), Decimal("5")),
    (Decimal("500"), Decimal("10")),
    (None, Decimal("25")),
]
PREMIUM_RATE = Decimal("0.10")
SOFT_CLOSE_SECONDS = 120
