import unittest
from datetime import datetime

from docs import DocStore


class Clock:
    def __init__(self):
        self.current = datetime(2026, 5, 4, 9, 0)

    def now(self):
        return self.current


class TestDocs(unittest.TestCase):
    def test_save_makes_next_version(self):
        store = DocStore(Clock())
        store.create("note", "ana", "draft")
        self.assertEqual(store.save("note", "ana", "better draft", base_version=1).number, 2)


if __name__ == "__main__":
    unittest.main()
