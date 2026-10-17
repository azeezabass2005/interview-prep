import unittest
from datetime import datetime
from decimal import Decimal

from margin import MarginEngine

NOW = datetime(2026, 5, 4, 15, 0)


class Clock:
    def __init__(self, now):
        self.current = now

    def now(self):
        return self.current


class TestMargin(unittest.TestCase):
    def test_cash_only_account(self):
        engine = MarginEngine(Clock(NOW))
        engine.open_account("a1", 5000)
        self.assertEqual(engine.evaluate("a1")["excess"], Decimal("5000"))


if __name__ == "__main__":
    unittest.main()
