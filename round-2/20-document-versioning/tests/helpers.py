import os
import tempfile
from datetime import datetime

from docstore.api.handlers import DocsApi
from docstore.clock import FakeClock
from docstore.db import Database
from docstore.repositories.documents import DocumentRepository
from docstore.services.editing import EditingService
from docstore.services.search import SearchService


class World:
    def __init__(self):
        self._dir = tempfile.TemporaryDirectory()
        self.db = Database(os.path.join(self._dir.name, "docs.db"))
        self.db.initialize()
        self.clock = FakeClock(datetime(2026, 1, 20, 9, 0))
        self.api = DocsApi(EditingService(self.db, self.clock), SearchService(self.db))
        self.docs = DocumentRepository(self.db)

    def editing(self):
        return EditingService(self.db, self.clock)

    def new_doc(self, content="draft"):
        return self.api.post_document("ana", {"title": "IBM Q2 preview", "content": content}).body["doc_id"]

    def cleanup(self):
        self._dir.cleanup()
