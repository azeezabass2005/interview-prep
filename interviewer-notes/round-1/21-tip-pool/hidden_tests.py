import unittest
from decimal import Decimal as D

from tips.models import NightTips, Shift
from tips.pool import distribute, pool_amount


def s(name, role, hours):
    return Shift(name, role, D(str(hours)))


EXAMPLE = [s("alice", "SERVER", 6), s("bob", "BARTENDER", 5), s("cara", "BUSSER", 4),
           s("dan", "MANAGER", 8), s("eve", "HOST", 1.5)]


class HiddenTips(unittest.TestCase):
    def test_B1_cash_tips_not_charged_fee(self):
        self.assertEqual(pool_amount(NightTips(D("1000"), D("200"))), D("1170.00"))

    def test_B2_managers_never_paid(self):
        shares = distribute(NightTips(D("1000"), D("0")), EXAMPLE)
        self.assertNotIn("dan", shares)

    def test_B3_exactly_two_hours_is_eligible(self):
        shares = distribute(NightTips(D("100"), D("0")), [s("a", "SERVER", 5), s("c", "BUSSER", 2)])
        self.assertIn("c", shares)

    def test_B4_multi_role_weights_add_up(self):
        shifts = [s("fay", "BUSSER", 3), s("fay", "SERVER", 3), s("gus", "SERVER", 3)]
        shares = distribute(NightTips(D("0"), D("100")), shifts)
        self.assertEqual(shares, {"fay": D("60.00"), "gus": D("40.00")})

    def test_B5_leftover_cents_by_largest_remainder(self):
        shares = distribute(NightTips(D("0"), D("1")), [s("a", "SERVER", 2), s("b", "SERVER", 4)])
        self.assertEqual(shares, {"a": D("0.33"), "b": D("0.67")})
