from decimal import Decimal

MILES_PER_DOLLAR = 5
TIER_THRESHOLDS = [("PLATINUM", 75_000), ("GOLD", 50_000), ("SILVER", 25_000), ("BASE", 0)]
TIER_MULTIPLIER = {"BASE": Decimal("1.00"), "SILVER": Decimal("1.25"), "GOLD": Decimal("1.50"), "PLATINUM": Decimal("2.00")}
EXPIRY_YEARS = 2
MIN_TRANSFER = 1_000
