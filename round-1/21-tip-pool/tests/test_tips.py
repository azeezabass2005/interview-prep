import unittest

from tips.app import build_app


class TestTips(unittest.TestCase):
    def test_two_servers_split_card_tips(self):
        api = build_app()
        for name in ("ann", "ben"):
            api.shift({"employee": name, "role": "SERVER", "start": "2026-03-04T17:00", "end": "2026-03-04T22:00"})
        api.declare({"day": "2026-03-04", "service": "DINNER", "card": "100", "cash": "0"})
        self.assertEqual(api.distribute("2026-03-04", "DINNER"), (200, {"ann": "48.50", "ben": "48.50"}))


if __name__ == "__main__":
    unittest.main()
