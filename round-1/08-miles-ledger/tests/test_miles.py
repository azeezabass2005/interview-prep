import unittest
from datetime import date

from miles import MilesLedger


class TestMiles(unittest.TestCase):
    def test_basic_member_earns_base_miles(self):
        ledger = MilesLedger()
        ledger.join("ana")
        self.assertEqual(ledger.fly("ana", date(2026, 3, 1), 1200, "Y"), 1200)
        self.assertEqual(ledger.balance("ana", date(2026, 3, 2)), 1200)


if __name__ == "__main__":
    unittest.main()
