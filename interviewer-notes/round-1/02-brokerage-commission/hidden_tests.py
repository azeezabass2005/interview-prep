import unittest
from decimal import Decimal

from fees.commission import commission_for, regulatory_fee
from fees.statement import build_statement
from tests.helpers import trade


class HiddenCommission(unittest.TestCase):
    def test_B1_tiers_are_marginal(self):
        self.assertEqual(commission_for(Decimal("60000")), Decimal("32.00"))

    def test_G1_commission_capped_at_fifty(self):
        self.assertEqual(commission_for(Decimal("1000000")), Decimal("50.00"))

    def test_B2_reg_fee_always_rounds_up(self):
        self.assertEqual(regulatory_fee("SELL", Decimal("12000")), Decimal("0.34"))

    def test_B3_discount_starts_at_51st_trade(self):
        trades = [trade(n) for n in range(1, 52)]
        statement = build_statement("ACC1", trades)
        self.assertEqual(statement.line_for("T50").discount, Decimal("0.00"))
        self.assertEqual(statement.line_for("T51").discount, Decimal("0.20"))

    def test_B4_discount_follows_execution_order(self):
        trades = [trade(n) for n in range(1, 53)]
        trades.reverse()  # newest first, as the upstream feed delivers them
        statement = build_statement("ACC1", trades)
        self.assertEqual(statement.line_for("T1").discount, Decimal("0.00"))
        self.assertEqual(statement.line_for("T52").discount, Decimal("0.20"))
