import unittest
from datetime import datetime, timedelta
from decimal import Decimal

from boxoffice import BoxOffice

SHOW = datetime(2026, 10, 30, 19, 30)
NOW = datetime(2026, 10, 1, 19, 0)


class TestBoxOffice(unittest.TestCase):
    def test_buy_back_row_seat(self):
        office = BoxOffice(SHOW)
        hold = office.hold("ana", ["M1"], NOW)
        self.assertEqual(office.buy(hold.hold_id, "ana", NOW + timedelta(minutes=2)).total, Decimal("54.50"))


if __name__ == "__main__":
    unittest.main()
