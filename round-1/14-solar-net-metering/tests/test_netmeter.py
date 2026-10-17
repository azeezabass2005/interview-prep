import unittest
from datetime import date
from decimal import Decimal

from netmeter import NetMetering


class TestNetMetering(unittest.TestCase):
    def test_small_month(self):
        m = NetMetering()
        m.read("c1", date(2026, 3, 1), 1000, 0)
        bill = m.read("c1", date(2026, 3, 31), 1200, 0)
        self.assertEqual(bill["total"], Decimal("40.00"))


if __name__ == "__main__":
    unittest.main()
