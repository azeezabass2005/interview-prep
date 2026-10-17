import unittest
from decimal import Decimal

from tab import GroupTab, TabError

D = Decimal


class HiddenTab(unittest.TestCase):
    def setUp(self):
        self.tab = GroupTab(["ana", "ben", "cai"])

    def test_B1_equal_split_leftover_cents(self):
        e = self.tab.add_expense("ana", "10.00", ["ana", "ben", "cai"])
        self.assertEqual(e.shares, {"ana": D("3.34"), "ben": D("3.33"), "cai": D("3.33")})

    def test_B2_exact_amounts_must_add_up(self):
        with self.assertRaises(TabError):
            self.tab.add_expense("ana", "10.00", ["ben", "cai"], "EXACT", ["6.00", "3.00"])

    def test_B3_shares_divide_by_total_shares(self):
        e = self.tab.add_expense("ana", "30.00", ["ben", "cai"], "SHARES", [2, 1])
        self.assertEqual(e.shares, {"ben": D("20.00"), "cai": D("10.00")})

    def test_B4_payment_reduces_debt(self):
        self.tab.add_expense("ben", "30.00", ["ana", "ben"])
        self.tab.pay("ana", "ben", "15.00")
        self.assertEqual(self.tab.balances(), {"ana": D("0.00"), "ben": D("0.00"), "cai": D("0.00")})

    def test_B5_deleted_expense_ignored(self):
        e = self.tab.add_expense("ana", "30.00", ["ana", "ben", "cai"])
        self.tab.delete_expense(e.expense_id)
        self.assertEqual(self.tab.settle_up(), [])
