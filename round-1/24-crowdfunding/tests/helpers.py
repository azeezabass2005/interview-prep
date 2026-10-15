from datetime import datetime
from decimal import Decimal as D

from crowd.campaign import Campaign
from crowd.models import Tier

DEADLINE = datetime(2026, 7, 1, 0, 0)


class FakeClock:
    def __init__(self, now=datetime(2026, 6, 1, 12, 0)):
        self.current = now

    def now(self):
        return self.current


def campaign(goal="1000", deluxe_limit=50):
    clock = FakeClock()
    tiers = [Tier("STANDARD", D("35")), Tier("DELUXE", D("100"), deluxe_limit)]
    return clock, Campaign(goal, DEADLINE, tiers, clock)
