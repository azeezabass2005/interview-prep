import threading
import unittest
from datetime import datetime
from unittest import mock

from chat.repositories.messages import MessageRepository
from chat.services.messaging import MessagingService
from tests.helpers import T0, World


class HiddenChat(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_MSG1001_ordered_by_server_sequence(self):
        self.w.send("ann", "lunch?")
        self.w.send("bob", "yes!", client_offset_s=-170)  # Bob's phone is ~3 minutes behind
        self.w.send("cy", "me too")
        bodies = [m["body"] for m in self.w.api.get_messages("ann", "lunch").body["messages"]]
        self.assertEqual(bodies, ["lunch?", "yes!", "me too"])

    def test_MSG1002_overlapping_retries_store_one_message(self):
        a, b = MessagingService(self.w.db, self.w.clock), MessagingService(self.w.db, self.w.clock)
        barrier = threading.Barrier(2, timeout=3)
        original = MessageRepository.find_by_client_id
        calls = {"n": 0}
        lock = threading.Lock()

        def paused(repo, conversation_id, sender, client_msg_id):
            result = original(repo, conversation_id, sender, client_msg_id)
            with lock:
                calls["n"] += 1
                first = calls["n"] <= 2
            if first:
                try:
                    barrier.wait()
                except threading.BrokenBarrierError:
                    pass
            return result

        results = [None, None]

        def run(i, svc):
            results[i] = svc.send("lunch", "ann", "c-77", "on my way", T0)

        with mock.patch.object(MessageRepository, "find_by_client_id", paused):
            threads = [threading.Thread(target=run, args=(i, s)) for i, s in enumerate((a, b))]
            for t in threads:
                t.start()
            for t in threads:
                t.join(10)
        self.assertEqual(self.w.messages.count("lunch"), 1)
        self.assertEqual(results[0].message_id, results[1].message_id)
        other = a.send("lunch", "bob", "c-77", "different sender", T0)
        self.assertNotEqual(other.message_id, results[0].message_id)

    def test_MSG1003_read_position_never_moves_back(self):
        for i in range(5):
            self.w.send("ann", f"m{i}")
        self.w.api.post_read("bob", "lunch", {"seq": 5})  # phone
        self.w.api.post_read("bob", "lunch", {"seq": 3})  # stale laptop
        self.assertEqual(self.w.api.get_unread("bob", "lunch").body["unread"], 0)

    def test_MSG1004_scroll_back_returns_messages_just_before_cursor(self):
        for i in range(1, 11):
            self.w.send("ann", f"m{i}")
        seqs = [m["seq"] for m in self.w.api.get_messages("bob", "lunch", before=8, limit=3).body["messages"]]
        self.assertEqual(seqs, [5, 6, 7])
