import unittest

from utility.app import build_app


def bills(*readings):
    api = build_app()
    first = readings[0]
    api.open({"account_id": "A", "read_on": first[0], "import": first[1], "export": first[2]})
    return api, [api.read("A", {"read_on": d, "import": i, "export": e})[1] for d, i, e in readings[1:]]


class HiddenUtility(unittest.TestCase):
    def test_B1_register_rollover(self):
        _, out = bills(("2026-03-01", 99_900, 0), ("2026-03-31", 300, 0))
        self.assertEqual(out[0]["imported"], 400)

    def test_B2_tiers_scale_with_period(self):
        _, out = bills(("2026-03-01", 0, 0), ("2026-03-16", 400, 0))
        self.assertEqual(out[0]["energy"], "52.50")

    def test_B3_bank_is_consumed(self):
        _, out = bills(("2026-04-01", 0, 0), ("2026-05-01", 300, 450), ("2026-05-31", 700, 450),
                       ("2026-06-30", 1000, 450))
        self.assertEqual([b["billable_kwh"] for b in out], [0, 250, 300])

    def test_B4_service_charge_not_taxed(self):
        _, out = bills(("2026-01-01", 10_000, 2_000), ("2026-01-31", 10_700, 2_100))
        self.assertEqual(out[0]["total"], "90.75")

    def test_B5_true_up_on_period_ending_in_december(self):
        api, out = bills(("2026-10-15", 0, 0), ("2026-11-15", 100, 300), ("2026-12-15", 150, 350))
        self.assertEqual(out[1]["true_up_payout"], "8.00")
        self.assertEqual(api.bank("A")[1]["bank_kwh"], 0)
