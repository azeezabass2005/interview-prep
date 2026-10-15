import unittest

from garage.pricing import parking_fee
from garage.tickets import Garage
from tests.helpers import FakeClock, at


class HiddenGarage(unittest.TestCase):
    def test_B1_early_bird_requires_exit_before_seven_pm(self):
        self.assertEqual(parking_fee(at(1, 7), at(1, 19, 30)), 2400)

    def test_B2_exactly_thirty_minutes_is_free(self):
        self.assertEqual(parking_fee(at(1, 10), at(1, 10, 30)), 0)

    def test_B3_cap_is_per_24_hours(self):
        self.assertEqual(parking_fee(at(0, 10), at(1, 12)), 3200)

    def test_B4_nine_oclock_is_not_early_bird(self):
        self.assertEqual(parking_fee(at(1, 9), at(1, 17)), 2400)

    def test_G1_early_bird_never_costs_more(self):
        self.assertEqual(parking_fee(at(1, 7), at(1, 8)), 400)

    def test_G2_ticket_closes_once(self):
        clock = FakeClock(at(1, 10))
        garage = Garage(clock)
        ticket = garage.issue_ticket("ABC123")
        clock.current = at(1, 12)
        garage.exit(ticket.ticket_id)
        clock.current = at(1, 18)
        with self.assertRaises(Exception):
            garage.exit(ticket.ticket_id)
