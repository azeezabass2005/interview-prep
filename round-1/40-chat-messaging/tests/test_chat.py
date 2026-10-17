import unittest
from datetime import datetime

from chat import Chat

T0 = datetime(2026, 5, 4, 9, 0)


class TestChat(unittest.TestCase):
    def test_post_and_history(self):
        chat = Chat()
        chat.create_channel("general", ["ana", "ben"])
        chat.post("general", "ana", "hello", "c1", T0)
        self.assertEqual([m.text for m in chat.history("general")], ["hello"])


if __name__ == "__main__":
    unittest.main()
