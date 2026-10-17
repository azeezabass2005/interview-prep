import unittest

from potluck.app import build_app


class ScriptedRng:
    def __init__(self, values):
        self.values = list(values)

    def randint(self, low, high):
        return self.values.pop(0)


def setup(codes, winning):
    api, store = build_app(rng=ScriptedRng(list(codes) + [winning]))
    _, ann = api.register({"name": "Ann", "email": "ann@example.com"})
    _, draw = api.open_draw()
    return api, store, ann["participant_id"], draw["draw_id"]


class HiddenPotLuck(unittest.TestCase):
    def test_B1_codes_are_zero_padded(self):
        api, store, pid, draw_id = setup([42, 0, 99999], 12345)
        _, bought = api.buy(pid, {"quantity": 3})
        self.assertEqual([e["code"] for e in bought["entries"]], ["00042", "00000", "99999"])

    def test_B2_matching_is_positional(self):
        api, store, pid, draw_id = setup([54321], 12345)
        api.buy(pid, {"quantity": 1})
        api.close_draw(draw_id)
        _, settled = api.settle_draw(draw_id)
        self.assertEqual(settled["payouts"], [])
        self.assertEqual(settled["rollover_cents"], 1_000_500)

    def test_B3_highest_tier_paid_first(self):
        api, store, pid, draw_id = setup([12345, 12340], 12345)
        api.buy(pid, {"quantity": 2})
        api.close_draw(draw_id)
        _, settled = api.settle_draw(draw_id)
        amounts = {p["matches"]: p["amount_cents"] for p in settled["payouts"]}
        self.assertEqual(amounts[5], 1_001_000)
        self.assertEqual(amounts.get(4, 0), 0)

    def test_B4_cancelled_entries_not_in_pot(self):
        api, store, pid, draw_id = setup([11111, 22222, 33333], 99999)
        _, bought = api.buy(pid, {"quantity": 3})
        api.cancel(pid, bought["entries"][0]["entry_id"])
        _, closed = api.close_draw(draw_id)
        self.assertEqual(closed["pot_cents"], 1_001_000)

    def test_B5_entry_limit_is_per_draw(self):
        api, store, pid, draw_id = setup([10000 + i for i in range(10)] + [99999] + [50000] * 11, 99999)
        api.buy(pid, {"quantity": 10})
        self.assertEqual(api.buy(pid, {"quantity": 1})[0], 422)
        api.close_draw(draw_id)
        api.settle_draw(draw_id)
        api.open_draw()
        self.assertEqual(api.buy(pid, {"quantity": 1})[0], 201)
