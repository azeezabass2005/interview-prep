import unittest
from decimal import Decimal as D

from margin.calc import collateral, haircuts, margin_call, requirement
from margin.liquidation import liquidation_plan
from margin.models import Account, Position
from tests.helpers import example_account


class HiddenMargin(unittest.TestCase):
    def test_B1_concentration_uses_gross_long_value(self):
        account = Account("A", D("0"), [
            Position("A", "EQUITY", 300, D("100")),
            Position("B", "EQUITY", 380, D("100")),
            Position("C", "EQUITY", 320, D("100")),
            Position("S", "EQUITY", -200, D("100")),
        ])
        self.assertEqual(haircuts(account)["B"], D("0.25"))

    def test_B2_exactly_forty_percent_not_concentrated(self):
        account = Account("A", D("0"), [
            Position("A", "EQUITY", 40, D("100")),
            Position("B", "BOND", 60, D("100")),
        ])
        self.assertEqual(haircuts(account)["A"], D("0.25"))

    def test_B3_call_rounds_up(self):
        self.assertEqual(margin_call(example_account(cash="-100040")), D("16100"))

    def test_B4_short_requirement_includes_principal(self):
        account = Account("A", D("0"), [Position("S", "EQUITY", -100, D("100"))])
        self.assertEqual(requirement(account), D("13000"))

    def test_B5_liquidate_highest_haircut_first(self):
        self.assertEqual(liquidation_plan(example_account(), D("16000")), [("AAPL", 160)])

    def test_G1_positive_cash_is_collateral(self):
        self.assertEqual(collateral(Account("A", D("5000"))), D("5000"))
