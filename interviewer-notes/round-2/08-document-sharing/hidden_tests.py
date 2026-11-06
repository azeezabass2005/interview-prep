import json
import unittest
from unittest import mock

from vault.services.documents import DocumentService
from tests.helpers import World


class HiddenChecks(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_doc801_links_stop_working_when_they_expire(self):
        doc = self.w.doc(self.w.nadia)
        link = self.w.call("POST", f"/documents/{doc['id']}/links", self.w.nadia, {"hours": 48}).body
        self.w.clock.advance(hours=47)
        self.assertEqual(self.w.call("GET", f"/s/{link['token']}").status, 200)
        self.w.clock.advance(hours=1)
        self.assertEqual(self.w.call("GET", f"/s/{link['token']}").status, 404)

    def test_doc805_search_only_returns_readable_documents(self):
        self.w.doc(self.w.nadia, title="Project Falcon - acquisition of Northwind (CONFIDENTIAL)")
        kite = self.w.doc(self.w.nadia, title="Project Kite overview")
        self.w.call("POST", f"/documents/{kite['id']}/shares", self.w.nadia, {"user_id": "usr_tom", "permission": "view"})
        self.assertEqual([d["title"] for d in self.w.call("GET", "/search?q=project", self.w.tom).body["documents"]],
                         ["Project Kite overview"])
        self.assertEqual(len(self.w.call("GET", "/search?q=project", self.w.nadia).body["documents"]), 2)

    def test_doc810_documents_with_the_same_timestamp_are_not_skipped(self):
        ids = {self.w.doc(self.w.nadia, title=f"Imported {i:02d}")["id"] for i in range(25)}
        first = self.w.call("GET", "/documents", self.w.nadia).body
        second = self.w.call("GET", f"/documents?cursor={first['next_cursor']}", self.w.nadia).body
        seen = [d["id"] for d in first["documents"] + second["documents"]]
        self.assertEqual(len(seen), 25)
        self.assertEqual(set(seen), ids)
        self.assertIsNone(second["next_cursor"])

    def test_doc815_preview_follows_the_current_version(self):
        doc = self.w.doc(self.w.nadia, content="old numbers")
        self.assertEqual(self.w.call("GET", f"/documents/{doc['id']}/preview", self.w.nadia).body["version"], 1)
        self.w.call("PATCH", f"/documents/{doc['id']}", self.w.nadia, {"content": "new numbers here", "version": 1})
        with mock.patch.object(DocumentService, "_render_preview", autospec=True,
                               side_effect=DocumentService._render_preview) as render:
            first = self.w.call("GET", f"/documents/{doc['id']}/preview", self.w.nadia).body
            self.w.call("GET", f"/documents/{doc['id']}/preview", self.w.nadia)
        self.assertEqual((first["version"], first["words"]), (2, 3))
        self.assertEqual(render.call_count, 1)

    def test_doc820_body_limit_does_not_trust_headers(self):
        body = json.dumps({"title": "Big", "content": "x" * 1_100_000}).encode()
        self.assertEqual(self.w.call("POST", "/documents", self.w.nadia, raw=body).status, 413)
        self.assertEqual(self.w.call("POST", "/documents", self.w.nadia, raw=body, headers={"Content-Length": "100"}).status, 413)
        self.assertEqual(self.w.call("POST", "/documents", self.w.nadia, {"title": "Small", "content": "ok"}).status, 201)


if __name__ == "__main__":
    unittest.main()
