FIXES = [
    ("shortlinks/repositories/links.py", "from datetime import datetime", "import sqlite3\nfrom datetime import datetime"),
    ("shortlinks/repositories/links.py",
     "    def save(self, link: Link) -> None:\n        with self._db.transaction() as conn:\n            conn.execute(\n"
     "                \"INSERT OR REPLACE INTO links",
     "    def insert(self, link: Link) -> bool:\n        \"\"\"False if the code is already taken.\"\"\"\n"
     "        try:\n            self._insert(link)\n            return True\n        except sqlite3.IntegrityError:\n"
     "            return False\n\n    def _insert(self, link: Link) -> None:\n        with self._db.transaction() as conn:\n            conn.execute(\n"
     "                \"INSERT INTO links"),
    ("shortlinks/repositories/links.py",
     "    def set_clicks(self, code: str, clicks: int) -> None:",
     "    def increment_clicks(self, code: str) -> None:\n        with self._db.transaction() as conn:\n"
     "            conn.execute(\"UPDATE links SET clicks = clicks + 1 WHERE code = ?\", (code,))\n\n"
     "    def set_clicks(self, code: str, clicks: int) -> None:"),
    ("shortlinks/services/analytics.py", "        self._links.set_clicks(link.code, link.clicks + 1)",
     "        self._links.increment_clicks(link.code)"),
    ("shortlinks/services/links.py", "from ..errors import AliasTaken, NotFound", "from ..errors import AliasTaken, Gone, LinkError, NotFound"),
    ("shortlinks/services/links.py",
     """        if alias is not None:
            code = validate_alias(alias)
            if self._links.get(code) is not None:
                raise AliasTaken(f"alias {alias} is taken")
        else:
            code = generate_code()
        link = Link(code, target_url, owner, now, expires_at, 0)
        self._links.save(link)
        return link""",
     """        if alias is not None:
            code = validate_alias(alias).lower()
            if self._links.lookup(code) is not None or not self._links.insert(
                    Link(code, target_url, owner, now, expires_at, 0)):
                raise AliasTaken(f"alias {alias} is taken")
            return self._links.get(code)
        for _ in range(5):
            link = Link(generate_code(), target_url, owner, now, expires_at, 0)
            if self._links.insert(link):
                return link
        raise LinkError("could not allocate a unique code")"""),
    ("shortlinks/services/links.py",
     "            raise NotFound(code)\n        self._clicks.record(link, referrer)",
     "            raise NotFound(code)\n        if link.is_expired(self._clock.now()):\n            raise Gone(code)\n"
     "        self._clicks.record(link, referrer)"),
]
