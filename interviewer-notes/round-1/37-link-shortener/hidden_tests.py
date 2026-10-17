import unittest
from datetime import datetime

from shortener import Shortener, encode

NOW = datetime(2026, 5, 4, 12, 0)


class Clock:
    def __init__(self):
        self.current = NOW

    def now(self):
        return self.current


class HiddenShortener(unittest.TestCase):
    def test_B1_aliases_case_insensitive(self):
        s = Shortener(Clock())
        s.shorten("ana", "https://a.example", alias="Promo")
        with self.assertRaises(Exception):
            s.shorten("ben", "https://b.example", alias="promo")

    def test_B2_reserved_words(self):
        with self.assertRaises(Exception):
            Shortener(Clock()).shorten("ana", "https://a.example", alias="admin")

    def test_B3_dedupe_per_user(self):
        s = Shortener(Clock())
        s.shorten("ana", "https://a.example")
        self.assertEqual(s.shorten("ben", "https://a.example").owner, "ben")

    def test_B4_expired_from_expiry_time(self):
        s = Shortener(Clock())
        link = s.shorten("ana", "https://a.example", expires_at=NOW)
        self.assertEqual(s.resolve(link.code), (410, None))

    def test_B5_base62_most_significant_first(self):
        self.assertEqual(encode(62), "000010")
