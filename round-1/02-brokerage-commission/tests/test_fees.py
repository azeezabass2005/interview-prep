import unittest
from decimal import Decimal

from fees.commission import commission_for, regulatory_fee
from fees.statement import build_statement
from tests.helpers import trade


class TestCommission(unittest.TestCase):
    def test_first_tier_rate(self):
        self.assertEqual(commission_for(Decimal("5000")), Decimal("5.00"))

    def test_minimum_commission(self):
        self.assertEqual(commission_for(Decimal("200")), Decimal("1.00"))

    def test_rejects_non_positive_notional(self):
        with self.assertRaises(ValueError):
            commission_for(Decimal("0"))


class TestRegulatoryFee(unittest.TestCase):
    def test_buys_have_no_reg_fee(self):
        self.assertEqual(regulatory_fee("BUY", Decimal("5000")), Decimal("0.00"))

    def test_sell_reg_fee_from_spec_example(self):
        self.assertEqual(regulatory_fee("SELL", Decimal("5000")), Decimal("0.14"))


class TestStatement(unittest.TestCase):
    def test_statement_only_includes_account(self):
        trades = [trade(1), trade(2, account="OTHER"), trade(3)]
        statement = build_statement("ACC1", trades)
        self.assertEqual([l.trade_id for l in statement.lines], ["T1", "T3"])

    def test_statement_total(self):
        trades = [trade(1, "5000", "SELL"), trade(2, "2000")]
        statement = build_statement("ACC1", trades)
        self.assertEqual(statement.total, Decimal("5.00") + Decimal("0.14") + Decimal("2.00"))

    def test_no_discount_for_small_months(self):
        trades = [trade(n) for n in range(1, 11)]
        statement = build_statement("ACC1", trades)
        self.assertTrue(all(l.discount == 0 for l in statement.lines))


if __name__ == "__main__":
    unittest.main()
