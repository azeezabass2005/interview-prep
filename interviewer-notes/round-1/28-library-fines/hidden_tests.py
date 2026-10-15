import unittest
from datetime import date, timedelta
from decimal import Decimal as D

from library.account import PatronAccount
from library.calendar import LibraryCalendar
from library.loans import checkout, fine_for, renew

MON = date(2026, 3, 2)


class HiddenLibrary(unittest.TestCase):
    def test_B1_due_date_moves_off_closed_day(self):
        cal = LibraryCalendar(holidays=[date(2026, 3, 9)])
        self.assertEqual(checkout("NEW_RELEASE", date(2026, 3, 6), cal).due_on, date(2026, 3, 10))

    def test_B2_sundays_do_not_accrue(self):
        cal = LibraryCalendar()
        loan = checkout("DVD", MON, cal)
        self.assertEqual(fine_for(loan, date(2026, 3, 16), cal), D("6.00"))

    def test_B3_grace_forgives_only_one_day(self):
        cal = LibraryCalendar()
        loan = checkout("BOOK", MON, cal)
        self.assertEqual(fine_for(loan, date(2026, 3, 25), cal), D("0.50"))

    def test_B4_renewal_extends_from_due_date(self):
        cal = LibraryCalendar()
        loan = checkout("BOOK", MON, cal)
        renew(loan, date(2026, 3, 10), cal)
        self.assertEqual(loan.due_on, date(2026, 4, 13))

    def test_B5_ten_dollars_blocks_borrowing(self):
        account = PatronAccount("p1")
        account.charge(D("10.00"))
        self.assertFalse(account.can_borrow())

    def test_G1_fine_capped_at_replacement_cost(self):
        cal = LibraryCalendar()
        loan = checkout("NEW_RELEASE", MON, cal)
        self.assertEqual(fine_for(loan, MON + timedelta(days=60), cal), D("30.00"))
