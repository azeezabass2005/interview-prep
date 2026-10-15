import unittest

from tests.helpers import World


class TestBoxOffice(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_hold_and_purchase_single_ticket(self):
        self.assertEqual(self.w.api.post_hold("ann", "ev1", {"seats": ["A1"]}).status, 200)
        resp = self.w.api.post_purchase("ann", "ev1", {"seats": ["A1"]})
        self.assertEqual(resp.status, 201)
        self.assertEqual(resp.body["total_cents"], 4850)

    def test_held_seat_unavailable_to_others(self):
        self.w.api.post_hold("ann", "ev1", {"seats": ["A1"]})
        self.assertEqual(self.w.api.post_hold("bob", "ev1", {"seats": ["A1"]}).status, 409)

    def test_cannot_buy_seat_you_did_not_hold(self):
        self.w.api.post_hold("ann", "ev1", {"seats": ["A1"]})
        self.assertEqual(self.w.api.post_purchase("bob", "ev1", {"seats": ["A1"]}).status, 409)

    def test_availability_list(self):
        self.w.api.post_hold("ann", "ev1", {"seats": ["A1", "A2"]})
        self.assertEqual(self.w.api.get_available("ev1").body["seats"], ["A3", "B1", "B2", "B3"])

    def test_refund_well_before_event(self):
        self.w.api.post_hold("ann", "ev1", {"seats": ["A1"]})
        order_id = self.w.api.post_purchase("ann", "ev1", {"seats": ["A1"]}).body["order_id"]
        self.assertEqual(self.w.api.post_refund(order_id).body["refunded_cents"], 4500)
        self.assertIn("A1", self.w.api.get_available("ev1").body["seats"])

    def test_too_many_seats(self):
        self.assertEqual(self.w.api.post_hold("ann", "ev1", {"seats": ["A1"] * 9}).status, 400)


if __name__ == "__main__":
    unittest.main()
