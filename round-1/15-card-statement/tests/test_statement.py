import unittest
from decimal import Decimal as D

from card.models import PAYMENT, PURCHASE, Cycle, Txn
from card.statement import build_statement


class TestStatement(unittest.TestCase):
    def test_spec_example(self):
        s = build_statement(Cycle(30, False, start_purchase=D("1000")))
        self.assertEqual(s.purchase_interest, D("19.73"))
        self.assertEqual(s.new_balance, D("1019.73"))
        self.assertEqual(s.minimum_due, D("29.93"))

    def test_grace_period_on_purchases(self):
        s = build_statement(Cycle(30, True, start_purchase=D("1000")))
        self.assertEqual(s.purchase_interest, D("0.00"))

    def test_mid_cycle_purchase_average_balance(self):
        s = build_statement(Cycle(30, False, txns=[Txn(15, PURCHASE, D("300"))]))
        self.assertEqual(s.purchase_interest, D("2.96"))  # ADB 150

    def test_payment_reduces_purchases(self):
        s = build_statement(Cycle(30, True, start_purchase=D("800"), txns=[Txn(0, PAYMENT, D("300"))]))
        self.assertEqual(s.purchase_balance, D("500"))

    def test_unknown_transaction(self):
        with self.assertRaises(ValueError):
            build_statement(Cycle(30, True, txns=[Txn(0, "REFUND", D("5"))]))


if __name__ == "__main__":
    unittest.main()
