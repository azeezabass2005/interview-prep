FIXES = [
    ("newsfeed/services/urls.py",
     "    host = parts.netloc\n    query = urlencode(sorted((k, v) for k, v in parse_qsl(parts.query) if not _is_tracking(k)))\n"
     "    return urlunsplit((parts.scheme, host, parts.path, query, \"\"))",
     "    host = parts.netloc.lower()\n    if host.startswith(\"www.\"):\n        host = host[4:]\n"
     "    path = parts.path.rstrip(\"/\") or \"/\"\n"
     "    query = urlencode(sorted((k, v) for k, v in parse_qsl(parts.query) if not _is_tracking(k)))\n"
     "    return urlunsplit((parts.scheme.lower(), host, path, query, \"\"))"),
    ("newsfeed/services/ranking.py", "total_seconds() / 86400", "total_seconds() / 3600"),
    ("newsfeed/repositories/stories.py",
     "[(cur.lastrowid, t) for t in tags])", "[(cur.lastrowid, t.lower()) for t in tags])"),
    ("newsfeed/repositories/stories.py", "WHERE t.tag = ? \"", "WHERE lower(t.tag) = lower(?) \""),
    ("newsfeed/repositories/stories.py",
     "    def since(self, since: datetime) -> List[Story]:",
     """    def older_than(self, published_at: str, story_id: int, limit: int) -> List[Story]:
        with self._db.transaction() as conn:
            rows = conn.execute(
                "SELECT * FROM stories WHERE published_at < ? OR (published_at = ? AND story_id < ?) "
                "ORDER BY published_at DESC, story_id DESC LIMIT ?",
                (published_at, published_at, story_id, limit)).fetchall()
            return self._hydrate(conn, rows)

    def since(self, since: datetime) -> List[Story]:"""),
    ("newsfeed/services/feed.py",
     """        offset = int(cursor) if cursor else 0
        stories = self._stories.newest(limit, offset)
        next_cursor = str(offset + len(stories)) if len(stories) == limit else None""",
     """        if cursor:
            published_at, story_id = cursor.rsplit("|", 1)
            stories = self._stories.older_than(published_at, int(story_id), limit)
        else:
            stories = self._stories.newest(limit)
        last = stories[-1] if stories else None
        next_cursor = f"{last.published_at.isoformat()}|{last.story_id}" if len(stories) == limit else None"""),
]
