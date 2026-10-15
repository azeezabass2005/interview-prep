import unittest
from decimal import Decimal as D

from utility.billing import SolarAccount, tiered_energy_charge
from tests.helpers import reading


class TestTiers(unittest.TestCase):
    def test_first_tier_only(self):
        self.assertEqual(tiered_energy_charge(400), D("48.00"))

    def test_spans_all_tiers(self):
        self.assertEqual(tiered_energy_charge(1200), D("60.00") + D("75.00") + D("40.00"))

    def test_zero(self):
        self.assertEqual(tiered_energy_charge(0), D("0"))


class TestBilling(unittest.TestCase):
    def test_no_solar_month(self):
        bill = SolarAccount("A1").bill(reading(1, 400))
        self.assertEqual(bill.energy, D("48.00"))
        self.assertEqual(bill.fixed, D("12.00"))

    def test_surplus_is_banked(self):
        account = SolarAccount("A1")
        account.bill(reading(5, 300, 450))
        self.assertEqual(account.bank_kwh, 150)


if __name__ == "__main__":
    unittest.main()
