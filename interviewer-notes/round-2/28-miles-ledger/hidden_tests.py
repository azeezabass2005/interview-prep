import unittest

from loyalty.app import build_app


def member(api, mid):
    api.join(mid, mid)


def fly(api, fid, mid, on, fare):
    status, body = api.fly({"flight_id": fid, "member_id": mid, "date": on, "fare": fare})
    assert status == 201, body
    return body


class HiddenLoyalty(unittest.TestCase):
    def setUp(self):
        self.api, _ = build_app()
        member(self.api, "m")

    def test_B1_gold_bonus_is_fifty_percent(self):
        fly(self.api, "F0", "m", "2026-01-05", "10000")
        self.assertEqual(fly(self.api, "F1", "m", "2026-01-10", "412.80"), {"base_miles": 2060, "bonus_miles": 1030})

    def test_B2_only_base_miles_qualify(self):
        fly(self.api, "F0", "m", "2026-01-05", "5000")
        fly(self.api, "F1", "m", "2026-01-10", "4000")
        self.assertEqual(self.api.account("m", "2026-02-01")[1]["tier"], "SILVER")

    def test_B3_oldest_miles_spent_first(self):
        fly(self.api, "F0", "m", "2024-01-10", "200")
        fly(self.api, "F1", "m", "2025-01-10", "200")
        self.api.redeem("m", 1000, "2025-02-01")
        self.assertEqual(self.api.account("m", "2026-02-01")[1]["balance"], 1000)

    def test_B4_expired_on_anniversary(self):
        fly(self.api, "F0", "m", "2024-03-01", "100")
        self.assertEqual(self.api.account("m", "2026-02-28")[1]["balance"], 500)
        self.assertEqual(self.api.account("m", "2026-03-01")[1]["balance"], 0)

    def test_B5_transfers_do_not_qualify(self):
        member(self.api, "r")
        fly(self.api, "F0", "m", "2026-01-05", "1000")
        fly(self.api, "F1", "r", "2026-01-05", "4400")
        self.api.transfer({"from": "m", "to": "r", "miles": 5000, "date": "2026-02-01"})
        self.assertEqual(self.api.account("r", "2026-02-02")[1]["tier"], "BASE")
