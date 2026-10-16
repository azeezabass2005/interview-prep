import unittest

from league.app import build_app


class TestLeague(unittest.TestCase):
    def test_open_frames(self):
        api, _ = build_app()
        status, body = api.score_game([3, 4] * 10)
        self.assertEqual(status, 200)
        self.assertEqual(body["score"], 70)


if __name__ == "__main__":
    unittest.main()
