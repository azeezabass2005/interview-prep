import unittest
from decimal import Decimal

from card.app import build_app


def card():
    api = build_app()
    api.open("C", "5000", "2026-03-01")
    return api


def post(api, day, kind, amount):
    assert api.post("C", {"date": day, "kind": kind, "amount": amount})[0] == 201


class HiddenCard(unittest.TestCase):
    def test_B1_payment_to_highest_apr_first(self):
        api = card()
        post(api, "2026-03-01", "PURCHASE", "500")
        post(api, "2026-03-01", "CASH", "200")
        post(api, "2026-03-02", "PAYMENT", "210")
        balances = api.close("C", "2026-03-30")[1]["balances"]
        self.assertLess(Decimal(balances["cash"]), Decimal("1"))
        self.assertGreaterEqual(Decimal(balances["purchase"]), Decimal("500"))

    def test_B2_cash_fee_greater_of(self):
        api = card()
        post(api, "2026-03-01", "CASH", "100")
        self.assertEqual(int(Decimal(api.close("C", "2026-03-01")[1]["balances"]["cash"])), 110)

    def test_B3_adb_uses_cycle_length(self):
        api = card()
        post(api, "2026-03-01", "PURCHASE", "1000")
        self.assertEqual(api.close("C", "2026-03-31")[1]["interest"]["purchase"], "20.38")

    def test_B4_cash_accrues_despite_grace(self):
        api = card()
        post(api, "2026-03-01", "PURCHASE", "1000")
        first = api.close("C", "2026-03-30")[1]
        post(api, "2026-04-10", "PAYMENT", first["new_balance"])
        post(api, "2026-04-15", "CASH", "300")
        second = api.close("C", "2026-04-30")[1]
        self.assertEqual(second["interest"]["purchase"], "0.00")
        self.assertGreater(Decimal(second["interest"]["cash"]), 0)

    def test_B5_payment_on_due_date_is_on_time(self):
        api = card()
        post(api, "2026-03-01", "PURCHASE", "1000")
        first = api.close("C", "2026-03-30")[1]
        post(api, first["due_date"], "PAYMENT", first["minimum_due"])
        self.assertEqual(api.close("C", "2026-04-30")[1]["fees"], "0.00")
