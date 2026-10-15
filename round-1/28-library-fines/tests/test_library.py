import unittest
from datetime import date
from decimal import Decimal as D

from library.account import PatronAccount
from library.calendar import LibraryCalendar
from library.loans import LoanError, checkout, fine_for, renew

MON = date(2026, 3, 2)


class TestLoans(unittest.TestCase):
    def setUp(self):
        self.cal = LibraryCalendar()

    def test_book_due_in_21_days(self):
        self.assertEqual(checkout("BOOK", MON, self.cal).due_on, date(2026, 3, 23))

    def test_on_time_return_no_fine(self):
        loan = checkout("DVD", MON, self.cal)
        self.assertEqual(fine_for(loan, date(2026, 3, 9), self.cal), D("0"))

    def test_book_one_day_late_is_forgiven(self):
        loan = checkout("BOOK", MON, self.cal)
        self.assertEqual(fine_for(loan, date(2026, 3, 24), self.cal), D("0"))

    def test_dvd_cannot_be_renewed(self):
        with self.assertRaises(LoanError):
            renew(checkout("DVD", MON, self.cal), MON, self.cal)

    def test_renewal_limit(self):
        loan = checkout("BOOK", MON, self.cal)
        renew(loan, MON, self.cal)
        renew(loan, MON, self.cal)
        with self.assertRaises(LoanError):
            renew(loan, MON, self.cal)


class TestAccount(unittest.TestCase):
    def test_small_balance_can_borrow(self):
        account = PatronAccount("p1")
        account.charge(D("3.00"))
        self.assertTrue(account.can_borrow())


if __name__ == "__main__":
    unittest.main()
