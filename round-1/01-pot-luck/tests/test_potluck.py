import unittest

from potluck.app import build_app


class ScriptedRng:
    def __init__(self, values):
        self.values = list(values)

    def randint(self, low, high):
        return self.values.pop(0)


class TestPotLuck(unittest.TestCase):
    def test_buying_entries(self):
        api, _ = build_app(rng=ScriptedRng([12345, 67890]))
        _, body = api.register({"name": "Ann", "email": "ann@example.com"})
        api.open_draw()
        status, bought = api.buy(body["participant_id"], {"quantity": 2})
        self.assertEqual(status, 201)
        self.assertEqual([e["code"] for e in bought["entries"]], ["12345", "67890"])


if __name__ == "__main__":
    unittest.main()
