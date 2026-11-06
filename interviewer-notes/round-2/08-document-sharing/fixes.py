FIXES = [
    ("vault/services/documents.py",
     '''        if link is None or link["revoked_at"] is not None:''',
     '''        if link is None or link["revoked_at"] is not None or parse_iso(link["expires_at"]) <= self._clock.now():'''),
    ("vault/repositories/documents.py",
     '''f"SELECT {COLUMNS} FROM documents d WHERE d.workspace_id = :ws AND d.title LIKE :q "''',
     '''f"SELECT {COLUMNS} FROM documents d WHERE d.workspace_id = :ws AND d.title LIKE :q AND {ACCESSIBLE} "'''),
    ("vault/services/documents.py",
     '''json.dumps({"updated_at": doc.updated_at})''', '''json.dumps({"updated_at": doc.updated_at, "id": doc.id})'''),
    ("vault/services/documents.py",
     '''def decode_cursor(cursor: str) -> str:
    try:
        return json.loads(base64.urlsafe_b64decode(cursor.encode()))["updated_at"]''',
     '''def decode_cursor(cursor: str) -> tuple[str, str]:
    try:
        data = json.loads(base64.urlsafe_b64decode(cursor.encode()))
        return data["updated_at"], data["id"]'''),
    ("vault/repositories/documents.py",
     '''            sql += " AND d.updated_at < :after"
            params["after"] = after''',
     '''            sql += " AND (d.updated_at < :after OR (d.updated_at = :after AND d.id < :after_id))"
            params["after"], params["after_id"] = after'''),
    ("vault/services/documents.py", '''        key = f"preview:{doc.id}"''', '''        key = f"preview:{doc.id}:{doc.version}"'''),
    ("vault/limits.py", "        if declared > max_bytes:", "        if declared > max_bytes or len(request.body) > max_bytes:"),
]
GROUPS = [[0], [1], [2, 3, 4], [5], [6]]
