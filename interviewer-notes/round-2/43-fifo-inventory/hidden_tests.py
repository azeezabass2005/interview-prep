import unittest

from inventory.app import build_app


class HiddenInventory(unittest.TestCase):
    def setUp(self):
        self.api, self.store = build_app()

    def test_B1_oldest_first(self):
        self.api.receive("W", "NJ", 100, "2.00", "2026-01-01")
        self.api.receive("W", "NJ", 50, "2.50", "2026-01-05")
        self.assertEqual(self.api.ship("S1", "W", "NJ", 50)[1]["cogs"], "100.00")

    def test_B2_short_shipment_changes_nothing(self):
        self.api.receive("W", "NJ", 10, "2.00", "2026-01-01")
        self.assertEqual(self.api.ship("S1", "W", "NJ", 15)[0], 409)
        self.assertEqual(self.api.value("W", "NJ")[1]["on_hand"], 10)

    def test_B3_partial_layer_keeps_remainder(self):
        self.api.receive("W", "NJ", 100, "2.00", "2026-01-01")
        self.api.ship("S1", "W", "NJ", 30)
        self.assertEqual(self.api.value("W", "NJ")[1]["value"], "140.00")

    def test_B4_transfers_keep_received_date(self):
        self.api.receive("W", "NJ", 10, "1.00", "2026-01-01")
        self.api.receive("W", "NY", 10, "5.00", "2026-02-01")
        self.api.receive("W", "NY", 10, "7.00", "2026-04-01")
        self.api.transfer("W", "NJ", "NY", 10, "2026-03-01")
        self.assertEqual(self.api.ship("S1", "W", "NY", 10)[1]["cogs"], "10.00")

    def test_B5_return_at_shipment_average(self):
        self.api.receive("W", "NJ", 100, "2.00", "2026-01-01")
        self.api.ship("S1", "W", "NJ", 40)
        self.api.receive("W", "NJ", 10, "3.00", "2026-01-05")
        self.assertEqual(self.api.return_units("S1", 5, "2026-01-09")[1]["unit_cost"], "2.0000")
