import unittest
from datetime import datetime, timedelta
from decimal import Decimal

from crowd import Platform

DEADLINE = datetime(2026, 9, 30, 23, 59)
EARLY = datetime(2026, 9, 1)
AFTER = DEADLINE + timedelta(minutes=1)


class Gateway:
    def __init__(self, script=None):
        self.script = {k: list(v) for k, v in (script or {}).items()}

    def charge(self, backer, amount):
        results = self.script.get(backer)
        return results.pop(0) if results else True


class HiddenCrowd(unittest.TestCase):
    def test_B1_cancel_frees_tier_slot(self):
        p = Platform(Gateway())
        p.create("c", 1000, DEADLINE, [("EARLY", 50, 1)])
        p.pledge("c", "ana", 60, EARLY, "EARLY")
        p.cancel("c", "ana", EARLY)
        p.pledge("c", "ben", 60, EARLY, "EARLY")
        self.assertEqual(p.campaigns["c"].tiers["EARLY"].taken, 1)

    def test_B2_goal_exactly_met_is_funded(self):
        p = Platform(Gateway())
        p.create("c", 1000, DEADLINE)
        p.pledge("c", "ana", 1000, EARLY)
        self.assertTrue(p.settle("c", AFTER)["funded"])

    def test_B3_no_pledges_at_the_deadline(self):
        p = Platform(Gateway())
        p.create("c", 1000, DEADLINE)
        with self.assertRaises(Exception):
            p.pledge("c", "ana", 100, DEADLINE)

    def test_B4_fixed_fee_only_for_successful_charges(self):
        p = Platform(Gateway({"ben": [False, False]}))
        p.create("c", 100, DEADLINE)
        p.pledge("c", "ana", 100, EARLY)
        p.pledge("c", "ben", 50, EARLY)
        self.assertEqual(p.settle("c", AFTER)["processing_fee"], Decimal("3.20"))

    def test_B5_declined_charge_retried_once(self):
        p = Platform(Gateway({"ana": [False, True]}))
        p.create("c", 100, DEADLINE)
        p.pledge("c", "ana", 100, EARLY)
        result = p.settle("c", AFTER)
        self.assertEqual((result["collected"], result["failed"]), (Decimal("100"), []))
