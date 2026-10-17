import unittest
from datetime import datetime

from hotel.app import build_app


class FakeClock:
    def __init__(self, now):
        self.current = now

    def now(self):
        return self.current


class TestHotel(unittest.TestCase):
    def test_weekday_quote(self):
        api, _ = build_app(FakeClock(datetime(2026, 5, 1, 9, 0)))
        status, quote = api.quote({"room_type": "STANDARD", "check_in": "2026-06-01", "check_out": "2026-06-03"})
        self.assertEqual(status, 200)
        self.assertEqual(quote["room_total"], "300.00")


if __name__ == "__main__":
    unittest.main()
