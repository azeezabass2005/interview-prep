from ..db import Database
from ..errors import DocError, NotFound
from ..models import Version
from ..repositories.documents import DocumentRepository
from ..repositories.versions import VersionRepository
from .checksums import checksum


class EditingService:
    def __init__(self, db: Database, clock):
        self._docs = DocumentRepository(db)
        self._versions = VersionRepository(db)
        self._clock = clock

    def _document(self, doc_id: int):
        doc = self._docs.get(doc_id)
        if doc is None or doc.deleted:
            raise NotFound(str(doc_id))
        return doc

    def create(self, owner: str, title: str, content: str) -> int:
        if not title.strip():
            raise DocError("title required")
        doc_id = self._docs.create(title.strip(), owner)
        self._versions.insert(Version(doc_id, 1, content, checksum(content), owner, self._clock.now()))
        return doc_id

    def save(self, doc_id: int, author: str, content: str, base_version: int) -> int:
        """Store a new version; returns the version number."""
        self._document(doc_id)
        digest = checksum(content)
        reference = self._versions.first(doc_id)
        if reference.checksum == digest:
            return reference.version
        next_version = self._versions.max_version(doc_id) + 1
        self._versions.insert(Version(doc_id, next_version, content, digest, author, self._clock.now()))
        return next_version

    def restore(self, doc_id: int, author: str, version: int) -> int:
        self._document(doc_id)
        target = self._versions.get(doc_id, version)
        if target is None:
            raise NotFound(f"{doc_id} v{version}")
        latest = self._versions.latest(doc_id)
        return self.save(doc_id, author, latest.content, latest.version)

    def latest(self, doc_id: int) -> Version:
        self._document(doc_id)
        return self._versions.latest(doc_id)

    def history(self, doc_id: int):
        self._document(doc_id)
        return self._versions.history(doc_id)
