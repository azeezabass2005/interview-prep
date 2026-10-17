import unittest
from datetime import datetime, timedelta

from fx.app import build_app


class FakeClock:
    def __init__(self):
        self.current = datetime(2026, 4, 1, 12, 0, 0)

    def now(self):
        return self.current


def world():
    clock = FakeClock()
    api = build_app(clock)
    for pair, rate in (("EURUSD", "1.0850"), ("GBPUSD", "1.2700"), ("USDJPY", "151.20")):
        api.publish(pair, rate)
    return api, clock


def quote(api, source, amount, target, customer="c1"):
    return api.quote({"customer": customer, "source": source, "amount": amount, "target": target})[1]


class HiddenFx(unittest.TestCase):
    def test_B1_usd_base_pairs_inverted(self):
        api, _ = world()
        self.assertEqual(quote(api, "JPY", "1512", "USD")["target_amount"], "9.90")

    def test_B2_tier_on_usd_equivalent(self):
        api, _ = world()
        self.assertEqual(quote(api, "GBP", "9000", "USD")["target_amount"], "11372.85")

    def test_B3_round_down(self):
        api, _ = world()
        self.assertEqual(quote(api, "EUR", "100", "USD")["target_amount"], "107.41")

    def test_B4_expired_quote_rejected(self):
        api, clock = world()
        q = quote(api, "EUR", "100", "USD")
        clock.current += timedelta(seconds=31)
        self.assertEqual(api.book(q["quote_id"])[0], 409)

    def test_B5_cancelled_payments_free_the_limit(self):
        api, _ = world()
        first = api.book(quote(api, "EUR", "36866.36", "USD")["quote_id"])[1]
        api.cancel(first["payment_id"])
        self.assertEqual(api.book(quote(api, "EUR", "36866.36", "USD")["quote_id"])[0], 201)
