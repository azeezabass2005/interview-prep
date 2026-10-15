import unittest

from tests.helpers import World


class TestDocs(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_create_is_version_one(self):
        doc = self.w.new_doc()
        self.assertEqual(self.w.api.get_document(doc).body["version"], 1)

    def test_save_creates_next_version(self):
        doc = self.w.new_doc()
        self.assertEqual(self.w.api.put_content("ana", doc, {"content": "v2", "base_version": 1}).body["version"], 2)
        self.assertEqual(self.w.api.get_history(doc).body["versions"], [1, 2])

    def test_unchanged_first_save_is_noop(self):
        doc = self.w.new_doc("same")
        self.assertEqual(self.w.api.put_content("ana", doc, {"content": "same", "base_version": 1}).body["version"], 1)

    def test_search_finds_text(self):
        doc = self.w.new_doc("Revenue outlook raised")
        self.assertEqual(self.w.api.get_search("outlook").body["doc_ids"], [doc])

    def test_deleted_doc_hidden(self):
        doc = self.w.new_doc("Revenue outlook raised")
        self.w.docs.delete(doc)
        self.assertEqual(self.w.api.get_search("outlook").body["doc_ids"], [])
        self.assertEqual(self.w.api.get_document(doc).status, 404)

    def test_restore_unknown_version(self):
        doc = self.w.new_doc()
        self.assertEqual(self.w.api.post_restore("ana", doc, 9).status, 404)


if __name__ == "__main__":
    unittest.main()
