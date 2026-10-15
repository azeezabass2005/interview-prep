from typing import Optional

from ..db import Database
from ..models import Document


class DocumentRepository:
    def __init__(self, db: Database):
        self._db = db

    def create(self, title: str, owner: str) -> int:
        with self._db.transaction() as conn:
            return conn.execute("INSERT INTO documents (title, owner) VALUES (?, ?)", (title, owner)).lastrowid

    def get(self, doc_id: int) -> Optional[Document]:
        with self._db.transaction() as conn:
            r = conn.execute("SELECT * FROM documents WHERE doc_id = ?", (doc_id,)).fetchone()
        return Document(r["doc_id"], r["title"], r["owner"], bool(r["deleted"])) if r else None

    def delete(self, doc_id: int) -> None:
        with self._db.transaction() as conn:
            conn.execute("UPDATE documents SET deleted = 1 WHERE doc_id = ?", (doc_id,))
