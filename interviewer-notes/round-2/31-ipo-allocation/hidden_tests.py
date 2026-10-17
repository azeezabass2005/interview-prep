import unittest

from ipo.app import build_app


def book(*orders, offering=10_000):
    api = build_app()
    api.create("X", offering)
    for investor, shares, limit in orders:
        api.submit("X", {"investor": investor, "shares": shares, "limit": limit})
    return api


RETAIL_FULL = (("r1", 1_000, "21"), ("r2", 1_000, "21"))


class HiddenIpo(unittest.TestCase):
    def test_B1_orders_below_price_drop_out(self):
        api = book(("i1", 3_000, "21"), ("i3", 6_000, "19"))
        self.assertEqual(api.close("X", "20")[1]["allocations"].get("i3", 0), 0)

    def test_B2_unused_retail_moves_to_institutional(self):
        api = book(("r1", 1_000, "21"), ("i1", 9_000, "21"))
        self.assertEqual(api.close("X", "20")[1]["allocations"]["i1"], 9_000)

    def test_B3_pro_rata_rounds_down(self):
        api = book(*RETAIL_FULL, ("i1", 6_500, "21"), ("i2", 4_500, "21"))
        alloc = api.close("X", "20")[1]["allocations"]
        self.assertEqual((alloc["i1"], alloc["i2"]), (4_800, 3_200))

    def test_B4_leftover_ties_to_earliest(self):
        api = book(*RETAIL_FULL, ("i1", 3_000, "21"), ("i2", 3_000, "21"), ("i3", 3_000, "21"))
        alloc = api.close("X", "20")[1]["allocations"]
        self.assertEqual((alloc["i1"], alloc["i2"], alloc["i3"]), (2_700, 2_700, 2_600))

    def test_B5_amend_loses_time_priority(self):
        api = book(*RETAIL_FULL, ("i1", 3_000, "21"), ("i2", 3_000, "21"), ("i3", 3_000, "21"))
        api.amend("X", {"investor": "i1", "limit": "22"})
        alloc = api.close("X", "20")[1]["allocations"]
        self.assertEqual((alloc["i1"], alloc["i2"], alloc["i3"]), (2_600, 2_700, 2_700))
