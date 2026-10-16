import unittest

from drip.app import build_app

Q1 = {"event_id": "Q1", "security": "BBG", "record_date": "2026-03-10", "pay_date": "2026-03-31",
      "per_share": "0.82", "reinvest_price": "40.00"}
Q2 = {"event_id": "Q2", "security": "BBG", "record_date": "2026-06-10", "pay_date": "2026-06-30",
      "per_share": "0.82", "reinvest_price": "40.00"}


def world(country="US", shares="100", enrol_from=None):
    api, store = build_app()
    api.open_account({"account_id": "A", "name": "Ann", "country": country})
    api.record_movement({"account_id": "A", "security": "BBG", "on": "2026-01-05", "shares": shares})
    if enrol_from:
        api.set_enrolment({"account_id": "A", "security": "BBG", "enrolled": True, "effective_from": enrol_from})
    api.declare(Q1)
    return api


def pay(api, event="Q1"):
    return api.process(event)[1]["payments"][0]


class HiddenDrip(unittest.TestCase):
    def test_B1_entitlement_on_record_date(self):
        api = world()
        api.record_movement({"account_id": "A", "security": "BBG", "on": "2026-03-20", "shares": "50"})
        self.assertEqual(pay(api)["gross"], "82.00")

    def test_B2_unknown_country_default_rate(self):
        self.assertEqual(pay(world(country="BR"))["withholding"], "24.60")

    def test_B3_enrolment_as_of_record_date(self):
        api = world(enrol_from="2026-03-15")
        p = pay(api)
        self.assertEqual((p["cash_paid"], p["shares_bought"]), ("82.00", "0"))

    def test_B4_leftover_feeds_next_reinvestment(self):
        api = world(shares="10", enrol_from="2026-01-01")
        pay(api)
        api.declare(Q2)
        p = pay(api, "Q2")
        self.assertEqual(p["shares_bought"], "0.1983")
        self.assertEqual(float(p["leftover"]), 0.0)

    def test_B5_fee_cap_on_net(self):
        self.assertEqual(pay(world(country="GB", shares="10", enrol_from="2026-01-01"))["fee"], "0.35")
