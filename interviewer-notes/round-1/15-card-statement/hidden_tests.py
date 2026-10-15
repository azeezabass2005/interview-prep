import unittest
from decimal import Decimal as D

from card.models import CASH, PAYMENT, Cycle, Txn
from card.statement import build_statement


class HiddenCard(unittest.TestCase):
    def test_B1_payment_to_highest_apr_first(self):
        s = build_statement(Cycle(30, True, start_purchase=D("500"), start_cash=D("500"),
                                  txns=[Txn(0, PAYMENT, D("500"))]))
        self.assertEqual(s.cash_balance, D("0"))
        self.assertEqual(s.purchase_balance, D("500"))

    def test_B2_cash_fee_is_greater_of(self):
        s = build_statement(Cycle(30, True, txns=[Txn(0, CASH, D("100"))]))
        self.assertEqual(s.cash_balance, D("110.00"))

    def test_B3_cash_always_accrues(self):
        s = build_statement(Cycle(30, True, start_cash=D("1000")))
        self.assertEqual(s.cash_interest, D("23.84"))

    def test_B4_uses_actual_cycle_length(self):
        s = build_statement(Cycle(31, False, start_purchase=D("1000")))
        self.assertEqual(s.purchase_interest, D("20.38"))

    def test_B5_small_balance_minimum_is_balance(self):
        s = build_statement(Cycle(30, True, start_purchase=D("20")))
        self.assertEqual(s.minimum_due, D("20.00"))
