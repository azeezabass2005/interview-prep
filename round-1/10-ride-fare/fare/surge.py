from decimal import Decimal


class SurgeFeed:
    """Live surge multipliers per zone, updated by the pricing team every minute."""

    def __init__(self, multipliers=None):
        self._multipliers = dict(multipliers or {})

    def set(self, zone: str, multiplier) -> None:
        self._multipliers[zone] = Decimal(multiplier)

    def multiplier(self, zone: str) -> Decimal:
        return self._multipliers.get(zone, Decimal("1.0"))
