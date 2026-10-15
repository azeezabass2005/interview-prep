import unittest
from decimal import Decimal as D

from crowd.models import PledgeRejected
from tests.helpers import campaign


class TestPledges(unittest.TestCase):
    def test_below_minimum_rejected(self):
        _, c = campaign()
        with self.assertRaises(PledgeRejected):
            c.pledge("ann", "DELUXE", "99")

    def test_unknown_tier(self):
        _, c = campaign()
        with self.assertRaises(PledgeRejected):
            c.pledge("ann", "GOLD", "500")

    def test_cancel_frees_limited_slot(self):
        _, c = campaign(deluxe_limit=1)
        p = c.pledge("ann", "DELUXE", "100")
        c.cancel(p.pledge_id)
        c.pledge("bob", "DELUXE", "100")


class TestClose(unittest.TestCase):
    def test_not_funded(self):
        _, c = campaign()
        c.pledge("ann", "STANDARD", "500")
        outcome = c.close()
        self.assertFalse(outcome.funded)
        self.assertEqual(outcome.payout, D("0.00"))
        self.assertEqual(outcome.charged, [])

    def test_funded_over_goal(self):
        _, c = campaign()
        c.pledge("ann", "DELUXE", "1500")
        self.assertTrue(c.close().funded)


if __name__ == "__main__":
    unittest.main()
