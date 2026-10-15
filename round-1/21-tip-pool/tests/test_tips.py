import unittest
from decimal import Decimal as D

from tips.models import NightTips, Shift
from tips.pool import distribute, pool_amount


def s(name, role, hours):
    return Shift(name, role, D(str(hours)))


class TestTips(unittest.TestCase):
    def test_card_fee_on_card_only_tips(self):
        self.assertEqual(pool_amount(NightTips(D("1000"), D("0"))), D("970.00"))

    def test_two_servers_split_evenly(self):
        shares = distribute(NightTips(D("100"), D("0")), [s("a", "SERVER", 5), s("b", "SERVER", 5)])
        self.assertEqual(shares, {"a": D("48.50"), "b": D("48.50")})

    def test_short_shift_excluded(self):
        shares = distribute(NightTips(D("100"), D("0")), [s("a", "SERVER", 5), s("e", "HOST", 1.5)])
        self.assertEqual(list(shares), ["a"])

    def test_unknown_role(self):
        with self.assertRaises(ValueError):
            distribute(NightTips(D("1"), D("0")), [s("a", "SOMMELIER", 3)])

    def test_nobody_eligible(self):
        self.assertEqual(distribute(NightTips(D("50"), D("0")), [s("e", "HOST", 1)]), {})


if __name__ == "__main__":
    unittest.main()
