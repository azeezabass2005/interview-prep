import unittest
from datetime import datetime, timedelta

from chat import Chat

T0 = datetime(2026, 5, 4, 9, 0)


def chat():
    c = Chat()
    c.create_channel("general", ["ana", "ben"])
    c.create_channel("random", ["ana", "ben"])
    return c


class HiddenChat(unittest.TestCase):
    def test_B1_sequence_per_channel(self):
        c = chat()
        c.post("general", "ana", "one", "c1", T0)
        self.assertEqual(c.post("random", "ana", "two", "c2", T0).seq, 1)

    def test_B2_own_messages_are_not_unread(self):
        c = chat()
        c.post("general", "ana", "a", "c1", T0)
        c.post("general", "ana", "b", "c2", T0)
        c.post("general", "ben", "c", "c3", T0)
        self.assertEqual(c.unread("general", "ana"), 1)

    def test_B3_only_author_can_edit(self):
        c = chat()
        m = c.post("general", "ana", "hi", "c1", T0)
        with self.assertRaises(Exception):
            c.edit("general", m.seq, "ben", "hacked", T0 + timedelta(minutes=1))

    def test_B4_before_is_exclusive(self):
        c = chat()
        for i in range(5):
            c.post("general", "ana", f"m{i}", f"c{i}", T0)
        self.assertEqual([m.seq for m in c.history("general", before=3, limit=2)], [2, 1])

    def test_B5_mentions_only_members(self):
        c = chat()
        c.post("general", "ana", "hi @zed and @ben", "c1", T0)
        self.assertEqual([n[0] for n in c.notifications], ["ben"])
