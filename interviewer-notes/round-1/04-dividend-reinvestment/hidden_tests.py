import unittest
from datetime import date
from decimal import Decimal

from drip.models import Account
from tests.helpers import Q1, Q2, by_account, setup

RES_CASH = Account("RC", resident=True, drip_enrolled=False)
RES_DRIP = Account("RD", resident=True, drip_enrolled=True)
NONRES_DRIP = Account("ND", resident=False, drip_enrolled=True)


class HiddenDrip(unittest.TestCase):
    def test_B1_entitlement_uses_record_date(self):
        ledger, proc = setup((RES_CASH, 100))
        ledger.record(date(2026, 3, 20), "RC", 50)  # after record date, before pay date
        self.assertEqual(by_account(proc.process(Q1))["RC"].gross, Decimal("82.00"))

    def test_B2_withholding_is_on_gross(self):
        _, proc = setup((NONRES_DRIP, 100))
        self.assertEqual(by_account(proc.process(Q1))["ND"].withholding, Decimal("12.30"))

    def test_B3_shares_never_round_up(self):
        _, proc = setup((RES_DRIP, 10))
        p = by_account(proc.process(Q1))["RD"]
        self.assertEqual(p.fee, Decimal("0.41"))
        self.assertEqual(p.shares_bought, Decimal("0.1947"))
        self.assertGreaterEqual(p.residual, 0)

    def test_B4_residual_rolls_into_next_reinvestment(self):
        _, proc = setup((RES_DRIP, 10))
        proc.process(Q1)
        p = by_account(proc.process(Q2))["RD"]
        self.assertEqual(p.shares_bought, Decimal("0.1983"))
        self.assertEqual(p.residual, 0)

    def test_B5_fee_cap_uses_net_cash(self):
        _, proc = setup((NONRES_DRIP, 10))
        self.assertEqual(by_account(proc.process(Q1))["ND"].fee, Decimal("0.35"))
