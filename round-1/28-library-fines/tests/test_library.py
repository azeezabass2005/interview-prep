import unittest
from datetime import date

from library import Library


class TestLibrary(unittest.TestCase):
    def test_book_due_in_three_weeks(self):
        lib = Library()
        lib.add_item("b1", "BOOK")
        lib.add_patron("ana")
        self.assertEqual(lib.checkout("ana", "b1", date(2026, 3, 2)).due, date(2026, 3, 23))


if __name__ == "__main__":
    unittest.main()
