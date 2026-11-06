import json
import unittest

from tests.helpers import World


class DocumentsTest(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_owner_reads_and_edits(self):
        doc = self.w.doc(self.w.nadia)
        resp = self.w.call("PATCH", f"/documents/{doc['id']}", self.w.nadia, {"content": "Draft two", "version": 1})
        self.assertEqual((resp.status, resp.body["version"]), (200, 2))
        self.assertEqual(self.w.call("GET", f"/documents/{doc['id']}", self.w.nadia).body["content"], "Draft two")

    def test_stale_edit_conflicts(self):
        doc = self.w.doc(self.w.nadia)
        self.w.call("PATCH", f"/documents/{doc['id']}", self.w.nadia, {"content": "a", "version": 1})
        self.assertEqual(self.w.call("PATCH", f"/documents/{doc['id']}", self.w.nadia, {"content": "b", "version": 1}).status, 409)

    def test_unshared_documents_are_invisible(self):
        doc = self.w.doc(self.w.nadia)
        self.assertEqual(self.w.call("GET", f"/documents/{doc['id']}", self.w.tom).status, 404)
        self.assertEqual(self.w.call("GET", f"/documents/{doc['id']}", self.w.outsider).status, 404)

    def test_sharing_view_and_edit(self):
        doc = self.w.doc(self.w.nadia)
        self.w.call("POST", f"/documents/{doc['id']}/shares", self.w.nadia, {"user_id": "usr_tom", "permission": "view"})
        self.assertEqual(self.w.call("GET", f"/documents/{doc['id']}", self.w.tom).status, 200)
        self.assertEqual(self.w.call("PATCH", f"/documents/{doc['id']}", self.w.tom, {"content": "x", "version": 1}).status, 403)
        self.w.call("POST", f"/documents/{doc['id']}/shares", self.w.nadia, {"user_id": "usr_tom", "permission": "edit"})
        self.assertEqual(self.w.call("PATCH", f"/documents/{doc['id']}", self.w.tom, {"content": "x", "version": 1}).status, 200)

    def test_only_owner_shares(self):
        doc = self.w.doc(self.w.nadia)
        self.w.call("POST", f"/documents/{doc['id']}/shares", self.w.nadia, {"user_id": "usr_tom", "permission": "edit"})
        resp = self.w.call("POST", f"/documents/{doc['id']}/shares", self.w.tom, {"user_id": "usr_uma", "permission": "view"})
        self.assertEqual(resp.status, 403)

    def test_list_pages_through_everything_newest_first(self):
        for i in range(25):
            self.w.doc(self.w.nadia, title=f"Doc {i:02d}")
            self.w.clock.advance(minutes=1)
        first = self.w.call("GET", "/documents", self.w.nadia).body
        second = self.w.call("GET", f"/documents?cursor={first['next_cursor']}", self.w.nadia).body
        titles = [d["title"] for d in first["documents"] + second["documents"]]
        self.assertEqual(titles, [f"Doc {i:02d}" for i in range(24, -1, -1)])
        self.assertIsNone(second["next_cursor"])

    def test_list_includes_shared_documents(self):
        mine = self.w.doc(self.w.tom, title="Tom's notes")
        shared = self.w.doc(self.w.nadia, title="Shared deck")
        self.w.doc(self.w.nadia, title="Private")
        self.w.call("POST", f"/documents/{shared['id']}/shares", self.w.nadia, {"user_id": "usr_tom", "permission": "view"})
        titles = {d["title"] for d in self.w.call("GET", "/documents", self.w.tom).body["documents"]}
        self.assertEqual(titles, {"Tom's notes", "Shared deck"})

    def test_search_finds_own_documents(self):
        self.w.doc(self.w.nadia, title="Project Falcon model")
        self.w.doc(self.w.nadia, title="Lunch menu")
        found = self.w.call("GET", "/search?q=falcon", self.w.nadia).body["documents"]
        self.assertEqual([d["title"] for d in found], ["Project Falcon model"])

    def test_preview(self):
        doc = self.w.doc(self.w.nadia, content="one two three")
        self.assertEqual(self.w.call("GET", f"/documents/{doc['id']}/preview", self.w.nadia).body["words"], 3)


class LinksAndLimitsTest(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_share_link_opens_without_login(self):
        doc = self.w.doc(self.w.nadia, content="Term sheet")
        link = self.w.call("POST", f"/documents/{doc['id']}/links", self.w.nadia, {"hours": 48}).body
        self.assertEqual(self.w.call("GET", f"/s/{link['token']}").body["content"], "Term sheet")

    def test_revoked_link(self):
        doc = self.w.doc(self.w.nadia)
        link = self.w.call("POST", f"/documents/{doc['id']}/links", self.w.nadia, {"hours": 48}).body
        self.w.call("DELETE", f"/documents/{doc['id']}/links", self.w.nadia)
        self.assertEqual(self.w.call("GET", f"/s/{link['token']}").status, 404)

    def test_link_lifetime_is_bounded(self):
        doc = self.w.doc(self.w.nadia)
        self.assertEqual(self.w.call("POST", f"/documents/{doc['id']}/links", self.w.nadia, {"hours": 10_000}).status, 400)

    def test_large_declared_body_is_rejected(self):
        body = json.dumps({"title": "Big", "content": "x" * 1_100_000}).encode()
        resp = self.w.call("POST", "/documents", self.w.nadia, raw=body, headers={"Content-Length": str(len(body))})
        self.assertEqual(resp.status, 413)


if __name__ == "__main__":
    unittest.main()
