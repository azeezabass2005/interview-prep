import unittest

from tests.helpers import World


class TestChat(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_send_assigns_sequence(self):
        self.assertEqual(self.w.send("ann", "hi").body["seq"], 1)
        self.assertEqual(self.w.send("bob", "hey").body["seq"], 2)

    def test_recent_in_order_when_clocks_agree(self):
        for text in ("a", "b", "c"):
            self.w.send("ann", text)
        bodies = [m["body"] for m in self.w.api.get_messages("bob", "lunch").body["messages"]]
        self.assertEqual(bodies, ["a", "b", "c"])

    def test_sequential_retry_is_idempotent(self):
        first = self.w.send("ann", "hi", client_id="c-1")
        second = self.w.send("ann", "hi", client_id="c-1")
        self.assertEqual(first.body["message_id"], second.body["message_id"])

    def test_non_member_rejected(self):
        self.assertEqual(self.w.api.post_message("eve", "lunch", {"client_msg_id": "x", "body": "hi",
                                                                   "client_sent_at": "2026-04-02T12:00:00"}).status, 403)

    def test_unread_and_mark_read(self):
        for text in ("a", "b", "c"):
            self.w.send("ann", text)
        self.assertEqual(self.w.api.get_unread("bob", "lunch").body["unread"], 3)
        self.assertEqual(self.w.api.post_read("bob", "lunch", {"seq": 2}).body["unread"], 1)
        self.assertEqual(self.w.api.get_unread("ann", "lunch").body["unread"], 0)

    def test_moderation(self):
        self.assertEqual(self.w.send("ann", "oh heck").body["body"], "oh ****")


if __name__ == "__main__":
    unittest.main()
