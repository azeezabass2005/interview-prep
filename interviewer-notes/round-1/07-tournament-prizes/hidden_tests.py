import unittest
from decimal import Decimal

from tournament import Tournament, TournamentError


def field(n, guarantee=0):
    t = Tournament(guarantee)
    for i in range(n):
        t.register(f"p{i}")
    return t


class HiddenTournament(unittest.TestCase):
    def test_B1_at_most_two_reentries(self):
        t = field(3)
        for _ in range(2):
            t.eliminate({"p0": 100})
            t.register("p0")
        t.eliminate({"p0": 100})
        with self.assertRaises(TournamentError):
            t.register("p0")

    def test_B2_reentries_add_to_pool(self):
        t = field(10)
        for p in ("p0", "p1"):
            t.eliminate({p: 100})
            t.register(p)
        self.assertEqual(t.prize_pool(), Decimal("1020"))

    def test_B3_ten_entries_pay_three_places(self):
        self.assertEqual(field(10).prizes(), {1: Decimal("425"), 2: Decimal("255"), 3: Decimal("170")})

    def test_B4_leftover_dollars_to_first(self):
        self.assertEqual(field(11).prizes(), {1: Decimal("468"), 2: Decimal("280"), 3: Decimal("187")})

    def test_B5_bigger_stack_finishes_higher(self):
        t = field(4)
        t.close_registration()
        self.assertEqual(t.eliminate({"p0": 1000, "p1": 500}), {"p1": 4, "p0": 3})
