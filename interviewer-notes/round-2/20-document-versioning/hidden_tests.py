import threading
import unittest
from unittest import mock

from docstore.errors import VersionConflict
from docstore.repositories.versions import VersionRepository
from tests.helpers import World


class HiddenDocs(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_DOC2001_optimistic_concurrency(self):
        doc = self.w.new_doc("v1")
        a, b = self.w.editing(), self.w.editing()
        barrier = threading.Barrier(2, timeout=3)
        original = VersionRepository.max_version
        calls = {"n": 0}
        lock = threading.Lock()

        def paused(repo, doc_id):
            result = original(repo, doc_id)
            with lock:
                calls["n"] += 1
                first = calls["n"] <= 2
            if first:
                try:
                    barrier.wait()
                except threading.BrokenBarrierError:
                    pass
            return result

        outcomes = []

        def run(svc, text):
            try:
                outcomes.append(svc.save(doc, "analyst", text, 1))
            except VersionConflict:
                outcomes.append("conflict")

        with mock.patch.object(VersionRepository, "max_version", paused):
            threads = [threading.Thread(target=run, args=(a, "alice's paragraph")),
                       threading.Thread(target=run, args=(b, "bob's paragraph"))]
            for t in threads:
                t.start()
            for t in threads:
                t.join(10)
        self.assertEqual(sorted(map(str, outcomes)), ["2", "conflict"])
        self.assertEqual(self.w.api.get_history(doc).body["versions"], [1, 2])
        self.assertEqual(self.w.api.put_content("ana", doc, {"content": "stale", "base_version": 1}).status, 409)

    def test_DOC2002_search_latest_version_only(self):
        doc = self.w.new_doc("Meeting with Client Acme about budget")
        self.w.api.put_content("ana", doc, {"content": "Meeting about budget", "base_version": 1})
        self.assertEqual(self.w.api.get_search("Acme").body["doc_ids"], [])
        self.assertEqual(self.w.api.get_search("budget").body["doc_ids"], [doc])

    def test_DOC2003_restore_creates_new_version_with_old_content(self):
        doc = self.w.new_doc("A")
        self.w.api.put_content("ana", doc, {"content": "B", "base_version": 1})
        self.assertEqual(self.w.api.post_restore("ana", doc, 1).body["version"], 3)
        self.assertEqual(self.w.api.get_document(doc).body["content"], "A")
        self.assertEqual(self.w.api.get_history(doc).body["versions"], [1, 2, 3])

    def test_DOC2004_unchanged_save_is_noop(self):
        doc = self.w.new_doc("A")
        self.w.api.put_content("ana", doc, {"content": "B", "base_version": 1})
        self.assertEqual(self.w.api.put_content("ana", doc, {"content": "B", "base_version": 2}).body["version"], 2)
        self.assertEqual(self.w.api.get_history(doc).body["versions"], [1, 2])
