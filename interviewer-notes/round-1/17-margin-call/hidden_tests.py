import unittest
from datetime import datetime, timedelta
from decimal import Decimal

from margin import MarginEngine

NOW = datetime(2026, 5, 4, 15, 0)


class Clock:
    def __init__(self, now):
        self.current = now

    def now(self):
        return self.current


def engine(cash=0, as_of=NOW):
    clock = Clock(NOW)
    e = MarginEngine(clock)
    for s in ("A", "B", "C"):
        e.list_security(s, "EQUITY")
        e.set_price(s, 100, as_of)
    e.open_account("a1", cash)
    return e, clock


class HiddenMargin(unittest.TestCase):
    def test_B1_shorts_reduce_equity(self):
        e, _ = engine(100_000)
        e.trade("a1", "A", -100, 100)
        self.assertEqual(e.evaluate("a1")["equity"], Decimal("100000"))

    def test_B2_concentration_uses_long_value_only(self):
        e, _ = engine(0)
        e.trade("a1", "A", 500, 100)
        e.trade("a1", "B", 500, 100)
        e.trade("a1", "C", -1000, 100)
        self.assertEqual(e.evaluate("a1")["requirement"], Decimal("80000"))

    def test_B3_exactly_15_minutes_is_fresh(self):
        e, _ = engine(0, as_of=NOW - timedelta(minutes=15))
        e.trade("a1", "A", 100, 100)
        self.assertEqual(e.evaluate("a1")["requirement"], Decimal("5000"))

    def test_B4_call_rounds_up(self):
        e, _ = engine(0)
        e.trade("a1", "A", 1000, 100)
        e.accounts["a1"].cash = Decimal("-51220")
        self.assertEqual(e.evaluate("a1")["call"]["amount"], Decimal("1300"))

    def test_B5_only_deposits_after_the_call_count(self):
        e, clock = engine(0)
        e.trade("a1", "A", 1000, 100)
        e.accounts["a1"].cash = Decimal("-51800")
        e.deposit("a1", 500)
        clock.current = NOW + timedelta(minutes=1)
        e.evaluate("a1")
        clock.current = NOW + timedelta(minutes=2)
        e.deposit("a1", 1000)
        self.assertEqual(e.call_remaining("a1"), Decimal("300"))
