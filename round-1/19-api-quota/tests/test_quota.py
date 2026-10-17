import unittest
from datetime import datetime

from quota import Meter

T0 = datetime(2026, 1, 10, 12, 0, 0)


class TestQuota(unittest.TestCase):
    def test_first_request_allowed(self):
        meter = Meter()
        meter.create_key("k1", "FREE", T0)
        self.assertEqual(meter.request("k1", T0), 200)


if __name__ == "__main__":
    unittest.main()
