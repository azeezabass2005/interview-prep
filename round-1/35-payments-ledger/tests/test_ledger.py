import unittest
from decimal import Decimal

from ledger import Ledger


class TestLedger(unittest.TestCase):
    def test_small_transfer(self):
        ledger = Ledger()
        ledger.open("ana", "USD")
        ledger.open("ben", "USD")
        ledger.deposit("ana", 100)
        ledger.transfer("k1", "ana", "ben", 40)
        self.assertEqual((ledger.balance("ana"), ledger.balance("ben")), (Decimal("60"), Decimal("40")))


if __name__ == "__main__":
    unittest.main()
