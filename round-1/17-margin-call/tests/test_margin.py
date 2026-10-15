import unittest
from decimal import Decimal as D

from margin.calc import collateral, haircuts, margin_call, requirement
from margin.liquidation import liquidation_plan
from margin.models import Account, Position
from tests.helpers import example_account


class TestCalc(unittest.TestCase):
    def test_market_value(self):
        self.assertEqual(Position("X", "ETF", 10, D("12.5")).market_value, D("125.0"))

    def test_example_collateral_and_call(self):
        account = example_account()
        self.assertEqual(collateral(account), D("84000"))
        self.assertEqual(margin_call(account), D("16000"))

    def test_concentrated_position(self):
        self.assertEqual(haircuts(example_account())["AAPL"], D("0.50"))

    def test_loan_requirement(self):
        self.assertEqual(requirement(Account("A", D("-5000"))), D("5000"))

    def test_no_call_when_well_collateralised(self):
        self.assertEqual(margin_call(example_account(cash="-10000")), D("0"))


class TestLiquidation(unittest.TestCase):
    def test_single_position(self):
        account = Account("A", D("-9000"), [Position("TLT", "BOND", 100, D("100"))])
        self.assertEqual(liquidation_plan(account, D("1000")), [("TLT", 20)])


if __name__ == "__main__":
    unittest.main()
