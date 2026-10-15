import unittest

from tab.allocation import split_evenly
from tab.calculator import compute_breakdown, settle_up
from tab.models import Bill, Item
from tests.helpers import example_bill


class TestSplitEvenly(unittest.TestCase):
    def test_leftover_cents_alphabetical(self):
        self.assertEqual(split_evenly(1000, ["carol", "alice", "bob"]),
                         {"alice": 334, "bob": 333, "carol": 333})


class TestBreakdown(unittest.TestCase):
    def test_example_subtotals_and_tax(self):
        b = compute_breakdown(example_bill())
        self.assertEqual(b.subtotals, {"alice": 2000, "bob": 2000, "carol": 2200})
        self.assertEqual(b.subtotal, 6200)
        self.assertEqual(b.tax, 550)

    def test_solo_diner(self):
        b = compute_breakdown(Bill([Item("soup", 1000, ("dan",))], payer="dan", tip_percent=0))
        self.assertEqual(b.tax, 89)  # 88.75 rounds half-up
        self.assertEqual(b.total, 1089)

    def test_item_needs_sharers(self):
        with self.assertRaises(ValueError):
            Item("ghost", 500, ())


class TestSettleUp(unittest.TestCase):
    def test_bob_pays_alice(self):
        transfers = {t.sender: t for t in settle_up(example_bill(tip_percent=0))}
        self.assertEqual(transfers["bob"].receiver, "alice")
        self.assertGreater(transfers["bob"].amount_cents, 2000)


if __name__ == "__main__":
    unittest.main()
