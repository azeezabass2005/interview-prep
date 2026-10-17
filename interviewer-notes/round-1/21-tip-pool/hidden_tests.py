import unittest
from datetime import date
from decimal import Decimal

from tips import TipPool

DAY = date(2026, 3, 4)


class HiddenTips(unittest.TestCase):
    def test_B1_managers_excluded(self):
        p = TipPool()
        p.add_work("ana", "SERVER", DAY, "DINNER", 5)
        p.add_work("mo", "MANAGER", DAY, "DINNER", 5)
        p.add_tips(DAY, "DINNER", card=100)
        self.assertEqual(p.distribute(DAY, "DINNER"), {"ana": Decimal("97.50")})

    def test_B2_no_fee_on_cash(self):
        p = TipPool()
        self.assertEqual((p.add_tips(DAY, "DINNER", cash=100, card=100), p.pool(DAY, "DINNER"))[1], Decimal("197.50"))

    def test_B3_exactly_one_hour_is_eligible(self):
        p = TipPool()
        p.add_work("ana", "SERVER", DAY, "DINNER", 5)
        p.add_work("ben", "SERVER", DAY, "DINNER", 1)
        p.add_tips(DAY, "DINNER", card=Decimal("61.54"))
        self.assertEqual(p.distribute(DAY, "DINNER"), {"ana": Decimal("50.00"), "ben": Decimal("10.00")})

    def test_B4_leftover_cents_to_most_points(self):
        p = TipPool()
        p.add_work("zoe", "SERVER", DAY, "DINNER", 2)
        p.add_work("ben", "SERVER", DAY, "DINNER", 1)
        p.add_tips(DAY, "DINNER", cash=10)
        self.assertEqual(p.distribute(DAY, "DINNER"), {"zoe": Decimal("6.67"), "ben": Decimal("3.33")})

    def test_B5_lunch_and_dinner_are_separate_pools(self):
        p = TipPool()
        p.add_work("ana", "SERVER", DAY, "LUNCH", 4)
        p.add_work("ben", "SERVER", DAY, "DINNER", 4)
        p.add_tips(DAY, "LUNCH", card=100)
        self.assertEqual(p.distribute(DAY, "LUNCH"), {"ana": Decimal("97.50")})
