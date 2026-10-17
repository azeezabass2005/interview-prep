import unittest
from datetime import date
from decimal import Decimal

from drip import DripProcessor

REC, PAY = date(2026, 3, 10), date(2026, 3, 15)


def holder(country="US", shares=100, enrol=None):
    d = DripProcessor()
    d.open_account("a1", country)
    d.trade("a1", "XYZ", date(2026, 3, 1), shares)
    if enrol:
        d.enrol("a1", "XYZ", enrol)
    return d


class HiddenDrip(unittest.TestCase):
    def test_B1_record_date_holdings(self):
        d = holder()
        d.trade("a1", "XYZ", date(2026, 3, 12), 50)
        [p] = d.pay_dividend("XYZ", "0.50", REC, PAY, "25")
        self.assertEqual(p["gross"], Decimal("50.00"))

    def test_B2_other_countries_withhold_30_percent(self):
        [p] = holder("BR").pay_dividend("XYZ", "0.50", REC, PAY, "25")
        self.assertEqual(p["tax"], Decimal("15.00"))

    def test_B3_shares_round_down(self):
        [p] = holder(shares=40, enrol=date(2026, 1, 1)).pay_dividend("XYZ", "0.50", REC, PAY, "3")
        self.assertEqual(p["shares_bought"], Decimal("6.6666"))

    def test_B4_leftover_cash_paid(self):
        [p] = holder(enrol=date(2026, 1, 1)).pay_dividend("XYZ", "0.50", REC, PAY, "700")
        self.assertEqual((p["shares_bought"], p["cash"]), (Decimal("0.0714"), Decimal("0.02")))

    def test_B5_enrolment_after_record_date_not_applied(self):
        [p] = holder(enrol=date(2026, 3, 12)).pay_dividend("XYZ", "0.50", REC, PAY, "25")
        self.assertEqual((p["shares_bought"], p["cash"]), (Decimal("0"), Decimal("50.00")))
