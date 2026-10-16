import unittest

from tips.app import build_app

DAY = "2026-03-04"


def shift(api, who, role, start, end):
    api.shift({"employee": who, "role": role, "start": f"{DAY}T{start}", "end": f"{DAY}T{end}"})


def example():
    api = build_app()
    shift(api, "alice", "SERVER", "17:00", "23:00")
    shift(api, "bob", "BARTENDER", "18:00", "23:00")
    shift(api, "cara", "BUSSER", "18:00", "22:00")
    shift(api, "dan", "MANAGER", "16:00", "23:59")
    shift(api, "eve", "HOST", "17:00", "18:30")
    api.declare({"day": DAY, "service": "DINNER", "card": "1000", "cash": "200"})
    return api.distribute(DAY, "DINNER")[1]


class HiddenTips(unittest.TestCase):
    def test_B1_cash_not_charged(self):
        self.assertEqual(example()["alice"], "585.00")

    def test_B2_managers_excluded(self):
        self.assertNotIn("dan", example())

    def test_B3_exactly_two_hours_eligible(self):
        api = build_app()
        shift(api, "a", "SERVER", "17:00", "22:00")
        shift(api, "c", "BUSSER", "18:00", "20:00")
        api.declare({"day": DAY, "service": "DINNER", "card": "0", "cash": "100"})
        self.assertIn("c", api.distribute(DAY, "DINNER")[1])

    def test_B4_roles_add_up(self):
        api = build_app()
        shift(api, "fay", "BUSSER", "16:00", "19:00")
        shift(api, "fay", "SERVER", "19:00", "22:00")
        shift(api, "gus", "SERVER", "17:00", "20:00")
        api.declare({"day": DAY, "service": "DINNER", "card": "0", "cash": "100"})
        self.assertEqual(api.distribute(DAY, "DINNER")[1], {"fay": "60.00", "gus": "40.00"})

    def test_B5_hours_split_by_service(self):
        api = build_app()
        shift(api, "ann", "SERVER", "14:00", "22:00")
        shift(api, "ben", "SERVER", "16:00", "22:00")
        api.declare({"day": DAY, "service": "DINNER", "card": "0", "cash": "100"})
        self.assertEqual(api.distribute(DAY, "DINNER")[1], {"ann": "50.00", "ben": "50.00"})
