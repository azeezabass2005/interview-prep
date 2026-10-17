import unittest
from datetime import date
from decimal import Decimal

from statement import Card

START, END = date(2026, 3, 1), date(2026, 3, 30)


class HiddenStatement(unittest.TestCase):
    def test_B1_cash_fee_minimum(self):
        self.assertEqual(Card().cash_advance(START, "100.00"), Decimal("10.00"))

    def test_B2_payments_go_to_cash_first(self):
        card = Card()
        card.cash_advance(START, "200.00")
        card.purchase(START, "300.00")
        card.pay(START, "210.00")
        self.assertEqual(card.close(START, END)["cash_interest"], Decimal("0.00"))

    def test_B3_paying_exactly_the_balance_keeps_grace(self):
        card = Card()
        card.purchase(date(2026, 3, 2), "500.00")
        card.close(START, END)
        card.pay(date(2026, 4, 10), "500.00")
        card.purchase(date(2026, 4, 15), "100.00")
        self.assertEqual(card.close(date(2026, 3, 31), date(2026, 4, 29))["purchase_interest"], Decimal("0.00"))

    def test_B4_cycle_includes_end_date(self):
        card = Card()
        card.cash_advance(START, "1000.00")
        self.assertEqual(card.close(START, END)["cash_interest"], Decimal("25.89"))

    def test_B5_small_balance_minimum_is_balance(self):
        card = Card()
        card.purchase(date(2026, 3, 2), "20.00")
        self.assertEqual(card.close(START, END)["minimum"], Decimal("20.00"))
