from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Document:
    doc_id: int
    title: str
    owner: str
    deleted: bool


@dataclass(frozen=True)
class Version:
    doc_id: int
    version: int
    content: str
    checksum: str
    author: str
    created_at: datetime
