import hashlib
import unittest

from flags import FlagService, bucket


class HiddenFlags(unittest.TestCase):
    def test_B1_denylist_beats_allowlist(self):
        flags = FlagService()
        flags.define("f", allow={"ana"}, deny={"ana"})
        self.assertFalse(flags.is_on("f", "ana"))

    def test_B2_bucket_includes_flag_key(self):
        expected = int(hashlib.sha256(b"new-chart:ana").hexdigest()[:8], 16) % 100
        self.assertEqual(bucket("new-chart", "ana"), expected)

    def test_B3_zero_percent_is_nobody(self):
        flags = FlagService()
        flags.define("f", percentage=0)
        self.assertEqual([u for u in (f"user{i}" for i in range(1000)) if flags.is_on("f", u)], [])

    def test_B4_country_case_insensitive(self):
        flags = FlagService()
        flags.define("f", countries={"GB"})
        self.assertTrue(flags.is_on("f", "ben", country="gb"))

    def test_B5_prerequisites(self):
        flags = FlagService()
        flags.define("base", enabled=False)
        flags.define("f", allow={"ana"}, prerequisites=["base"])
        self.assertFalse(flags.is_on("f", "ana"))
