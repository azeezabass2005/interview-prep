import unittest
from datetime import datetime

from garage.app import build_app


class FakeClock:
    def __init__(self, now):
        self.current = now

    def now(self):
        return self.current


class TestGarage(unittest.TestCase):
    def test_two_hour_stay(self):
        clock = FakeClock(datetime(2026, 3, 3, 10, 0))
        api, _ = build_app(clock)
        _, ticket = api.enter("AB12 CDE")
        clock.current = datetime(2026, 3, 3, 12, 0)
        self.assertEqual(api.exit(ticket["ticket_id"]), (200, {"charge_cents": 800}))


if __name__ == "__main__":
    unittest.main()
