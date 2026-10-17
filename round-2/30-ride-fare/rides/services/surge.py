from decimal import Decimal

from ..config import SURGE_CAP


class SurgeFeed:
    def __init__(self):
        self._zones = {}

    def set(self, zone: str, multiplier) -> None:
        self._zones[zone] = Decimal(str(multiplier))

    def current(self, zone: str) -> Decimal:
        return min(self._zones.get(zone, Decimal("1.0")), SURGE_CAP)
