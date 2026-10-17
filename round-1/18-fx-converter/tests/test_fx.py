import unittest
from datetime import datetime, timedelta

from fx import FxDesk

T0 = datetime(2026, 7, 1, 12, 0, 0)


class Clock:
    def __init__(self, now):
        self.current = now

    def now(self):
        return self.current


class TestFx(unittest.TestCase):
    def test_book_fresh_quote(self):
        clock = Clock(T0)
        desk = FxDesk(clock)
        desk.set_rate("EUR", "0.92")
        q = desk.quote("acme", "USD", "EUR", 1000)
        clock.current = T0 + timedelta(seconds=5)
        self.assertEqual(desk.book(q["quote_id"])["status"], "BOOKED")


if __name__ == "__main__":
    unittest.main()
