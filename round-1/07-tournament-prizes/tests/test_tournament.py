import unittest
from decimal import Decimal

from tournament import Tournament


class TestTournament(unittest.TestCase):
    def test_heads_up_positions(self):
        t = Tournament()
        for p in ("ana", "ben", "cai"):
            t.register(p)
        t.close_registration()
        t.eliminate({"cai": 500})
        t.eliminate({"ben": 800})
        self.assertEqual(t.finish, {"cai": 3, "ben": 2, "ana": 1})


if __name__ == "__main__":
    unittest.main()
