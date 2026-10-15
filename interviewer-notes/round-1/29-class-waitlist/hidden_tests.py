import unittest
from decimal import Decimal as D

from classes.models import Member
from tests.helpers import ANA, BEA, PIA, SAM, setup


class HiddenBooking(unittest.TestCase):
    def test_B1_premium_ahead_on_waitlist(self):
        clock, svc, cls = setup()
        svc.book(cls, ANA)
        svc.book(cls, SAM)
        svc.book(cls, PIA)
        clock.hours_before_start(20)
        svc.cancel(cls, ANA)
        self.assertEqual(svc.roster(cls), ["pia"])

    def test_B2_no_second_place_from_waitlist(self):
        _, svc, cls = setup()
        svc.book(cls, ANA)
        svc.book(cls, BEA)
        with self.assertRaises(Exception):
            svc.book(cls, BEA)

    def test_B3_leaving_waitlist_is_free(self):
        clock, svc, cls = setup()
        svc.book(cls, ANA)
        svc.book(cls, BEA)
        clock.hours_before_start(2)
        self.assertEqual(svc.cancel(cls, BEA), D("0.00"))

    def test_B4_no_promotion_in_last_hour(self):
        clock, svc, cls = setup()
        svc.book(cls, ANA)
        svc.book(cls, BEA)
        clock.hours_before_start(0.5)
        svc.cancel(cls, ANA)
        self.assertEqual(svc.roster(cls), [])

    def test_B5_promoted_member_leaves_waitlist(self):
        clock, svc, cls = setup()
        svc.book(cls, ANA)
        svc.book(cls, BEA)
        clock.hours_before_start(20)
        svc.cancel(cls, ANA)
        self.assertEqual(svc.waitlist(cls), [])

    def test_G1_waitlist_capped_at_ten(self):
        _, svc, cls = setup()
        svc.book(cls, ANA)
        for i in range(10):
            svc.book(cls, Member(f"w{i}"))
        with self.assertRaises(Exception):
            svc.book(cls, Member("w10"))
