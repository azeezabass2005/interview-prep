from ..models import Document

COLUMNS = "d.id, d.workspace_id, d.owner_id, d.title, d.content, d.version, d.created_at, d.updated_at"
# Documents a user may read: their own, or shared with them.
ACCESSIBLE = "(d.owner_id = :user OR EXISTS (SELECT 1 FROM acl a WHERE a.doc_id = d.id AND a.user_id = :user))"


def _doc(row) -> Document:
    return Document(row["id"], row["workspace_id"], row["owner_id"], row["title"], row["content"], row["version"],
                    row["created_at"], row["updated_at"])


class DocumentRepository:
    def __init__(self, db):
        self._db = db

    def add(self, d: Document) -> None:
        self._db.execute("INSERT INTO documents (id, workspace_id, owner_id, title, content, version, created_at, updated_at) "
                         "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                         (d.id, d.workspace_id, d.owner_id, d.title, d.content, d.version, d.created_at, d.updated_at))

    def get(self, doc_id: str) -> Document | None:
        row = self._db.query_one(f"SELECT {COLUMNS} FROM documents d WHERE d.id = ?", (doc_id,))
        return _doc(row) if row else None

    def update_content(self, doc_id: str, content: str, expected_version: int, at: str) -> bool:
        return self._db.execute("UPDATE documents SET content = ?, version = version + 1, updated_at = ? "
                                "WHERE id = ? AND version = ?", (content, at, doc_id, expected_version)) == 1

    def permission(self, doc_id: str, user_id: str) -> str | None:
        row = self._db.query_one("SELECT permission FROM acl WHERE doc_id = ? AND user_id = ?", (doc_id, user_id))
        return row["permission"] if row else None

    def share(self, doc_id: str, user_id: str, permission: str) -> None:
        self._db.execute("INSERT INTO acl (doc_id, user_id, permission) VALUES (?, ?, ?) "
                         "ON CONFLICT (doc_id, user_id) DO UPDATE SET permission = excluded.permission",
                         (doc_id, user_id, permission))

    def accessible_page(self, workspace_id: str, user_id: str, after: str | None, limit: int) -> list[Document]:
        """Newest first. `after` is the cursor from the previous page."""
        sql = f"SELECT {COLUMNS} FROM documents d WHERE d.workspace_id = :ws AND {ACCESSIBLE}"
        params = {"ws": workspace_id, "user": user_id, "limit": limit}
        if after:
            sql += " AND d.updated_at < :after"
            params["after"] = after
        rows = self._db.query(sql + " ORDER BY d.updated_at DESC, d.id DESC LIMIT :limit", params)
        return [_doc(r) for r in rows]

    def search(self, workspace_id: str, user_id: str, text: str, limit: int = 20) -> list[Document]:
        rows = self._db.query(
            f"SELECT {COLUMNS} FROM documents d WHERE d.workspace_id = :ws AND d.title LIKE :q "
            "ORDER BY d.updated_at DESC, d.id DESC LIMIT :limit",
            {"ws": workspace_id, "user": user_id, "q": f"%{text}%", "limit": limit},
        )
        return [_doc(r) for r in rows]


class LinkRepository:
    def __init__(self, db):
        self._db = db

    def add(self, token_hash: str, doc_id: str, created_by: str, expires_at: str) -> None:
        self._db.execute("INSERT INTO share_links (token_hash, doc_id, created_by, expires_at) VALUES (?, ?, ?, ?)",
                         (token_hash, doc_id, created_by, expires_at))

    def get(self, token_hash: str):
        return self._db.query_one("SELECT * FROM share_links WHERE token_hash = ?", (token_hash,))

    def revoke(self, token_hash: str, at: str) -> None:
        self._db.execute("UPDATE share_links SET revoked_at = ? WHERE token_hash = ?", (at, token_hash))

    def revoke_for_doc(self, doc_id: str, at: str) -> int:
        return self._db.execute("UPDATE share_links SET revoked_at = ? WHERE doc_id = ? AND revoked_at IS NULL", (at, doc_id))
