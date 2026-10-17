from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Optional

LOCK_FOR = timedelta(minutes=30)
DEFAULT_MAX_VERSIONS = 20


class DocError(Exception):
    pass


class Conflict(DocError):
    pass


@dataclass
class Version:
    number: int
    author: str
    content: str


@dataclass
class Document:
    doc_id: str
    versions: Dict[int, Version] = field(default_factory=dict)
    latest: int = 0
    published: Optional[int] = None
    lock_holder: Optional[str] = None
    lock_until: Optional[datetime] = None


class DocStore:
    def __init__(self, clock, max_versions=DEFAULT_MAX_VERSIONS):
        self.clock = clock
        self.max_versions = max_versions
        self.docs = {}

    def _doc(self, doc_id):
        if doc_id not in self.docs:
            raise DocError("no such document")
        return self.docs[doc_id]

    def _add_version(self, doc, author, content):
        doc.latest += 1
        doc.versions[doc.latest] = Version(doc.latest, author, content)
        while len(doc.versions) > self.max_versions:
            del doc.versions[min(doc.versions)]
        return doc.versions[doc.latest]

    def create(self, doc_id, author, content):
        if doc_id in self.docs:
            raise DocError("document exists")
        doc = self.docs[doc_id] = Document(doc_id)
        return self._add_version(doc, author, content)

    def lock(self, doc_id, user):
        doc = self._doc(doc_id)
        now = self.clock.now()
        if doc.lock_holder not in (None, user) and doc.lock_until > now:
            raise DocError("locked by someone else")
        doc.lock_holder, doc.lock_until = user, now + LOCK_FOR

    def save(self, doc_id, author, content, base_version):
        doc = self._doc(doc_id)
        if doc.lock_holder not in (None, author):
            raise DocError(f"locked by {doc.lock_holder}")
        return self._add_version(doc, author, content)

    def restore(self, doc_id, author, number):
        doc = self._doc(doc_id)
        old = doc.versions.get(number)
        if old is None:
            raise DocError("no such version")
        doc.versions[doc.latest] = Version(doc.latest, author, old.content)
        return doc.versions[doc.latest]

    def publish(self, doc_id, number):
        doc = self._doc(doc_id)
        if number not in doc.versions:
            raise DocError("no such version")
        doc.published = number

    def read(self, doc_id):
        doc = self._doc(doc_id)
        return doc.versions[doc.latest].content
