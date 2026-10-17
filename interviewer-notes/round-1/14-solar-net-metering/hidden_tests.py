import unittest
from datetime import date
from decimal import Decimal

from netmeter import NetMetering

D1, D2, D3, D4 = date(2026, 3, 1), date(2026, 3, 31), date(2026, 4, 30), date(2026, 5, 30)


class HiddenNetMetering(unittest.TestCase):
    def test_B1_register_rollover(self):
        m = NetMetering()
        m.read("c", D1, 99_900, 0)
        self.assertEqual(m.read("c", D2, 100, 0)["total"], Decimal("40.00"))

    def test_B2_tier_prorated(self):
        m = NetMetering()
        m.read("c", D1, 0, 0)
        self.assertEqual(m.read("c", date(2026, 3, 16), 400, 0)["total"], Decimal("77.50"))

    def test_B3_bank_is_used_up(self):
        m = NetMetering()
        m.read("c", D1, 0, 0)
        m.read("c", D2, 0, 100)
        m.read("c", D3, 60, 100)
        self.assertEqual(m.read("c", D4, 120, 100)["total"], Decimal("13.00"))

    def test_B4_true_up_resets_bank(self):
        m = NetMetering()
        m.read("c", D1, 0, 0)
        m.read("c", D2, 0, 100)
        self.assertEqual(m.true_up("c"), Decimal("5.00"))
        self.assertEqual(m.accounts["c"].bank, 0)

    def test_B5_bank_only_the_excess(self):
        m = NetMetering()
        m.read("c", D1, 0, 0)
        self.assertEqual(m.read("c", D2, 300, 500)["bank"], 200)
