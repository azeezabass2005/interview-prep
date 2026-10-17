from decimal import Decimal

from ..config import TIERS_PER_30_DAYS


def tier_sizes(days: int):
    return [None if size is None else size for size, _ in TIERS_PER_30_DAYS]


def energy_charge(kwh: int, days: int) -> Decimal:
    charge = Decimal("0")
    remaining = kwh
    for size, (_, rate) in zip(tier_sizes(days), TIERS_PER_30_DAYS):
        if remaining <= 0:
            break
        take = remaining if size is None else min(remaining, size)
        charge += take * rate
        remaining -= take
    return charge
