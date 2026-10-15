import unittest
from decimal import Decimal as D

from classes.models import BOOKED, WAITLISTED, BookingError
from tests.helpers import ANA, BEA, SAM, setup


class TestBooking(unittest.TestCase):
    def test_books_until_full_then_waitlists(self):
        _, svc, cls = setup(capacity=2)
        self.assertEqual(svc.book(cls, ANA), BOOKED)
        self.assertEqual(svc.book(cls, SAM), BOOKED)
        self.assertEqual(svc.book(cls, BEA), WAITLISTED)
        self.assertEqual(svc.roster(cls), ["ana", "sam"])

    def test_cannot_book_twice(self):
        _, svc, cls = setup()
        svc.book(cls, ANA)
        with self.assertRaises(BookingError):
            svc.book(cls, ANA)

    def test_early_cancel_free(self):
        clock, svc, cls = setup()
        svc.book(cls, ANA)
        clock.hours_before_start(20)
        self.assertEqual(svc.cancel(cls, ANA), D("0.00"))

    def test_late_cancel_fee(self):
        clock, svc, cls = setup()
        svc.book(cls, ANA)
        clock.hours_before_start(2)
        self.assertEqual(svc.cancel(cls, ANA), D("10.00"))

    def test_cancel_without_place(self):
        _, svc, cls = setup()
        with self.assertRaises(BookingError):
            svc.cancel(cls, ANA)


if __name__ == "__main__":
    unittest.main()
