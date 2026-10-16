from decimal import Decimal
from typing import Tuple

from ..config import MILES_PER_DOLLAR, TIER_MULTIPLIER


def miles_for(base_fare: Decimal, tier: str) -> Tuple[int, int]:
    base = int(base_fare) * MILES_PER_DOLLAR
    bonus = int(base * TIER_MULTIPLIER[tier]) if tier != "BASE" else 0
    return base, bonus
