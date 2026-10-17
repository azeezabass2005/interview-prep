import unittest
from datetime import datetime

from shortener import Shortener


class Clock:
    def now(self):
        return datetime(2026, 5, 4, 12, 0)


class TestShortener(unittest.TestCase):
    def test_first_link_resolves(self):
        s = Shortener(Clock())
        link = s.shorten("ana", "https://example.com/q3-report")
        self.assertEqual(s.resolve(link.code), (301, "https://example.com/q3-report"))


if __name__ == "__main__":
    unittest.main()
