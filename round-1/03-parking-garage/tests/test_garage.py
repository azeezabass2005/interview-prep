import unittest

from garage.pricing import parking_fee
from garage.tickets import Garage
from tests.helpers import FakeClock, at


class TestPricing(unittest.TestCase):
    def test_short_stay_is_free(self):
        self.assertEqual(parking_fee(at(1, 10), at(1, 10, 25)), 0)

    def test_two_whole_hours(self):
        self.assertEqual(parking_fee(at(1, 10), at(1, 12)), 800)

    def test_cap_within_one_day(self):
        self.assertEqual(parking_fee(at(1, 10), at(1, 22)), 2400)

    def test_early_bird_example(self):
        self.assertEqual(parking_fee(at(1, 7, 15), at(1, 17, 30)), 1200)

    def test_pass_holder_free_on_weekday(self):
        self.assertEqual(parking_fee(at(1, 10), at(1, 15), pass_holder=True), 0)

    def test_lost_ticket(self):
        self.assertEqual(parking_fee(at(1, 10), at(1, 11), lost_ticket=True), 5000)

    def test_exit_before_entry_rejected(self):
        with self.assertRaises(ValueError):
            parking_fee(at(1, 10), at(1, 9))


class TestGarage(unittest.TestCase):
    def test_issue_and_exit(self):
        clock = FakeClock(at(1, 10))
        garage = Garage(clock)
        ticket = garage.issue_ticket("ABC123")
        clock.current = at(1, 13)
        self.assertEqual(garage.exit(ticket.ticket_id), 1200)
        self.assertEqual(garage.open_tickets(), [])


if __name__ == "__main__":
    unittest.main()
