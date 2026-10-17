import unittest
from datetime import datetime

from auction.app import build_app


class FakeClock:
    def __init__(self, now):
        self.current = now

    def now(self):
        return self.current


def setup(opening="50", fmv="40", closes="2026-05-01T20:00:00"):
    clock = FakeClock(datetime(2026, 5, 1, 19, 0))
    api, _ = build_app(clock)
    api.add_lot({"lot_id": "L1", "opening": opening, "fmv": fmv, "closes_at": closes})
    for paddle in (101, 102, 103):
        api.register(paddle, f"b{paddle}")
    return api, clock


def close(api, clock):
    clock.current = datetime(2026, 5, 2)
    return api.close("L1")[1]


class HiddenAuction(unittest.TestCase):
    def test_B1_tie_goes_to_first_bid(self):
        api, clock = setup()
        api.bid("L1", 101, "150")
        self.assertEqual(api.bid("L1", 102, "150")[1]["leader"], 101)

    def test_B2_increment_from_runner_up(self):
        api, clock = setup()
        api.bid("L1", 101, "600")
        self.assertEqual(api.bid("L1", 102, "450")[1]["price"], "460")

    def test_B3_soft_close_extends_from_bid_time(self):
        api, clock = setup()
        clock.current = datetime(2026, 5, 1, 19, 59, 30)
        self.assertEqual(api.bid("L1", 101, "100")[1]["closes_at"], "2026-05-01T20:01:30")
        clock.current = datetime(2026, 5, 1, 20, 1, 45)
        self.assertEqual(api.bid("L1", 102, "200")[0], 409)

    def test_B4_premium_on_hammer(self):
        api, clock = setup()
        api.bid("L1", 101, "200")
        api.bid("L1", 102, "120")
        close(api, clock)
        invoice = api.invoices()[1]["101"]
        self.assertEqual((invoice["lines"][0]["premium"], invoice["total"]), ("13.00", "143.00"))

    def test_B5_deductible_never_negative(self):
        api, clock = setup(fmv="100")
        api.bid("L1", 101, "80")
        close(api, clock)
        self.assertEqual(api.invoices()[1]["101"]["lines"][0]["deductible"], "0")
