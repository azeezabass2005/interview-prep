import unittest
from datetime import datetime, timedelta

from docs import DocStore

T0 = datetime(2026, 5, 4, 9, 0)


class Clock:
    def __init__(self):
        self.current = T0

    def now(self):
        return self.current


class HiddenDocs(unittest.TestCase):
    def test_B1_stale_base_version_conflicts(self):
        store = DocStore(Clock())
        store.create("note", "ana", "v1")
        store.save("note", "ben", "v2", base_version=1)
        with self.assertRaises(Exception):
            store.save("note", "ana", "v2-ana", base_version=1)

    def test_B2_restore_creates_new_version(self):
        store = DocStore(Clock())
        store.create("note", "ana", "a")
        store.save("note", "ana", "b", base_version=1)
        v = store.restore("note", "ana", 1)
        self.assertEqual((v.number, v.content, store.docs["note"].versions[2].content), (3, "a", "b"))

    def test_B3_published_version_kept(self):
        store = DocStore(Clock(), max_versions=3)
        store.create("note", "ana", "v1")
        store.publish("note", 1)
        for n in range(2, 5):
            store.save("note", "ana", f"v{n}", base_version=n - 1)
        self.assertEqual(sorted(store.docs["note"].versions), [1, 3, 4])

    def test_B4_expired_lock_ignored(self):
        clock = Clock()
        store = DocStore(clock)
        store.create("note", "ana", "v1")
        store.lock("note", "ana")
        clock.current = T0 + timedelta(minutes=31)
        self.assertEqual(store.save("note", "ben", "v2", base_version=1).number, 2)

    def test_B5_readers_see_published_version(self):
        store = DocStore(Clock())
        store.create("note", "ana", "v1")
        store.publish("note", 1)
        store.save("note", "ben", "v2 draft", base_version=1)
        self.assertEqual(store.read("note"), "v1")
