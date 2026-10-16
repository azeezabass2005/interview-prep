import unittest
from decimal import Decimal

from metering.app import build_app


class FakeClock:
    def __init__(self):
        self.t = Decimal("1772323200")

    def time(self):
        return self.t


class TestMetering(unittest.TestCase):
    def test_bucket_starts_full(self):
        api, _ = build_app(FakeClock())
        api.register("c1", "FREE")
        results = [api.request("c1", "/quote")[1]["allowed"] for _ in range(11)]
        self.assertEqual(results, [True] * 10 + [False])


if __name__ == "__main__":
    unittest.main()
