import unittest

from bonds.app import build_app


def book(maturity="2030-05-15", day_count="30/360", trade_date="2026-03-12", frequency=2, holidays=()):
    api, _ = build_app()
    for h in holidays:
        api.add_holiday(h)
    api.load_bond({"bond_id": "B", "coupon": "0.05", "frequency": frequency, "maturity": maturity, "day_count": day_count})
    return api.book({"trade_id": "T", "bond_id": "B", "face": "1000000", "price": "99.5", "trade_date": trade_date})[1]


class HiddenBonds(unittest.TestCase):
    def test_B1_d2_rule_needs_d1_30(self):
        self.assertEqual(book(maturity="2030-07-15", trade_date="2026-03-30")["accrued"], "10555.56")

    def test_B2_end_of_month_rule(self):
        self.assertEqual(book(maturity="2030-06-30", day_count="ACT/360", trade_date="2026-01-14")["accrued"], "2083.33")

    def test_B3_holidays_are_not_business_days(self):
        self.assertEqual(book(trade_date="2026-04-02", holidays=["2026-04-03"])["settle_date"], "2026-04-06")

    def test_B4_settle_on_coupon_date(self):
        self.assertEqual(book(trade_date="2026-05-14")["accrued"], "0.00")

    def test_B5_act_360(self):
        self.assertEqual(book(day_count="ACT/360", trade_date="2026-01-14")["accrued"], "8472.22")
