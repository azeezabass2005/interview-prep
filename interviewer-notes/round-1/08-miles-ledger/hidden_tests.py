import unittest
from datetime import date

from miles import MilesError, MilesLedger


def member(*names):
    ledger = MilesLedger()
    for n in names:
        ledger.join(n)
    return ledger


class HiddenMiles(unittest.TestCase):
    def test_B1_bonus_on_base_miles(self):
        m = member("ana")
        m.fly("ana", date(2026, 1, 5), 50_000, "Y")
        self.assertEqual(m.fly("ana", date(2026, 2, 1), 1_000, "J"), 2_250)

    def test_B2_bonus_miles_do_not_qualify(self):
        m = member("ana")
        m.fly("ana", date(2026, 1, 5), 25_000, "Y")
        m.fly("ana", date(2026, 2, 1), 20_000, "Y")
        self.assertEqual(m.status_on("ana", date(2026, 3, 1)), "SILVER")

    def test_B3_status_lasts_through_next_year(self):
        m = member("ana")
        m.fly("ana", date(2025, 6, 1), 30_000, "Y")
        self.assertEqual(m.fly("ana", date(2026, 2, 1), 1_000, "Y"), 1_250)

    def test_B4_redemption_is_activity(self):
        m = member("ana")
        m.fly("ana", date(2025, 1, 10), 1_000, "Y")
        m.redeem("ana", date(2026, 6, 1), 500)
        self.assertEqual(m.balance("ana", date(2026, 12, 1)), 500)

    def test_B5_annual_transfer_limit_is_cumulative(self):
        m = member("ana", "ben")
        m.fly("ana", date(2026, 1, 5), 100_000, "Y")
        m.transfer("ana", "ben", date(2026, 2, 1), 30_000)
        with self.assertRaises(MilesError):
            m.transfer("ana", "ben", date(2026, 3, 1), 30_000)
