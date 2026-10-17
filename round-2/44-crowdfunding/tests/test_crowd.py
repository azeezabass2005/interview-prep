import unittest
from datetime import datetime

from crowd.app import build_app


class FakeClock:
    def __init__(self, now):
        self.current = now

    def now(self):
        return self.current


class TestCrowd(unittest.TestCase):
    def test_unfunded_campaign_charges_nobody(self):
        clock = FakeClock(datetime(2026, 6, 1))
        api, payments = build_app(clock)
        api.create({"id": "c", "goal": "1000", "deadline": "2026-07-01T00:00", "tiers": [{"name": "STANDARD", "minimum": "35"}]})
        api.pledge("c", {"backer": "ann", "tier": "STANDARD", "amount": "500"})
        clock.current = datetime(2026, 7, 1)
        status, result = api.settle("c")
        self.assertEqual((status, result["funded"]), (200, False))
        self.assertEqual(payments.charges, [])


if __name__ == "__main__":
    unittest.main()
