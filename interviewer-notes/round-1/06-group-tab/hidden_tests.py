import unittest

from tab.calculator import compute_breakdown, settle_up
from tab.models import Bill, Item
from tests.helpers import example_bill


class HiddenTab(unittest.TestCase):
    def test_B1_shares_add_up_to_total(self):
        b = compute_breakdown(example_bill())
        self.assertEqual(sum(b.shares.values()), b.total)

    def test_B2_tip_on_pre_tax_subtotal(self):
        self.assertEqual(compute_breakdown(example_bill()).tip, 1116)

    def test_B3_six_people_get_auto_gratuity(self):
        people = ["p1", "p2", "p3", "p4", "p5", "p6"]
        bill = Bill([Item(f"dish-{p}", 1000, (p,)) for p in people], payer="p1")
        self.assertEqual(compute_breakdown(bill).tip_percent, 20)

    def test_B4_coupon_applies_before_tax(self):
        self.assertEqual(compute_breakdown(example_bill(coupon_cents=1000)).tax, 462)

    def test_B5_payer_sends_nothing(self):
        senders = [t.sender for t in settle_up(example_bill())]
        self.assertNotIn("alice", senders)
        self.assertEqual(sorted(senders), ["bob", "carol"])
