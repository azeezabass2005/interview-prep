import unittest

from tests.helpers import World, call


class TestGateway(unittest.TestCase):
    def setUp(self):
        self.w = World()
        self.gw = self.w.gateway()

    def tearDown(self):
        self.w.cleanup()

    def test_unknown_key(self):
        self.assertEqual(call(self.gw, "nope").status, 401)

    def test_allows_up_to_limit_on_one_instance(self):
        statuses = [call(self.gw, "k-acme-admin").status for _ in range(61)]
        self.assertEqual(statuses.count(200), 60)
        self.assertEqual(statuses[-1], 429)

    def test_headers(self):
        resp = call(self.gw, "k-acme-admin")
        self.assertEqual((resp.headers["X-RateLimit-Limit"], resp.headers["X-RateLimit-Remaining"]), ("60", "59"))

    def test_new_window_resets(self):
        for _ in range(61):
            call(self.gw, "k-acme-admin")
        self.w.clock.advance(60)
        self.assertEqual(call(self.gw, "k-acme-admin").status, 200)


if __name__ == "__main__":
    unittest.main()
