import unittest
from datetime import date, datetime
from decimal import Decimal

from payroll import Payroll


class TestPayroll(unittest.TestCase):
    def test_short_shift(self):
        p = Payroll()
        p.set_rate("ana", date(2026, 1, 1), 20)
        p.add_shift("ana", datetime(2026, 3, 2, 9), datetime(2026, 3, 2, 13))
        self.assertEqual(p.week("ana", date(2026, 3, 2))["gross"], Decimal("80.00"))


if __name__ == "__main__":
    unittest.main()
