SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL,
    owner_id TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_documents_updated ON documents (workspace_id, updated_at, id);
CREATE TABLE IF NOT EXISTS acl (
    doc_id TEXT NOT NULL REFERENCES documents(id),
    user_id TEXT NOT NULL,
    permission TEXT NOT NULL CHECK (permission IN ('view', 'edit')),
    PRIMARY KEY (doc_id, user_id)
);
CREATE TABLE IF NOT EXISTS share_links (
    token_hash TEXT PRIMARY KEY,
    doc_id TEXT NOT NULL REFERENCES documents(id),
    created_by TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    revoked_at TEXT
);
"""
