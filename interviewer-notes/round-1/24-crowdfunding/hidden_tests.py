import unittest
from datetime import datetime

from crowd.app import build_app
from crowd.payments import FakePayments


class FakeClock:
    def __init__(self):
        self.current = datetime(2026, 6, 1)

    def now(self):
        return self.current


def campaign(deluxe_limit=50, failing=()):
    clock = FakeClock()
    payments = FakePayments(failing)
    api, _ = build_app(clock, payments)
    api.create({"id": "c", "goal": "1000", "deadline": "2026-07-01T00:00",
                "tiers": [{"name": "STANDARD", "minimum": "35"}, {"name": "DELUXE", "minimum": "100", "limit": deluxe_limit}]})
    return api, clock, payments


def settle(api, clock):
    clock.current = datetime(2026, 7, 1)
    return api.settle("c")[1]


class HiddenCrowd(unittest.TestCase):
    def test_B1_tier_limit_exact(self):
        api, _, _ = campaign(deluxe_limit=2)
        api.pledge("c", {"backer": "a", "tier": "DELUXE", "amount": "100"})
        api.pledge("c", {"backer": "b", "tier": "DELUXE", "amount": "100"})
        self.assertEqual(api.pledge("c", {"backer": "x", "tier": "DELUXE", "amount": "100"})[0], 409)

    def test_B2_cancelled_pledges_ignored(self):
        api, clock, payments = campaign()
        api.pledge("c", {"backer": "a", "tier": "DELUXE", "amount": "900"})
        pid = api.pledge("c", {"backer": "b", "tier": "DELUXE", "amount": "200"})[1]["pledge_id"]
        api.cancel("c", pid)
        self.assertFalse(settle(api, clock)["funded"])
        self.assertEqual(payments.charges, [])

    def test_B3_goal_reached_exactly(self):
        api, clock, _ = campaign()
        api.pledge("c", {"backer": "a", "tier": "DELUXE", "amount": "1000"})
        self.assertTrue(settle(api, clock)["funded"])

    def test_B4_fee_only_for_successful_charges(self):
        api, clock, _ = campaign(failing={"s0"})
        for i in range(20):
            api.pledge("c", {"backer": f"s{i}", "tier": "STANDARD", "amount": "35"})
        for i in range(5):
            api.pledge("c", {"backer": f"d{i}", "tier": "DELUXE", "amount": "100"})
        result = settle(api, clock)
        self.assertEqual((result["collected"], result["payout"]), ("1165.00", "1067.00"))

    def test_B5_cannot_change_into_sold_out_tier(self):
        api, _, _ = campaign(deluxe_limit=1)
        api.pledge("c", {"backer": "ann", "tier": "DELUXE", "amount": "100"})
        pid = api.pledge("c", {"backer": "bob", "tier": "STANDARD", "amount": "35"})[1]["pledge_id"]
        self.assertEqual(api.change("c", pid, {"tier": "DELUXE", "amount": "100"})[0], 409)
