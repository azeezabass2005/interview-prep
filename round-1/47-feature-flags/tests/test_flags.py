import unittest

from flags import FlagService


class TestFlags(unittest.TestCase):
    def test_disabled_flag_is_off(self):
        flags = FlagService()
        flags.define("new-chart", enabled=False, percentage=100)
        self.assertFalse(flags.is_on("new-chart", "ana"))


if __name__ == "__main__":
    unittest.main()
