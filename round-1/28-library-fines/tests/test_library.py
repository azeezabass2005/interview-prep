import unittest

from library.app import build_app


class TestLibrary(unittest.TestCase):
    def test_book_due_in_21_days(self):
        api, _ = build_app()
        api.setup({"MAIN": []}, {"b1": ("BOOK", "MAIN")}, ["ann"])
        self.assertEqual(api.checkout("ann", "b1", "2026-03-02"), (201, {"due": "2026-03-23"}))


if __name__ == "__main__":
    unittest.main()
