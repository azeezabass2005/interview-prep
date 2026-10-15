from decimal import Decimal

MILES_PER_DOLLAR = 5

TIER_MULTIPLIER = {
    "BASE": Decimal("1.00"),
    "SILVER": Decimal("1.25"),
    "GOLD": Decimal("1.50"),
    "PLATINUM": Decimal("2.00"),
}


def miles_for_fare(fare: Decimal, tier: str) -> int:
    base = int(fare * MILES_PER_DOLLAR)
    if tier == "BASE":
        return base
    bonus = int(base * TIER_MULTIPLIER[tier])
    return base + bonus
