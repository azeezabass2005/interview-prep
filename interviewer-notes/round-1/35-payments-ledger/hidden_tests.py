import unittest
from decimal import Decimal

from ledger import Ledger


def ledger(deposit=2000):
    l = Ledger()
    l.open("ana", "USD")
    l.open("ben", "USD")
    l.deposit("ana", deposit)
    return l


class HiddenLedger(unittest.TestCase):
    def test_B1_holds_reduce_spendable_funds(self):
        l = ledger(100)
        l.hold("h1", "ana", 80)
        with self.assertRaises(Exception):
            l.transfer("k1", "ana", "ben", 50)

    def test_B2_idempotency_key_reused(self):
        l = ledger()
        l.transfer("k1", "ana", "ben", 100)
        l.transfer("k1", "ana", "ben", 100)
        self.assertEqual(l.balance("ana"), Decimal("1900"))

    def test_B3_exactly_1000_has_no_fee(self):
        self.assertEqual(Ledger.fee_for(Decimal("1000")), Decimal("0.00"))

    def test_B4_minimum_fee(self):
        self.assertEqual(Ledger.fee_for(Decimal("1200")), Decimal("1.00"))

    def test_B5_reversal_refunds_fee(self):
        l = ledger()
        t = l.transfer("k1", "ana", "ben", 1500)
        l.reverse(t.transfer_id)
        self.assertEqual((l.balance("ana"), l.balance("FEES")), (Decimal("2000"), Decimal("0")))
