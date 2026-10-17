import unittest
from datetime import datetime, timedelta
from decimal import Decimal

from boxoffice import BoxOffice, price

SHOW = datetime(2026, 10, 30, 19, 30)
NOW = datetime(2026, 10, 1, 19, 0)


class HiddenBoxOffice(unittest.TestCase):
    def test_B1_expired_holds_free_the_seat(self):
        office = BoxOffice(SHOW)
        office.hold("ana", ["A1"], NOW)
        self.assertEqual(office.hold("ben", ["A1"], NOW + timedelta(minutes=11)).customer, "ben")

    def test_B2_limit_counts_bought_tickets(self):
        office = BoxOffice(SHOW)
        hold = office.hold("ana", ["M1", "M2", "M3", "M4", "M5"], NOW)
        office.buy(hold.hold_id, "ana", NOW)
        with self.assertRaises(Exception):
            office.hold("ana", ["N1", "N2", "N3", "N4"], NOW)

    def test_B3_gap_on_the_right(self):
        office = BoxOffice(SHOW)
        hold = office.hold("ana", ["E5"], NOW)
        office.buy(hold.hold_id, "ana", NOW)
        with self.assertRaises(Exception):
            office.hold("ben", ["E3"], NOW)

    def test_B4_row_c_is_premium(self):
        self.assertEqual(price("C1"), Decimal("120.00"))

    def test_B5_fees_not_refunded(self):
        office = BoxOffice(SHOW)
        hold = office.hold("ana", ["D4", "D5"], NOW)
        order = office.buy(hold.hold_id, "ana", NOW)
        self.assertEqual(office.refund(order.order_id, SHOW - timedelta(days=3)), Decimal("160.00"))
