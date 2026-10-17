import unittest
from decimal import Decimal

from tab import GroupTab


class TestTab(unittest.TestCase):
    def test_equal_split(self):
        tab = GroupTab(["ana", "ben", "cai"])
        tab.add_expense("ana", "30.00", ["ana", "ben", "cai"])
        self.assertEqual(tab.balances(), {"ana": Decimal("20.00"), "ben": Decimal("-10.00"), "cai": Decimal("-10.00")})


if __name__ == "__main__":
    unittest.main()
