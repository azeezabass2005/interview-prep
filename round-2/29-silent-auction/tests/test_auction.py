import unittest
from datetime import datetime

from auction.app import build_app


class FakeClock:
    def __init__(self, now):
        self.current = now

    def now(self):
        return self.current


class TestAuction(unittest.TestCase):
    def test_single_bidder_pays_opening(self):
        clock = FakeClock(datetime(2026, 5, 1, 19, 0))
        api, _ = build_app(clock)
        api.add_lot({"lot_id": "L1", "opening": "50", "fmv": "40", "closes_at": "2026-05-01T21:00:00"})
        api.register(101, "Ann")
        api.bid("L1", 101, "120")
        clock.current = datetime(2026, 5, 1, 21, 0)
        self.assertEqual(api.close("L1")[1], {"winner": 101, "hammer": "50"})


if __name__ == "__main__":
    unittest.main()
