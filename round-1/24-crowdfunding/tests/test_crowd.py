import unittest
from datetime import datetime
from decimal import Decimal

from crowd import Platform

DEADLINE = datetime(2026, 9, 30, 23, 59)


class AlwaysOk:
    def charge(self, backer, amount):
        return True


class TestCrowd(unittest.TestCase):
    def test_pledges_add_up(self):
        p = Platform(AlwaysOk())
        p.create("c1", 1000, DEADLINE)
        p.pledge("c1", "ana", 300, datetime(2026, 9, 1))
        p.pledge("c1", "ben", 200, datetime(2026, 9, 2))
        self.assertEqual(p.total("c1"), Decimal("500"))


if __name__ == "__main__":
    unittest.main()
