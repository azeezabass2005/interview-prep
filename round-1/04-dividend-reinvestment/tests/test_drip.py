import unittest
from datetime import date
from decimal import Decimal

from drip.models import Account
from tests.helpers import Q1, by_account, setup

RES_CASH = Account("RC", resident=True, drip_enrolled=False)
NONRES_CASH = Account("NC", resident=False, drip_enrolled=False)
RES_DRIP = Account("RD", resident=True, drip_enrolled=True)


class TestCashHolders(unittest.TestCase):
    def test_resident_cash_payment(self):
        _, proc = setup((RES_CASH, 100))
        p = by_account(proc.process(Q1))["RC"]
        self.assertEqual(p.gross, Decimal("82.00"))
        self.assertEqual(p.cash_paid, Decimal("82.00"))

    def test_non_resident_withholding(self):
        _, proc = setup((NONRES_CASH, 100))
        p = by_account(proc.process(Q1))["NC"]
        self.assertEqual(p.withholding, Decimal("12.30"))
        self.assertEqual(p.cash_paid, Decimal("69.70"))

    def test_gross_rounds_down(self):
        _, proc = setup((RES_CASH, "33.3333"))
        p = by_account(proc.process(Q1))["RC"]
        self.assertEqual(p.gross, Decimal("27.33"))  # 27.333306


class TestReinvestment(unittest.TestCase):
    def test_spec_example_hundred_shares(self):
        ledger, proc = setup((RES_DRIP, 100))
        p = by_account(proc.process(Q1))["RD"]
        self.assertEqual(p.fee, Decimal("0.50"))
        self.assertEqual(p.shares_bought, Decimal("2.0375"))
        self.assertEqual(p.cash_paid, 0)
        self.assertEqual(ledger.positions_as_of(Q1.pay_date)["RD"], Decimal("102.0375"))

    def test_reinvested_shares_credited_on_pay_date(self):
        ledger, proc = setup((RES_DRIP, 100))
        proc.process(Q1)
        self.assertEqual(ledger.positions_as_of(Q1.record_date)["RD"], Decimal("100"))

    def test_accounts_with_no_shares_are_skipped(self):
        ledger, proc = setup((RES_CASH, 100), (RES_DRIP, 10))
        ledger.record(date(2026, 2, 1), "RD", -10)
        self.assertEqual(list(by_account(proc.process(Q1))), ["RC"])


if __name__ == "__main__":
    unittest.main()
