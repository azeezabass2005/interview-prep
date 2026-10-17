import unittest

from tourney.app import build_app


def field(n):
    api, _ = build_app()
    api.create("t")
    names = [f"p{i:02d}" for i in range(n)]
    for name in names:
        api.enter("t", name)
    api.start("t")
    return api, names


class HiddenTourney(unittest.TestCase):
    def test_B1_guarantee_after_rake(self):
        api, _ = field(20)
        self.assertEqual(api.pool("t")[1]["pool_cents"], 200_000)

    def test_B2_ten_entries_pay_two(self):
        api, names = field(10)
        for hand, name in enumerate(names[1:], start=1):
            api.eliminate("t", {"hand": hand, "eliminated": [name], "winners": [names[0]]})
        prizes = api.finish("t")[1]["prizes"]
        self.assertEqual(len([v for v in prizes.values() if v > 0]), 2)

    def test_B3_tied_players_split_places(self):
        api, names = field(20)
        winner, ben, cy, dee = names[0], names[1], names[2], names[3]
        hand = 1
        for name in names[4:]:
            api.eliminate("t", {"hand": hand, "eliminated": [name], "winners": [winner]})
            hand += 1
        api.eliminate("t", {"hand": hand, "eliminated": [dee], "winners": [winner]})
        api.eliminate("t", {"hand": hand + 1, "eliminated": [ben, cy], "winners": [winner]})
        result = api.finish("t")[1]
        self.assertEqual((result["prizes"][ben], result["prizes"][cy]), (50_000, 50_000))
        self.assertEqual(sum(result["prizes"].values()), result["pool_cents"])

    def test_B4_at_most_two_reentries(self):
        api, names = field(3)
        for hand in range(1, 4):
            api.eliminate("t", {"hand": hand, "eliminated": ["p02"], "winners": ["p00"]})
            status = api.enter("t", "p02")[0]
            self.assertEqual(status, 201 if hand < 3 else 409)

    def test_B5_late_registration_through_level_6(self):
        api, _ = field(3)
        for _ in range(5):
            api.next_level("t")
        self.assertEqual(api.enter("t", "late6")[0], 201)
        api.next_level("t")
        self.assertEqual(api.enter("t", "late7")[0], 409)
