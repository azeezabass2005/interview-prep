import unittest
from decimal import Decimal as D

from utility.billing import SolarAccount
from tests.helpers import reading


class HiddenSolar(unittest.TestCase):
    def test_B1_tiers_on_net_usage(self):
        self.assertEqual(SolarAccount("A").bill(reading(1, 700, 100)).total, D("90.75"))

    def test_B2_bank_offsets_kwh_before_tiers(self):
        account = SolarAccount("A")
        account.bill(reading(5, 300, 450))
        self.assertEqual(account.bill(reading(6, 900, 100)).total, D("98.63"))

    def test_B3_fixed_charge_not_taxed(self):
        self.assertEqual(SolarAccount("A").bill(reading(5, 300, 450)).total, D("12.00"))

    def test_B4_bank_is_consumed(self):
        account = SolarAccount("A")
        account.bill(reading(5, 300, 450))
        account.bill(reading(6, 900, 100))
        self.assertEqual(account.bill(reading(7, 300)).total, D("49.80"))

    def test_G1_december_true_up(self):
        account = SolarAccount("A")
        account.bill(reading(11, 100, 300))
        december = account.bill(reading(12, 50, 50))
        self.assertEqual(december.true_up_payout, D("8.00"))
        self.assertEqual(account.bank_kwh, 0)

    def test_G2_months_in_order(self):
        account = SolarAccount("A")
        account.bill(reading(5, 300))
        with self.assertRaises(Exception):
            account.bill(reading(3, 300))
