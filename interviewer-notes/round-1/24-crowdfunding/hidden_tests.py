import unittest
from datetime import datetime
from decimal import Decimal as D

from tests.helpers import campaign


class HiddenCrowd(unittest.TestCase):
    def test_B1_tier_limit_is_exact(self):
        _, c = campaign(deluxe_limit=2)
        c.pledge("a", "DELUXE", "100")
        c.pledge("b", "DELUXE", "100")
        with self.assertRaises(Exception):
            c.pledge("c", "DELUXE", "100")

    def test_B2_cancelled_pledges_do_not_count(self):
        _, c = campaign()
        c.pledge("a", "DELUXE", "900")
        p = c.pledge("b", "DELUXE", "200")
        c.cancel(p.pledge_id)
        self.assertFalse(c.close().funded)

    def test_B3_reaching_goal_exactly_funds(self):
        _, c = campaign()
        c.pledge("a", "DELUXE", "1000")
        self.assertTrue(c.close().funded)

    def test_B4_no_fees_when_not_funded(self):
        _, c = campaign()
        c.pledge("a", "STANDARD", "500")
        outcome = c.close()
        self.assertEqual((outcome.platform_fee, outcome.processing_fee), (D("0.00"), D("0.00")))

    def test_B5_spec_example_payout(self):
        _, c = campaign()
        for i in range(20):
            c.pledge(f"s{i}", "STANDARD", "35")
        for i in range(5):
            c.pledge(f"d{i}", "DELUXE", "100")
        outcome = c.close()
        self.assertEqual(outcome.processing_fee, D("41.00"))
        self.assertEqual(outcome.payout, D("1099.00"))

    def test_G1_no_pledges_after_deadline(self):
        clock, c = campaign()
        clock.current = datetime(2026, 7, 1, 0, 1)
        with self.assertRaises(Exception):
            c.pledge("late", "STANDARD", "35")
