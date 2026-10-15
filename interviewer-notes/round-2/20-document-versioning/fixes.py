FIXES = [
    ("docstore/db.py", "CREATE INDEX IF NOT EXISTS idx_versions_doc ON versions (doc_id, version);",
     "CREATE UNIQUE INDEX IF NOT EXISTS idx_versions_doc ON versions (doc_id, version);"),
    ("docstore/repositories/versions.py", "from datetime import datetime", "import sqlite3\nfrom datetime import datetime"),
    ("docstore/repositories/versions.py",
     "    def insert(self, v: Version) -> None:\n        with self._db.transaction() as conn:",
     "    def insert_new(self, v: Version) -> bool:\n        \"\"\"False if that version number already exists.\"\"\"\n"
     "        try:\n            self.insert(v)\n            return True\n        except sqlite3.IntegrityError:\n            return False\n\n"
     "    def insert(self, v: Version) -> None:\n        with self._db.transaction() as conn:"),
    ("docstore/repositories/versions.py",
     "\"WHERE d.deleted = 0 AND v.content LIKE ? ORDER BY v.doc_id\"",
     "\"WHERE d.deleted = 0 AND v.content LIKE ? \"\n"
     "                \"AND v.version = (SELECT MAX(version) FROM versions x WHERE x.doc_id = v.doc_id) ORDER BY v.doc_id\""),
    ("docstore/services/editing.py", "from ..errors import DocError, NotFound", "from ..errors import DocError, NotFound, VersionConflict"),
    ("docstore/services/editing.py",
     """        reference = self._versions.first(doc_id)
        if reference.checksum == digest:
            return reference.version
        next_version = self._versions.max_version(doc_id) + 1
        self._versions.insert(Version(doc_id, next_version, content, digest, author, self._clock.now()))
        return next_version""",
     """        latest = self._versions.latest(doc_id)
        if latest.checksum == digest:
            return latest.version
        if base_version != latest.version:
            raise VersionConflict(f"document is at version {latest.version}, not {base_version}")
        next_version = base_version + 1
        if not self._versions.insert_new(Version(doc_id, next_version, content, digest, author, self._clock.now())):
            raise VersionConflict("someone else saved first")
        return next_version"""),
    ("docstore/services/editing.py", "        return self.save(doc_id, author, latest.content, latest.version)",
     "        return self.save(doc_id, author, target.content, latest.version)"),
]
