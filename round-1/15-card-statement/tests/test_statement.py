import unittest
from datetime import date
from decimal import Decimal

from statement import Card


class TestStatement(unittest.TestCase):
    def test_first_cycle_has_grace(self):
        card = Card()
        card.purchase(date(2026, 3, 5), "400.00")
        s = card.close(date(2026, 3, 1), date(2026, 3, 30))
        self.assertEqual((s["purchase_interest"], s["balance"]), (Decimal("0.00"), Decimal("400.00")))

    def test_purchase_adds_amount_to_purchase_balance(self):
        card = Card()
        card.purchase(date(2026, 3, 1), "250.00")
        card.close(date(2026, 3, 1), date(2026, 3, 30))
        self.assertEqual(card.balances["purchase"], Decimal("250.00"))

    def test_cash_advance_adds_amount_plus_fee_to_cash_balance(self):
        card = Card()
        amount = Decimal("100.00")
        fee = max(Decimal("10.00"), amount * Decimal("0.05"))
        card.cash_advance(date(2026, 3, 1), amount)
        s = card.close(date(2026, 3, 1), date(2026, 3, 30))
        self.assertEqual(card.balances["cash"] - s["cash_interest"], amount + fee)

    def test_cash_interest_added_to_cash_balance_at_close(self):
        card = Card()
        card.cash_advance(date(2026, 3, 1), "200.00")
        s = card.close(date(2026, 3, 1), date(2026, 3, 30))
        self.assertGreater(s["cash_interest"], Decimal("0.00"))
        self.assertEqual(card.balances["cash"], Decimal("210.00") + s["cash_interest"])

    def test_purchase_interest_added_to_purchase_balance_at_close(self):
        card = Card()
        card.purchase(date(2026, 3, 1), "1000.00")
        card.close(date(2026, 3, 1), date(2026, 3, 30))
        card.pay(date(2026, 4, 10), "25.00")
        s = card.close(date(2026, 3, 31), date(2026, 4, 29))
        self.assertGreater(s["purchase_interest"], Decimal("0.00"))
        self.assertEqual(card.balances["purchase"], Decimal("975.00") + s["purchase_interest"])

    def test_payment_goes_to_cash_balance_before_purchase_balance(self):
        card = Card()
        card.purchase(date(2026, 3, 1), "100.00")
        card.cash_advance(date(2026, 3, 1), "100.00")
        card.pay(date(2026, 3, 1), "110.00")
        card.close(date(2026, 3, 1), date(2026, 3, 30))
        self.assertEqual(card.balances["cash"], Decimal("0.00"))
        self.assertEqual(card.balances["purchase"], Decimal("100.00"))

    def test_no_purchase_interest_when_previous_statement_paid_in_full(self):
        card = Card()
        card.purchase(date(2026, 3, 1), "1000.00")
        first = card.close(date(2026, 3, 1), date(2026, 3, 30))
        card.pay(date(2026, 4, 10), first["balance"])
        card.purchase(date(2026, 4, 15), "200.00")
        card.cash_advance(date(2026, 4, 15), "200.00")
        s = card.close(date(2026, 3, 31), date(2026, 4, 29))
        self.assertEqual(s["purchase_interest"], Decimal("0.00"))
        self.assertGreater(s["cash_interest"], Decimal("0.00"))

    def test_late_fee_added_to_purchase_balance_when_minimum_not_paid(self):
        card = Card()
        card.purchase(date(2026, 3, 1), "1000.00")
        first = card.close(date(2026, 3, 1), date(2026, 3, 30))
        card.pay(date(2026, 4, 10), first["minimum"] - Decimal("5.00"))
        s = card.close(date(2026, 3, 31), date(2026, 4, 29))
        self.assertEqual(s["late_fee"], Decimal("30.00"))
        self.assertEqual(card.balances["purchase"], Decimal("980.00") + s["purchase_interest"] + Decimal("30.00"))


if __name__ == "__main__":
    unittest.main()
