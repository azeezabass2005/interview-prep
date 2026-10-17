import unittest
from datetime import date
from decimal import Decimal

from tips import TipPool

DAY = date(2026, 3, 4)


class TestTips(unittest.TestCase):
    def test_single_server_gets_card_pool(self):
        pool = TipPool()
        pool.add_work("ana", "SERVER", DAY, "DINNER", 6)
        pool.add_tips(DAY, "DINNER", card=200)
        self.assertEqual(pool.distribute(DAY, "DINNER"), {"ana": Decimal("195.00")})


if __name__ == "__main__":
    unittest.main()
